from django.contrib.auth import get_user_model
from django.test import TestCase  # noqa
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, RequestsClient

User = get_user_model()
client = RequestsClient()
response = client.get('http://localhost/homepage/')
assert response.status_code == 200
csrftoken = response.cookies['csrftoken']


class UsersManagersTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="jdoe", password="foo")
        self.assertEqual(user.username, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(username="")
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser("super", "foo")
        self.assertEqual(admin_user.username, "super")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="super", password="foo", is_superuser=False,
            )


class TestUserViewSet(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="john1",
            password="john1"
        )
        self.user2 = User.objects.create_user(
            username="john2",
            password="john2"
        )
        self.user3 = User.objects.create_user(
            username="jane1",
            password="jane1"
        )
        self.user4 = User.objects.create_user(
            username="jane2",
            password="jane2"
        )

    def test_get_list(self):
        pass

    def retrieve_user(self):
        pass

    def update_user(self):
        pass


class TestUserSettingViewSet(APITestCase):
    pass


class TestUserProfileViewSet(APITestCase):
    pass


class TestUserCertificationViewSet(APITestCase):
    pass


class TestUserEmployerViewSet(APITestCase):
    pass


class TestUserLicenseViewSet(APITestCase):
    pass


class TestUserSchoolViewSet(APITestCase):
    pass
