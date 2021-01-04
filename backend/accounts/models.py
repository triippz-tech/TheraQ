from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from model_utils import Choices
from rest_framework_simplejwt.tokens import RefreshToken


from .managers import UserManager
from core.exceptions import OneToOneRelationPresentException
from core.models import BaseAppModel, IndexedTimeStampedModel

AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}


DEGREE_TYPE = Choices(
    ("BACHELORS", "BACHELORS"),
    ("MASTERS", "MASTERS"),
    ("DOCTORATES", "DOCTORATES")
)


class UserSetting(BaseAppModel):

    class Meta:
        db_table = 'user_setting'
        verbose_name = "User Setting"

    def __str__(self):
        return self.user.get_short_name()


class UserProfile(BaseAppModel):
    headline = models.CharField(max_length=250, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=250, blank=True, null=True)
    nick_name = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.URLField(max_length=250, blank=True, null=True)
    linkedin = models.URLField(max_length=250, blank=True, null=True)
    twitter = models.URLField(max_length=250, blank=True, null=True)
    facebook = models.URLField(max_length=250, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'user_profile'
        verbose_name = "User Profile"

    def __str__(self):
        return self.user.get_short_name()


class User(AbstractBaseUser, PermissionsMixin, IndexedTimeStampedModel):
    username = models.CharField(max_length=255, unique=True, db_index=True, null=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(_('email address'), max_length=255, unique=True, db_index=True, null=False)
    image_url = models.URLField(max_length=256, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        default=False, help_text=_("Designates whether the user can log into this admin " "site.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "Designates whether this user should be treated as "
            "active. Unselect this instead of deleting accounts."
        ),
    )
    user_settings = models.OneToOneField(
        UserSetting,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="user")
    user_profile = models.OneToOneField(
        UserProfile,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="user")

    objects = UserManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['email']

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def create_default_settings(self):
        if self.user_settings:
            raise OneToOneRelationPresentException(
                "Can not create default settings for already existing relationship", None)
        new_user_settings = UserSetting()
        new_user_settings.save()
        self.user_settings = new_user_settings
        self.save()

    def create_default_profile(self):
        if self.user_profile:
            raise OneToOneRelationPresentException(
                "Can not create default settings for already existing relationship", None)
        profile = UserProfile()
        profile.save()
        self.user_profile = profile
        self.save()


class UserCertification(BaseAppModel):
    institution_name = models.CharField(max_length=250, null=False)
    certificate_program = models.CharField(max_length=250, null=False)
    certificate_number = models.CharField(max_length=250, blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    user: User = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        blank=True,
        null=False,
        related_name="user_certifications")

    class Meta:
        db_table = 'user_certification'
        verbose_name = "User Certification"

    def __str__(self):
        return f"{self.user.get_short_name()} : {self.certificate_program}"

    def archive(self):
        self.status = True
        self.save()


class UserEmployer(BaseAppModel):
    employer_name = models.CharField(max_length=200, null=False, blank=True)
    position = models.CharField(max_length=250, blank=True, null=False)
    current_position = models.BooleanField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    user: User = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="user_employers")

    class Meta:
        db_table = 'user_employer'
        verbose_name = "User Employer"

    def __str__(self):
        return f"{self.user.get_short_name()} : {self.employer_name}"

    def archive(self):
        self.status = True
        self.save()


class UserLicense(BaseAppModel):
    issuing_authority = models.CharField(max_length=250, blank=True)
    license_type = models.CharField(max_length=250, blank=True)
    license_number = models.CharField(max_length=250, blank=True)
    completion_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    user: User = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="user_licenses")

    class Meta:
        db_table = 'user_license'
        verbose_name = "User License"

    def __str__(self):
        return f"{self.user.get_short_name()} : {self.license_type}"

    def archive(self):
        self.status = True
        self.save()


class UserSchool(BaseAppModel):
    school_name = models.CharField(max_length=250, blank=True)
    program = models.CharField(max_length=250, blank=True, null=True)
    degree_type = models.CharField(choices=DEGREE_TYPE, blank=True, null=True, max_length=25)
    current_student = models.BooleanField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    graduate_date = models.DateField(blank=True, null=True)
    user: User = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        blank=True,
        null=True,
        related_name="user_schools")

    class Meta:
        db_table = 'user_school'
        verbose_name = "User School"

    def __str__(self):
        return f"{self.user.get_short_name()} : {self.school_name}"

    def archive(self):
        self.status = True
        self.save()


# add a signal to automatically create default
# user settings when a new user is created
@receiver(post_save, sender=User)
def create_default_settings(sender, instance, created=False, **kwargs):
    if created:
        instance.create_default_settings()


# add a signal to automatically create default
# user profile when a new user is created
@receiver(post_save, sender=User)
def create_default_profile(sender, instance, created=False, **kwargs):
    if created:
        instance.create_default_profile()
