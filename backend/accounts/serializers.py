from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import get_username_max_length, email_address_exists
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.models import UserSetting, UserProfile, UserCertification, UserEmployer, UserLicense, UserSchool, \
    DEGREE_TYPE
from core.serializers import DynamicFieldsModelSerializer, ChoicesField

User = get_user_model()


class IdUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    username = serializers.CharField(required=False, allow_null=True)


class UpdateUserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ('id', 'status', 'created_date', 'updated_date')
        read_only_fields = ('id', 'created_date', 'updated_date', 'status')


class ViewUserSettingSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = UserSetting
        fields = '__all__'
        read_only_fields = ('id', 'created_date', 'updated_date', 'status')


class ViewUserProfileSerialzer(DynamicFieldsModelSerializer):
    headline = serializers.CharField(required=False, max_length=250, allow_null=True, allow_blank=True)
    bio = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    location = serializers.CharField(required=False, max_length=250, allow_null=True, allow_blank=True)
    nick_name = serializers.CharField(required=False, max_length=250, allow_null=True, allow_blank=True)
    profile_picture = serializers.URLField(required=False, max_length=250, allow_null=True, allow_blank=True)
    linkedin = serializers.CharField(required=False, max_length=250, allow_null=True, allow_blank=True)
    twitter = serializers.CharField(required=False, max_length=250, allow_null=True, allow_blank=True)
    facebook = serializers.CharField(required=False, max_length=250, allow_null=True, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            "headline",
            "bio",
            "location",
            "nick_name",
            "profile_picture",
            "linkedin",
            "twitter",
            "facebook",
            "birth_date"
        )
        read_only_fields = (
            'id', 'created_date', 'updated_date', 'status'
        )
        optional_fields = (
            "headline",
            "bio",
            "location",
            "nick_name",
            "profile_picture",
            "linkedin",
            "twitter",
            "facebook",
            "birth_date"
        )


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = (
            'id', 'created_date', 'updated_date', 'status'
        )


class UpdateUserCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCertification
        fields = '__all__'
        read_only_fields = (
            'id', 'created_date', 'updated_date', 'status'
        )


class CreateUserCertificationSerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=False)
    completion_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserCertification
        fields = (
            "user",
            'institution_name',
            'certificate_program',
            'certificate_number',
            'completion_date'
        )
        read_only_fields = ('status', 'created_date', 'updated_date')
        optional_fields = (
            "user",
            'certificate_number',
            'completion_date',
        )


class ViewUserCertificationSerializer(DynamicFieldsModelSerializer):
    user = IdUserSerializer(required=False, allow_null=True, many=False)
    institution_name = serializers.CharField(required=False, max_length=250, allow_null=False, allow_blank=True)
    certificate_program = serializers.CharField(required=False, max_length=250, allow_null=False, allow_blank=True)
    certificate_number = serializers.CharField(required=False, max_length=250, allow_null=True, allow_blank=True)
    completion_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserCertification
        fields = '__all__'
        read_only_fields = ('id', 'status', 'created_date', 'updated_date')
        optional_fields = (
            'institution_name',
            'certificate_program',
            'certificate_number',
            'completion_date',
            'user'
        )


class CreateUserEmployerSerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(required=True, max_length=200, allow_null=False)
    position = serializers.CharField(required=True, max_length=250, allow_null=False)
    current_position = serializers.BooleanField(required=False, allow_null=True, default=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user = IdUserSerializer(required=False, allow_null=True, many=False)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserEmployer
        fields = (
            'id',
            'employer_name',
            'position',
            'current_position',
            'description',
            'start_date',
            'end_date',
            'user'
        )
        read_only_fields = ('id', 'status', 'created_date', 'updated_date')
        optional_fields = (
            'current_position',
            'description',
            'start_date',
            'end_date'
        )


class UpdateUserEmployerSerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=False, allow_null=True, many=False)

    class Meta:
        model = UserEmployer
        fields = (
            'id',
            'employer_name',
            'position',
            'current_position',
            'description',
            'start_date',
            'end_date',
            'user'
        )
        read_only_fields = (
            'id', 'created_date', 'updated_date', 'status'
        )


class ViewUserEmployerSerializer(DynamicFieldsModelSerializer):
    employer_name = serializers.CharField(required=False, max_length=200, allow_null=False)
    position = serializers.CharField(required=False, max_length=250, allow_null=False)
    current_position = serializers.BooleanField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user = IdUserSerializer(required=False, allow_null=True, many=False)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserEmployer
        fields = (
            'id',
            'employer_name',
            'position',
            'current_position',
            'description',
            'start_date',
            'end_date',
            'user'
        )
        read_only_fields = ('id', 'status', 'created_date', 'updated_date', 'user')
        optional_fields = (
            'employer_name',
            'position',
            'current_position',
            'description',
            'start_date',
            'end_date'
        )


class CreateUserLicenseSerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=False, allow_null=True, many=False)
    completion_date = serializers.DateField(required=False, allow_null=True)
    expiration_date = serializers.DateField(required=False, allow_null=True)
    issuing_authority = serializers.CharField(required=True, max_length=250)
    license_type = serializers.CharField(required=True, max_length=250)
    license_number = serializers.CharField(required=True, max_length=250)

    class Meta:
        model = UserLicense
        fields = (
            'id',
            'issuing_authority',
            'license_type',
            'license_number',
            'completion_date',
            'expiration_date',
            'user'
        )
        read_only_fields = ('id', 'status', 'created_date', 'updated_date', 'user')
        optional_fields = (
            'issuing_authority',
            'license_type',
            'license_number',
            'completion_date',
            'expiration_date',
        )


class UpdateUserLicenseSerializer(serializers.ModelSerializer):
    completion_date = serializers.DateField(required=False, allow_null=True)
    expiration_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserLicense
        fields = '__all__'
        read_only_fields = (
            'id', 'created_date', 'updated_date', 'status'
        )


class ViewUserLicenseSerializer(DynamicFieldsModelSerializer):
    user = IdUserSerializer(required=False, allow_null=False, many=False)
    issuing_authority = serializers.CharField(required=False, max_length=250, allow_null=False, allow_blank=True)
    license_type = serializers.CharField(required=False, max_length=250, allow_null=False, allow_blank=True)
    license_number = serializers.CharField(required=False, max_length=250, allow_null=False, allow_blank=True)
    completion_date = serializers.DateField(required=False, allow_null=True)
    expiration_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserLicense
        fields = (
            'id',
            'issuing_authority',
            'license_type',
            'license_number',
            'completion_date',
            'expiration_date',
            'user'
        )
        read_only_fields = ('id', 'status', 'created_date', 'updated_date', 'user')
        optional_fields = (
            'issuing_authority',
            'license_type',
            'license_number',
            'completion_date',
            'expiration_date',
        )


class CreateUserSchoolSerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=False, allow_null=True, many=False)
    school_name = serializers.CharField(max_length=250, required=True, allow_null=False, error_messages={
        "required": "Must provide a school name"
    })
    program = serializers.CharField(max_length=250, required=True, allow_null=False, error_messages={
        "required": "Must provide a degree program"
    })
    degree_type = ChoicesField(DEGREE_TYPE, required=True, allow_null=False, error_messages={
        "required": "Must select a degree type"
    })
    current_student = serializers.BooleanField(required=False, default=True, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    graduate_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserSchool
        fields = (
            "id",
            'school_name',
            'program',
            'degree_type',
            'current_student',
            'start_date',
            'graduate_date',
            "user"
        )
        read_only_fields = ("id", 'status', 'created_date', 'updated_date', "user")
        optional_fields = (
            'current_student',
            'start_date',
            'graduate_date'
        )


class UpdateUserSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSchool
        fields = '__all__'
        read_only_fields = (
            'id', 'created_date', 'updated_date', 'status'
        )


class ViewUserSchoolSerializer(DynamicFieldsModelSerializer):
    user = IdUserSerializer(required=False, allow_null=True, many=False)
    school_name = serializers.CharField(max_length=250, required=False, allow_blank=True, allow_null=False)
    program = serializers.CharField(max_length=250, required=False, allow_blank=True, allow_null=False)
    degree_type = ChoicesField(DEGREE_TYPE, required=False, allow_null=False)
    current_student = serializers.BooleanField(required=False, default=True, allow_null=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    graduate_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = UserSchool
        fields = (
            'id',
            'school_name',
            'program',
            'degree_type',
            'current_student',
            'start_date',
            'graduate_date',
            'user'
        )
        read_only_fields = ('id', 'status', 'created_date', 'updated_date', 'user')
        optional_fields = (
            'school_name',
            'program',
            'degree_type',
            'current_student',
            'start_date',
            'graduate_date',
        )


class UserSerializer(DynamicFieldsModelSerializer):
    is_staff = serializers.BooleanField(read_only=True, required=False, allow_null=True)
    is_verified = serializers.BooleanField(read_only=True, required=False, allow_null=True)
    is_superuser = serializers.BooleanField(read_only=True, required=False, allow_null=True)
    is_active = serializers.BooleanField(read_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("id", "email", "username", "is_staff", "is_superuser", "is_verified", "is_active")
        read_only_fields = (
            "id",
            "created_date",
            "updated_date",
            "is_staff",
            "is_superuser",
            "is_verified",
            "is_active"
        )
        optional = (
            "email",
            "username",
        )


class ListUserSerializer(DynamicFieldsModelSerializer):
    first_name = serializers.CharField(required=False, max_length=255, allow_null=True)
    last_name = serializers.CharField(required=False, max_length=255, allow_null=True)
    image_url = serializers.URLField(required=False, max_length=256, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=False, max_length=255)
    username = serializers.CharField(required=False, allow_null=False, max_length=255)
    is_staff = serializers.BooleanField(read_only=True, required=False, allow_null=False)
    is_verified = serializers.BooleanField(read_only=True, required=False, allow_null=False)
    is_superuser = serializers.BooleanField(read_only=True, required=False, allow_null=False)
    is_active = serializers.BooleanField(read_only=True, required=False, allow_null=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_active",
            "image_url",
            "is_verified",
        )
        read_only_fields = (
            "id",
            "created_date",
            "updated_date",
            "username",
            "is_staff",
            "is_superuser",
            "is_active",
            "is_verified",
            "user_profile",
            "user_settings",
            "user_certifications",
            "user_employers",
            "user_licenses",
            "user_schools"
        )


class ViewUserSerializer(DynamicFieldsModelSerializer):
    first_name = serializers.CharField(required=False, max_length=255, allow_null=True)
    last_name = serializers.CharField(required=False, max_length=255, allow_null=True)
    image_url = serializers.URLField(required=False, max_length=256, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=False, max_length=255)
    username = serializers.CharField(required=False, allow_null=False, max_length=255)
    is_staff = serializers.BooleanField(read_only=True, required=False, allow_null=False)
    is_verified = serializers.BooleanField(read_only=True, required=False, allow_null=False)
    is_superuser = serializers.BooleanField(read_only=True, required=False, allow_null=False)
    is_active = serializers.BooleanField(read_only=True, required=False, allow_null=False)
    user_profile = ViewUserProfileSerialzer(exclude=("user",), many=False, read_only=False, required=False,
                                            allow_null=False)
    user_settings = ViewUserSettingSerializer(exclude=("user",), many=False, read_only=False, required=False,
                                              allow_null=False)
    user_certifications = ViewUserCertificationSerializer(exclude=("user",), many=True, read_only=False, required=False,
                                                          allow_null=True)
    user_employers = ViewUserEmployerSerializer(exclude=("user",), many=True, read_only=False, required=False,
                                                allow_null=True)
    user_licenses = ViewUserLicenseSerializer(exclude=("user",), many=True, read_only=False, required=False,
                                              allow_null=True)
    user_schools = ViewUserSchoolSerializer(exclude=("user",), many=True, read_only=False, required=False,
                                            allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_active",
            "image_url",
            "is_verified",
            "user_profile",
            "user_settings",
            "user_certifications",
            "user_employers",
            "user_licenses",
            "user_schools"
        )
        read_only_fields = (
            "id",
            "created_date",
            "updated_date",
            "username",
            "is_staff",
            "is_superuser",
            "is_active",
            "is_verified",
            "user_profile",
            "user_settings",
            "user_certifications",
            "user_employers",
            "user_licenses",
            "user_schools"
        )
        optional = (
            "email",
            "image_url",
            "first_name",
            "last_name",
        )


class UpdateUserSerializer(serializers.ModelSerializer):
    image_url = serializers.URLField(required=False, max_length=256, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=False, max_length=255)
    username = serializers.CharField(required=False, allow_null=False, max_length=255)

    class Meta:
        model = User
        fields = ("id", "username", "email", "image_url")
        read_only_fields = ('id',)
        optional_fields = ("username", "email", "image_url")


class CustomRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=6,
        required=True
    )
    email = serializers.EmailField(required=True, write_only=True)
    password_1 = serializers.CharField(required=True, write_only=True)
    password_2 = serializers.CharField(required=True, write_only=True)

    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and email_address_exists(email):
            raise serializers.ValidationError(
                _("A user is already registered with this e-mail address."))
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password_1'] != data['password_2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'username': self.validated_data.get('username', ''),
            'password_1': self.validated_data.get('password_1', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
