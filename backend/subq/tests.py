import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from subq.models import SubQ, SubQFollower
from subq.serializers import CreateSubQFollowerSerializer, IdSubQSerializer
from accounts.serializers import IdUserSerializer

User = get_user_model()


# Create your tests here.
def create_user(**params):
    """ Helper function to create new user """
    return User.objects.create_user(**params)


def create_normal_client():
    test_user = User.objects.create_user(
        username="test_user",
        password="testing",
        email="tester@tester.com"
    )
    client = APIClient()
    client.force_authenticate(user=test_user)
    return test_user, client


def create_super_client():
    super_user = User.objects.create_superuser(
        username="super_user",
        password="super_user_pass",
        email="super_user@tester.com"
    )
    client = APIClient()
    client.force_authenticate(user=super_user)
    return super_user, client


def create_subq(**params):
    return SubQ.objects.create(**params)


def create_subq_follower(**params):
    return SubQFollower.objects.create(**params)


class TestSubQViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()
        self.user1 = create_user(username="user1", email="user1@user.com", password="user1pass")
        self.user2 = create_user(username="user2", email="user2@user.com", password="user2pass")
        self.user3 = create_user(username="user3", email="user3@user.com", password="user3pass")
        self.owner1 = create_user(username="owner1", email="owner1@user.com", password="owner1pass")
        self.owner2 = create_user(username="owner2", email="owner2@user.com", password="owner2pass")
        self.subq1 = create_subq(sub_name="sub1", description="SUB 1 Decsription", owner=self.owner1)
        self.subq2 = create_subq(sub_name="subq2", description="SUB 2 Decsription", owner=self.owner1)
        self.subq3 = create_subq(sub_name="subq3", description="SUB 3 Decsription", owner=self.test_user)
        self.subq4 = create_subq(sub_name="subq4", description="SUB 4 Decsription", owner=self.test_user)

    def test_create(self):
        payload = {
            "sub_name": "Therapy For Dummies",
            "description": "We talk about therapy, but for dummies",
        }
        res = self.normal_client.post("/api/subqs/subq/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["sub_name"], "Therapy For Dummies")
        self.assertEqual(res.data["description"], "We talk about therapy, but for dummies")
        self.assertIsNotNone(res.data["slug"])
        self.assertEqual(res.data.get("owner")["id"], self.test_user.pk)

    def test_update_by_id(self):
        new_subq = create_subq(sub_name="Pennsylvania State University",
                               description="Some Boring Stuff",
                               owner=self.test_user)
        payload = {
            "description": "Some different boring stuff",
        }
        res = self.normal_client.patch(f"/api/subqs/subq/{new_subq.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["sub_name"], "Pennsylvania State University")
        self.assertEqual(res.data["description"], "Some different boring stuff")
        self.assertEqual(res.data["slug"], new_subq.slug)

    def test_update_by_slug(self):
        new_subq = create_subq(sub_name="Pennsylvania State University",
                               description="Some Boring Stuff",
                               owner=self.test_user)
        payload = {
            "description": "Some different boring stuff",
        }
        res = self.normal_client.patch(f"/api/subqs/subq/{new_subq.slug}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["sub_name"], "Pennsylvania State University")
        self.assertEqual(res.data["description"], "Some different boring stuff")
        self.assertEqual(res.data["slug"], new_subq.slug)

    def test_list(self):
        res = self.normal_client.get("/api/subqs/subq/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(SubQ.objects.all().count(), len(res.data["results"]))

    def test_list_filter(self):
        res = self.normal_client.get(f"/api/subqs/subq/?owner__email={self.test_user.email}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(SubQ.objects.filter(owner__email=self.test_user.email).count(),
                         len(res.data["results"]))

        res = self.normal_client.get(f"/api/subqs/subq/?sub_name={self.subq1.sub_name}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(SubQ.objects.filter(sub_name=self.subq1.sub_name).count(),
                         len(res.data["results"]))

        res = self.normal_client.get(f"/api/subqs/subq/?slug={self.subq2.slug}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(SubQ.objects.filter(slug=self.subq2.slug).count(),
                         len(res.data["results"]))

    def test_retrieve_by_pk(self):
        res = self.normal_client.get(f"/api/subqs/subq/{self.subq3.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.subq3.id, res.data["id"])

    def test_retrieve_by_slug(self):
        res = self.normal_client.get(f"/api/subqs/subq/{self.subq3.slug}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.subq3.slug, res.data["slug"])

    def test_delete(self):
        res = self.normal_client.delete(f"/api/subqs/subq/{self.subq1.pk}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.normal_client.delete(f"/api/subqs/subq/{self.subq4.slug}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        subq_refreshed = SubQ.objects.get(pk=self.subq4.pk)
        self.assertTrue(subq_refreshed.status)

    def test_add_moderator(self):
        follower = create_subq_follower(follower=self.user1, subq=self.subq3)
        serializer = IdUserSerializer(self.user1)
        res = self.normal_client.post(f"/api/subqs/subq/{self.subq3.pk}/add_moderator/", serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        refreshed_follower = SubQFollower.objects.get(pk=follower.pk)
        self.assertTrue(refreshed_follower.is_moderator)

    def test_remove_moderator(self):
        follower = create_subq_follower(follower=self.user1, subq=self.subq3, is_moderator=True)
        serializer = IdUserSerializer(self.user1)
        res = self.normal_client.post(f"/api/subqs/subq/{self.subq3.pk}/remove_moderator/", serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        refreshed_follower = SubQFollower.objects.get(pk=follower.pk)
        self.assertFalse(refreshed_follower.is_moderator)

    def test_ban(self):
        follower = create_subq_follower(follower=self.user1, subq=self.subq3)
        serializer = IdUserSerializer(self.user1)
        res = self.normal_client.post(f"/api/subqs/subq/{self.subq3.pk}/ban/", serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        refreshed_follower = SubQFollower.objects.get(pk=follower.pk)
        self.assertTrue(refreshed_follower.is_banned)
        self.assertTrue(refreshed_follower.status)
        self.assertIsNotNone(refreshed_follower.ban_date)

    def test_leave(self):
        follower = create_subq_follower(follower=self.test_user, subq=self.subq1)
        res = self.normal_client.post(f"/api/subqs/subq/{self.subq1.pk}/leave/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        refreshed_follower = SubQFollower.objects.get(pk=follower.pk)
        self.assertTrue(refreshed_follower.status)

    def test_join(self):
        res = self.normal_client.post(f"/api/subqs/subq/{self.subq2.pk}/join/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        refreshed_follower = SubQFollower.objects.get(follower=self.test_user, subq=self.subq2)
        self.assertFalse(refreshed_follower.status)
        self.assertFalse(refreshed_follower.is_moderator)
        self.assertTrue(refreshed_follower.notifications_enabled)


class TestSubQFollowerViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()
        self.user1 = create_user(username="user1", email="user1@user.com", password="user1pass")
        self.user2 = create_user(username="user2", email="user2@user.com", password="user2pass")
        self.user3 = create_user(username="user3", email="user3@user.com", password="user3pass")
        self.subq1 = create_subq(sub_name="sub1", description="SUB 1 Decsription", owner=self.test_user)
        self.subq4 = create_subq(sub_name="subq4", description="SUB 4 Decsription", owner=self.user3)
        self.follower_test = create_subq_follower(subq=self.subq4, follower=self.test_user)
        self.follower1 = create_subq_follower(subq=self.subq1, follower=self.user1)
        self.follower2 = create_subq_follower(subq=self.subq1, follower=self.user2)

    def test_create(self):
        res = self.normal_client.post("/api/subqs/subqfollower/", json.dumps({
            "subq": {
                "id": self.subq4.pk,
            },
        }),  content_type='application/json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data.get("subq")["id"], self.subq4.pk)
        self.assertEqual(res.data.get("follower")["id"], self.test_user.pk)

    def test_update(self):
        payload = {
            "notifications_enabled": False,
        }
        res = self.normal_client.patch(f"/api/subqs/subqfollower/{self.follower_test.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["notifications_enabled"])

    def test_list(self):
        res = self.normal_client.get("/api/subqs/subqfollower/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(SubQFollower.objects.all().count(), len(res.data["results"]))

    def test_list_filter(self):
        res = self.normal_client.get(f"/api/subqs/subqfollower/?follower__email={self.user1.email}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(SubQFollower.objects.filter(follower__email=self.user1.email).count(),
                         len(res.data["results"]))

        res = self.normal_client.get(f"/api/subqs/subqfollower/?subq__sub_name={self.subq1.sub_name}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(SubQFollower.objects.filter(subq__sub_name=self.subq1.sub_name).count(),
                         len(res.data["results"]))

        res = self.normal_client.get(f"/api/subqs/subqfollower/?is_banned=False")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(SubQFollower.objects.filter(is_banned=False).count(),
                         len(res.data["results"]))

    def test_retrieve(self):
        res = self.normal_client.get(f"/api/subqs/subqfollower/{self.follower1.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.follower1.id, res.data["id"])

    def test_delete(self):
        res = self.normal_client.delete(f"/api/subqs/subqfollower/{self.follower1.pk}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.normal_client.delete(f"/api/subqs/subqfollower/{self.follower_test.pk}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        subqf_refreshed = SubQFollower.objects.get(pk=self.follower_test.pk)
        self.assertTrue(subqf_refreshed.status)
