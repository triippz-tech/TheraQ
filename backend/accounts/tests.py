from django.contrib.auth import get_user_model
from django.test import TestCase  # noqa
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from accounts.models import UserCertification, UserEmployer, UserLicense, UserSchool

User = get_user_model()


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


class UsersManagersTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@test.com",
            username="mytester",
            password="testing",
            first_name="test",
            last_name="tester"
        )
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.username, "mytester")
        self.assertIsNotNone(user.password)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        super_user = User.objects.create_superuser(
            email="super@super.com",
            username="superduper",
            password="testing",
            first_name="super",
            last_name="user"
        )
        self.assertEqual(super_user.email, "super@super.com")
        self.assertEqual(super_user.username, "superduper")
        self.assertIsNotNone(super_user.password)
        self.assertTrue(super_user.is_active)
        self.assertTrue(super_user.is_superuser)
        self.assertTrue(super_user.is_staff)


class TestUserSignals(TestCase):
    def setUp(self):
        self.created_user = create_user(username="myuser", email="myuser@user.com", password="myuserpass")

    def tearDown(self):
        self.created_user.delete()

    def test_settings_created(self):
        self.assertIsNotNone(self.created_user.user_settings)

    def test_profile_created(self):
        self.assertIsNotNone(self.created_user.user_profile)


class TestUserViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()
        self.user1 = create_user(username="user1", email="user1@tt.com", password="user1_pass")
        self.user2 = create_user(username="user2", email="user2@tt.com", password="user2_pass")

    def test_get_list(self):
        res = self.normal_client.get("/api/users/user/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.all().count(), len(res.data["results"]))

    def test_retrieve_user_by_id(self):
        res = self.normal_client.get(f"/api/users/user/{self.user1.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.id, res.data["id"])

    def test_retrieve_user_by_slug(self):
        res = self.normal_client.get(f"/api/users/user/{self.user2.username}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user2.id, res.data["id"])

    def test_update_user_not_permitted(self):
        payload = {"first_name": "Peter", "last_name": "Pan"}
        res = self.normal_client.patch(f"/api/users/user/{self.user1.pk}/", payload)
        self.assertNotEqual(res.status_code, status.HTTP_200_OK)

    def test_update_user_permitted(self):
        payload = {"first_name": "Peter", "last_name": "Pan"}
        res = self.normal_client.patch(f"/api/users/user/{self.test_user.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual("Peter", res.data["first_name"])
        self.assertEqual("Pan", res.data["last_name"])

    def test_update_user_superuser_permitted(self):
        payload = {"first_name": "Peter", "last_name": "Pan"}
        res = self.super_client.patch(f"/api/users/user/{self.user2.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual("Peter", res.data["first_name"])
        self.assertEqual("Pan", res.data["last_name"])


class TestUserSettingViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()
        self.user1 = create_user(username="user1", email="user1@tt.com", password="user1_pass")
        self.user2 = create_user(username="user2", email="user2@tt.com", password="user2_pass")

    def test_retrieve_by_slug_authenticated(self):
        res = self.normal_client.get(f"/api/users/settings/{self.test_user.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_user.id, res.data["id"])

    def test_retrieve_by_id_authenticated(self):
        res = self.normal_client.get(f"/api/users/settings/{self.test_user.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_user.id, res.data["id"])

    def test_retrieve_by_slug_not_authenticated(self):
        res = self.normal_client.get(f"/api/users/settings/{self.user1.pk}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_by_id_not_authenticated(self):
        res = self.normal_client.get(f"/api/users/settings/{self.user1.pk}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update(self):
        pass


class TestUserProfileViewSet(APITestCase):

    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()
        self.user1 = create_user(username="user1", email="user1@tt.com", password="user1_pass")
        self.user2 = create_user(username="user2", email="user2@tt.com", password="user2_pass")

    def test_retrieve_by_slug(self):
        res = self.normal_client.get(f"/api/users/profile/{self.test_user.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_user.id, res.data["id"])

    def test_retrieve_by_id(self):
        res = self.normal_client.get(f"/api/users/profile/{self.test_user.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.test_user.id, res.data["id"])

    def test_update_unathenticated(self):
        payload = {
            "headline": "THIS IS A TEST",
            "bio": "I am a pretty boring person",
            "location": "Lancaster, PA",
            "nick_name": "Trip",
            "profile_picture": "http://testing.com"
        }
        res = self.normal_client.patch(f"/api/users/profile/{self.user1.pk}/", payload)
        self.assertNotEqual(res.status_code, status.HTTP_200_OK)

    def test_update_superuser(self):
        payload = {
            "headline": "THIS IS A TEST",
            "bio": "I am a pretty boring person",
            "location": "Lancaster, PA",
            "nick_name": "Trip",
            "profile_picture": "http://testing.com"
        }
        res = self.super_client.patch(f"/api/users/profile/{self.user1.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_authenticated(self):
        payload = {
            "headline": "THIS IS A TEST",
            "bio": "I am a pretty boring person",
            "location": "Lancaster, PA",
            "nick_name": "Trip",
            "profile_picture": "http://testing.com"
        }
        res = self.normal_client.patch(f"/api/users/profile/{self.test_user.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["headline"], "THIS IS A TEST")
        self.assertEqual(res.data["bio"], "I am a pretty boring person")
        self.assertEqual(res.data["location"], "Lancaster, PA")
        self.assertEqual(res.data["nick_name"], "Trip")
        self.assertEqual(res.data["profile_picture"], "http://testing.com")


class TestUserCertificationViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()
        self.user1 = create_user(username="user1", email="user1@tt.com", password="user1_pass")

    def test_create(self):
        payload = {
            "institution_name": "Penn State",
            "certificate_program": "Rehab 101",
            "certificate_number": "ABCD1234",
            "completion_date": "2020-10-10"
        }
        res = self.normal_client.post("/api/users/certifications/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["institution_name"], "Penn State")
        self.assertEqual(res.data["certificate_program"], "Rehab 101")
        self.assertEqual(res.data["certificate_number"], "ABCD1234")
        self.assertEqual(res.data["completion_date"], "2020-10-10")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)

    def test_update(self):
        new_cert = UserCertification.objects.create(institution_name="Nope University",
                                                    certificate_program="Noping 101",
                                                    user=self.test_user)
        payload = {
            "certificate_number": "123ABC",
            "completion_date": "2020-10-10"
        }
        res = self.normal_client.patch(f"/api/users/certifications/{new_cert.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["certificate_number"], "123ABC")
        self.assertEqual(res.data["completion_date"], "2020-10-10")

    def test_list(self):
        res = self.normal_client.get("/api/users/certifications/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserCertification.objects.all().count(), len(res.data["results"]))

    def test_list_filter(self):
        certification = UserCertification.objects.create(user=self.test_user,
                                                         institution_name="Penn_State",
                                                         certificate_program="Rehab 101",
                                                         certificate_number="ABCD1234")
        res = self.normal_client.get(f"/api/users/certifications/?user__username={self.test_user.username}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserCertification.objects.filter(user__username=self.test_user.username).count(),
                         len(res.data["results"]))
        res = self.normal_client.get(f"/api/users/certifications/?institution_name={certification.institution_name}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserCertification.objects.filter(institution_name=certification.institution_name).count(),
                         len(res.data["results"]))

    def test_retrieve(self):
        new_cert = UserCertification.objects.create(institution_name="Nope University",
                                                    certificate_program="Noping 101",
                                                    user=self.test_user)
        res = self.normal_client.get(f"/api/users/certifications/{new_cert.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(new_cert.id, res.data["id"])

    def test_delete(self):
        new_cert = UserCertification.objects.create(institution_name="Nope University",
                                                    certificate_program="Noping 101",
                                                    user=self.test_user)
        res = self.normal_client.delete(f"/api/users/certifications/{new_cert.pk}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        refreshed_cert = UserCertification.objects.get(pk=new_cert.pk)
        self.assertTrue(refreshed_cert.status)


class TestUserEmployerViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()

    def test_create(self):
        payload = {
            "employer_name": "Penn Medicine",
            "position": "Rehab Therapist",
            "current_position": True,
            "description": "We Do Werk",
            "start_date": "2020-10-10",
            "end_date": "2020-12-31",
        }
        res = self.normal_client.post("/api/users/employers/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["employer_name"], "Penn Medicine")
        self.assertEqual(res.data["position"], "Rehab Therapist")
        self.assertTrue(res.data["current_position"])
        self.assertEqual(res.data["description"], "We Do Werk")
        self.assertEqual(res.data["start_date"], "2020-10-10")
        self.assertEqual(res.data["end_date"], "2020-12-31")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)

    def test_update(self):
        new_cert = UserEmployer.objects.create(employer_name="Nope University",
                                               position="OT",
                                               user=self.test_user)
        payload = {
            "current_position": False,
            "start_date": "2020-10-10"
        }
        res = self.normal_client.patch(f"/api/users/employers/{new_cert.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["current_position"])
        self.assertEqual(res.data["start_date"], "2020-10-10")

    def test_list(self):
        new_cert = UserEmployer.objects.create(employer_name="Nope University",
                                               position="OT",
                                               user=self.test_user)
        res = self.normal_client.get("/api/users/employers/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserEmployer.objects.all().count(), len(res.data["results"]))

    def test_list_filter(self):
        employer1 = UserEmployer.objects.create(user=self.test_user,
                                                employer_name="Penn Medicine",
                                                position="Rehab Therapist",
                                                current_position=True,
                                                description="We Do Werk",
                                                start_date="2020-10-10",
                                                end_date="2020-12-31")
        employer2 = UserEmployer.objects.create(user=self.test_user,
                                                employer_name="Ok Johnny",
                                                position="Rehab_Therapist",
                                                current_position=True,
                                                description="We Do Werk",
                                                start_date="2020-10-10",
                                                end_date="2020-12-31")
        res = self.normal_client.get(f"/api/users/employers/?user__email={self.test_user.email}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserEmployer.objects.filter(user__email=self.test_user.email).count(),
                         len(res.data["results"]))
        res = self.normal_client.get(f"/api/users/employers/?employer_name={employer1.employer_name}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserEmployer.objects.filter(employer_name=employer1.employer_name).count(),
                         len(res.data["results"]))
        res = self.normal_client.get(f"/api/users/employers/?position={employer2.position}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserEmployer.objects.filter(position=employer2.position).count(),
                         len(res.data["results"]))

    def test_retrieve(self):
        employer2 = UserEmployer.objects.create(user=self.test_user,
                                                employer_name="Ok Johnny",
                                                position="Rehab_Therapist",
                                                current_position=True,
                                                description="We Do Werk",
                                                start_date="2020-10-10",
                                                end_date="2020-12-31")
        res = self.normal_client.get(f"/api/users/employers/{employer2.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(employer2.id, res.data["id"])

    def test_delete(self):
        employer2 = UserEmployer.objects.create(user=self.test_user,
                                                employer_name="Ok Johnny",
                                                position="Rehab_Therapist",
                                                current_position=True,
                                                description="We Do Werk",
                                                start_date="2020-10-10",
                                                end_date="2020-12-31")
        res = self.normal_client.delete(f"/api/users/employers/{employer2.pk}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        employer_refreshed = UserEmployer.objects.get(pk=employer2.pk)
        self.assertTrue(employer_refreshed.status)


class TestUserLicenseViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()

    def test_create(self):
        payload = {
            "issuing_authority": "Pennsylvania",
            "license_type": "OTR",
            "license_number": "ABCD1234",
            "completion_date": "2020-10-10",
            "expiration_date": "2020-12-31",
        }
        res = self.normal_client.post("/api/users/licenses/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["issuing_authority"], "Pennsylvania")
        self.assertEqual(res.data["license_type"], "OTR")
        self.assertEqual(res.data["license_number"], "ABCD1234")
        self.assertEqual(res.data["completion_date"], "2020-10-10")
        self.assertEqual(res.data["expiration_date"], "2020-12-31")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)

    def test_update(self):
        new_license = UserLicense.objects.create(issuing_authority="Pennsylvania",
                                                 license_type="OTR",
                                                 license_number="ABCD1234",
                                                 user=self.test_user)
        payload = {
            "expiration_date": "2020-10-10",
            "completion_date": "2022-10-10"
        }
        res = self.normal_client.patch(f"/api/users/licenses/{new_license.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["expiration_date"], "2020-10-10")
        self.assertEqual(res.data["completion_date"], "2022-10-10")

    def test_list(self):
        UserLicense.objects.create(issuing_authority="Pennsylvania",
                                   license_type="OTR",
                                   license_number="ABCD1234",
                                   user=self.test_user)
        res = self.normal_client.get("/api/users/licenses/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLicense.objects.all().count(), len(res.data["results"]))

    def test_list_filter(self):
        new_license = UserLicense.objects.create(issuing_authority="Pennsylvania",
                                                 license_type="OTR",
                                                 license_number="ABCD1234",
                                                 expiration_date="2020-10-10",
                                                 completion_date="2022-10-10",
                                                 user=self.test_user)
        new_license2 = UserLicense.objects.create(issuing_authority="Pennsylvania",
                                                  license_type="OTR",
                                                  license_number="ZYX987",
                                                  expiration_date="2020-10-10",
                                                  completion_date="2022-10-10",
                                                  user=self.test_user)
        res = self.normal_client.get(f"/api/users/licenses/?user__email={self.test_user.email}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLicense.objects.filter(user__email=self.test_user.email).count(),
                         len(res.data["results"]))
        res = self.normal_client.get(f"/api/users/licenses/?issuing_authority={new_license.issuing_authority}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLicense.objects.filter(issuing_authority=new_license.issuing_authority).count(),
                         len(res.data["results"]))
        res = self.normal_client.get(f"/api/users/licenses/?license_number={new_license2.license_number}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserLicense.objects.filter(license_number=new_license2.license_number).count(),
                         len(res.data["results"]))

    def test_retrieve(self):
        new_license = UserLicense.objects.create(issuing_authority="Pennsylvania",
                                                 license_type="OTR",
                                                 license_number="ABCD1234",
                                                 expiration_date="2020-10-10",
                                                 completion_date="2022-10-10",
                                                 user=self.test_user)
        res = self.normal_client.get(f"/api/users/licenses/{new_license.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(new_license.id, res.data["id"])

    def test_delete(self):
        new_license = UserLicense.objects.create(issuing_authority="Pennsylvania",
                                                 license_type="OTR",
                                                 license_number="ABCD1234",
                                                 expiration_date="2020-10-10",
                                                 completion_date="2022-10-10",
                                                 user=self.test_user)
        res = self.normal_client.delete(f"/api/users/licenses/{new_license.pk}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        license_refreshed = UserLicense.objects.get(pk=new_license.pk)
        self.assertTrue(license_refreshed.status)


class TestUserSchoolViewSet(APITestCase):
    def setUp(self):
        self.test_user, self.normal_client = create_normal_client()
        self.super_user, self.super_client = create_super_client()

    def test_create(self):
        payload = {
            "school_name": "Pennsylvania State University",
            "program": "Masters of Science: Occupational Therapy",
            "degree_type": "MASTERS",
            "current_student": False,
            "start_date": "2020-10-10",
            "graduate_date": "2023-12-31",
        }
        res = self.normal_client.post("/api/users/schools/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["school_name"], "Pennsylvania State University")
        self.assertEqual(res.data["program"], "Masters of Science: Occupational Therapy")
        self.assertEqual(res.data["degree_type"], "MASTERS")
        self.assertFalse(res.data["current_student"])
        self.assertEqual(res.data["start_date"], "2020-10-10")
        self.assertEqual(res.data["graduate_date"], "2023-12-31")
        self.assertEqual(res.data.get("user")["id"], self.test_user.pk)

    def test_update(self):
        new_school = UserSchool.objects.create(school_name="Pennsylvania State University",
                                               program="PT",
                                               degree_type="BACHELORS",
                                               user=self.test_user)
        payload = {
            "current_student": True,
            "start_date": "2020-10-10",
            "graduate_date": "2022-10-10"
        }
        res = self.normal_client.patch(f"/api/users/schools/{new_school.pk}/", payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["current_student"])
        self.assertEqual(res.data["start_date"], "2020-10-10")
        self.assertEqual(res.data["graduate_date"], "2022-10-10")

    def test_list(self):
        UserSchool.objects.create(school_name="Pennsylvania State University",
                                  program="PT",
                                  degree_type="BACHELORS",
                                  user=self.test_user)
        res = self.normal_client.get("/api/users/schools/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserSchool.objects.all().count(), len(res.data["results"]))

    def test_list_filter(self):
        new_school = UserSchool.objects.create(school_name="Pennsylvania State University",
                                               program="OT",
                                               degree_type="MASTERS",
                                               start_date="2020-10-10",
                                               graduate_date="2022-10-10",
                                               user=self.test_user)
        new_schools2 = UserSchool.objects.create(school_name="Pennsylvania State University",
                                                 program="PT",
                                                 degree_type="MASTERS",
                                                 start_date="2020-10-10",
                                                 graduate_date="2022-10-10",
                                                 user=self.test_user)
        res = self.normal_client.get(f"/api/users/schools/?user__email={self.test_user.email}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserSchool.objects.filter(user__email=self.test_user.email).count(),
                         len(res.data["results"]))

        res = self.normal_client.get(f"/api/users/schools/?program={new_school.program}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserSchool.objects.filter(program=new_school.program).count(),
                         len(res.data["results"]))

        res = self.normal_client.get(f"/api/users/schools/?degree_type={new_schools2.degree_type}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(UserSchool.objects.filter(degree_type=new_schools2.degree_type).count(),
                         len(res.data["results"]))

    def test_retrieve(self):
        new_school = UserSchool.objects.create(school_name="Pennsylvania State University",
                                               program="OT",
                                               degree_type="MASTERS",
                                               start_date="2020-10-10",
                                               graduate_date="2022-10-10",
                                               user=self.test_user)
        res = self.normal_client.get(f"/api/users/schools/{new_school.pk}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(new_school.id, res.data["id"])

    def test_delete(self):
        new_school = UserSchool.objects.create(school_name="Pennsylvania State University",
                                               program="OT",
                                               degree_type="MASTERS",
                                               start_date="2020-10-10",
                                               graduate_date="2022-10-10",
                                               user=self.test_user)
        res = self.normal_client.delete(f"/api/users/schools/{new_school.pk}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        school_refreshed = UserSchool.objects.get(pk=new_school.pk)
        self.assertTrue(school_refreshed.status)
