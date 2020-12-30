from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.models import UserSetting, UserProfile, UserCertification, UserEmployer, UserLicense, UserSchool
from core.serializers import DynamicFieldsModelSerializer

User = get_user_model()


class IdUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    username = serializers.CharField(required=False, allow_null=True)


class UserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "username", "is_staff", "is_superuser")
        read_only_fields = (
            "id",
            "created_date",
            "updated_date",
        )
        optional = (
            "email",
            "username",
            "is_staff",
            "is_superuser"
        )


class UserSettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSetting
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = '__all__'



class UserCertificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserCertification
        fields = '__all__'


class UserEmployerSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserEmployer
        fields = '__all__'


class UserLicenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLicense
        fields = '__all__'


class UserSchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSchool
        fields = '__all__'
