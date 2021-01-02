import json

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import filters, mixins


from accounts.models import (
    UserSetting,
    UserProfile,
    UserCertification,
    UserEmployer,
    UserLicense,
    UserSchool
)
from accounts.serializers import (
    ViewUserSettingSerializer,
    UpdateUserSettingSerializer,
    UpdateUserProfileSerializer,
    ViewUserProfileSerialzer,
    ViewUserSerializer,
    UpdateUserSerializer,
    ViewUserCertificationSerializer,
    UpdateUserCertificationSerializer,
    CreateUserCertificationSerializer,
    UpdateUserEmployerSerializer,
    CreateUserEmployerSerializer,
    ViewUserEmployerSerializer,
    ViewUserLicenseSerializer,
    UpdateUserLicenseSerializer,
    CreateUserLicenseSerializer,
    UpdateUserSchoolSerializer,
    CreateUserSchoolSerializer,
    ViewUserSchoolSerializer
)
from core.renderers import TheraQJsonRenderer

User = get_user_model()


class UserSettingViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = UserSetting.objects.all()
    serializer_class = ViewUserSettingSerializer
    renderer_classes = (TheraQJsonRenderer,)

    def get_serializer_class(self):
        if self.action == "update":
            return UpdateUserSettingSerializer
        return ViewUserSettingSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(UserSetting, slug=kwargs["slug"])
        except KeyError:
            item = get_object_or_404(UserSetting, pk=kwargs["pk"])
        serializer = ViewUserSettingSerializer(item)
        return Response(status=200, data=serializer.data)

    def update(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(UserSetting, slug=kwargs["slug"])
        except KeyError:
            item = get_object_or_404(UserSetting, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        serializer = UpdateUserSettingSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class UserProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ViewUserProfileSerialzer
    renderer_classes = (TheraQJsonRenderer,)

    def get_serializer_class(self):
        if self.action == "update":
            return UpdateUserProfileSerializer
        return ViewUserProfileSerialzer

    def retrieve(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(UserProfile, user__username=kwargs["username"])
        except KeyError:
            item = get_object_or_404(UserProfile, pk=kwargs["pk"])
        serializer = ViewUserProfileSerialzer(item)
        return Response(status=200, data=serializer.data)

    def update(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(UserSetting, user__username=kwargs["username"])
        except KeyError:
            item = get_object_or_404(UserSetting, pk=kwargs["pk"])
        serializer = UpdateUserProfileSerializer(item, data=request.data)
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = ViewUserSerializer
    renderer_classes = (TheraQJsonRenderer,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "is_staff", "is_superuser", "is_active", "is_verified"]
    search_fields = ["email", "username", "user_certifications__certificate_program",
                     "user_certifications__institution_name", "user_employers__employer_name",
                     "users_employer__position",  "user_licenses__issuing_authority", "user_licenses__license_type",
                     "user_schools__school_name", "user_schools__program"]

    def get_serializer_class(self):
        if self.action == "update" or self.action == "partial_update":
            return UpdateUserSerializer
        return ViewUserSettingSerializer

    def list(self, request, *args, **kwargs):
        queryset = User.objects.order_by('username')
        serializer = ViewUserSerializer(queryset, many=True, exclude=(
            "user_profile",
            "user_settings",
            "user_certifications",
            "user_employers",
            "user_licenses",
            "user_schools"
        ))
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(User, username=kwargs["username"])
        except KeyError:
            item = get_object_or_404(User, pk=kwargs["pk"])
        serializer = ViewUserSerializer(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(User, username=kwargs["username"])
        except KeyError:
            item = get_object_or_404(User, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        serializer = UpdateUserSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class UserCertificationViewSet(viewsets.ModelViewSet):
    queryset = UserCertification.objects.all()
    serializer_class = ViewUserCertificationSerializer
    renderer_classes = (TheraQJsonRenderer,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "status", "completion_date"]
    search_fields = ["user__email", "user__username", "certificate_program",
                     "institution_name", "certificate_number"]

    def get_serializer_class(self):
        if self.action == "update" or self.action == "partial_update":
            return UpdateUserCertificationSerializer
        if self.action == "create":
            return CreateUserCertificationSerializer
        return ViewUserCertificationSerializer

    def list(self, request, *args, **kwargs):
        queryset = UserCertification.objects.order_by('certificate_program')
        serializer = ViewUserCertificationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CreateUserCertificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    # TODO - Won't be efficient, might need to change query
    def retrieve(self, request, *args, **kwargs):
        queryset = UserCertification.objects.all()
        item = get_object_or_404(queryset, pk=kwargs["pk"])
        serializer = ViewUserCertificationSerializer(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(UserCertification, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        serializer = UpdateUserCertificationSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(UserCertification, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        item.archive()
        return Response(status=204)


class UserEmployerViewSet(viewsets.ModelViewSet):
    queryset = UserEmployer.objects.all()
    serializer_class = ViewUserEmployerSerializer
    renderer_classes = (TheraQJsonRenderer,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "status", "start_date", "end_date", "current_position"]
    search_fields = ["user__email", "user__username", "employer_name", "position", "description"]

    def get_serializer_class(self):
        if self.action == "update" or self.action == "partial_update":
            return UpdateUserEmployerSerializer
        if self.action == "create":
            return CreateUserEmployerSerializer
        return ViewUserEmployerSerializer

    def list(self, request, *args, **kwargs):
        queryset = UserEmployer.objects.order_by('employer_name')
        serializer = ViewUserEmployerSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CreateUserEmployerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, *args, **kwargs):
        queryset = UserEmployer.objects.all()
        item = get_object_or_404(queryset, pk=kwargs["pk"])
        serializer = ViewUserEmployerSerializer(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(UserEmployer, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        serializer = UpdateUserEmployerSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(UserEmployer, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        item.archive()
        return Response(status=204)


class UserLicenseViewSet(viewsets.ModelViewSet):
    queryset = UserLicense.objects.all()
    serializer_class = ViewUserLicenseSerializer
    renderer_classes = (TheraQJsonRenderer,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "status", "completion_date", "expiration_date"]
    search_fields = ["user__email", "user__username", "issuing_authority", "license_type", "license_number"]

    def get_serializer_class(self):
        if self.action == "update" or self.action == "partial_update":
            return UpdateUserLicenseSerializer
        if self.action == "create":
            return CreateUserLicenseSerializer
        return ViewUserLicenseSerializer

    def list(self, request, *args, **kwargs):
        queryset = UserLicense.objects.order_by('license_type')
        serializer = ViewUserLicenseSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CreateUserLicenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, *args, **kwargs):
        queryset = UserLicense.objects.all()
        item = get_object_or_404(queryset, pk=kwargs["pk"])
        serializer = ViewUserLicenseSerializer(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(UserLicense, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        serializer = UpdateUserLicenseSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(UserLicense, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        item.archive()
        return Response(status=204)


class UserSchoolViewSet(viewsets.ModelViewSet):
    queryset = UserSchool.objects.all()
    serializer_class = ViewUserSchoolSerializer
    renderer_classes = (TheraQJsonRenderer,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "status", "start_date", "graduate_date", "degree_type", "current_student"]
    search_fields = ["user__email", "user__username", "school_name", "program"]

    def get_serializer_class(self):
        if self.action == "update" or self.action == "partial_update":
            return UpdateUserSchoolSerializer
        if self.action == "create":
            return CreateUserSchoolSerializer
        return ViewUserSchoolSerializer

    def list(self, request, *args, **kwargs):
        queryset = UserSchool.objects.order_by('school_name')
        serializer = ViewUserSchoolSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CreateUserSchoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, *args, **kwargs):
        queryset = UserSchool.objects.all()
        item = get_object_or_404(queryset, pk=kwargs["pk"])
        serializer = ViewUserSchoolSerializer(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(UserSchool, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        serializer = UpdateUserSchoolSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(UserSchool, pk=kwargs["pk"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        item.archive()
        return Response(status=204)
