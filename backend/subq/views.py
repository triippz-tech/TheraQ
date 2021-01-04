from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.error_codes import UNAUTHORIZED_ERR_401, BAD_REQUEST_ERR_400
from core.renderers import TheraQJsonRenderer
from core.serializers import EmptySerializer
from subq.exceptions import SubQException, SubQFollowerException
from subq.serializers import (
    SubQFollowerSerializer,
    ViewSubQSerializer,
    CreateSubQSerializer,
    ViewSubQFollowerSerializer,
    CreateSubQFollowerSerializer,
    UpdateSubQFollowerSerializer,
    ListSubQSerializer
)
from accounts.serializers import IdUserSerializer
from subq.models import SubQ, SubQFollower

User = get_user_model()


class SubQViewSet(ModelViewSet):
    queryset = SubQ.objects.order_by('sub_name')
    renderer_classes = (TheraQJsonRenderer,)
    lookup_fields = ('slug', 'id')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "status", "created_date", "updated_date", "sub_name", "slug", "description",
                        "owner__email", "owner__username"]
    search_fields = ["sub_name", "slug", "description", "owner__email", "owner__username"]
    serializer_class = ViewSubQSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateSubQSerializer
        if self.action == "list":
            return ListSubQSerializer
        if self.action == "add_moderator" or self.action == "remove_moderator" or self.action == "ban":
            return IdUserSerializer
        if self.action == "leave" or self.action == "join":
            return EmptySerializer
        return ViewSubQSerializer

    @swagger_auto_schema(responses={404: "SubQ Does not Exist"})
    def retrieve(self, request, *args, **kwargs):
        queryset = SubQ.objects.all()
        try:
            item = get_object_or_404(queryset=queryset, slug=kwargs["sub_name"])
        except KeyError:
            item = get_object_or_404(queryset=queryset, pk=kwargs["pk"])
        serializer = ViewSubQSerializer(item, exclude=("followers",))
        return Response(serializer.data)

    @swagger_auto_schema(responses={201: CreateSubQSerializer(), 400: "Bad Request"})
    def create(self, request, *args, **kwargs):
        serializer = CreateSubQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        responses={
            200: ViewSubQSerializer(),
            404: "SubQ Does not Exist",
            401: "UnAuthorized", 400:
                "Bad Request"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Updates the selected SubQ. May only be perofmred by the owner.
        """
        try:
            item = get_object_or_404(SubQ, slug=kwargs["sub_name"])
        except KeyError:
            item = get_object_or_404(SubQ, pk=kwargs["pk"])
        if item.owner.pk != request.user.pk and not request.user.is_superuser:
            raise SubQException(theraq_err=UNAUTHORIZED_ERR_401, default_code="update_sub_err")
        serializer = ViewSubQSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        raise SubQException(status_code=400, detail="Error encountered while updating Sub.",
                            default_code="update_sub_err")

    @swagger_auto_schema(
        responses={
            204: "Deleted",
            404: "SubQ Does not Exist",
            401: "UnAuthorized",
            400: "Bad Request"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Deletes (archives) the selected SubQ. This action may only be performed by the owner.
        """
        try:
            item = get_object_or_404(SubQ, slug=kwargs["sub_name"])
        except KeyError:
            item = get_object_or_404(SubQ, pk=kwargs["pk"])
        if item.owner.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        item.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        responses={
            200: "Moderator Added",
            404: "SubQ Does not Exist | User Not a member of Sub",
            401: "UnAuthorized",
            400: "Bad Request"
        }
    )
    @action(detail=True, methods=['POST'], name="Adds a user as a Moderator", url_name="add_moderator")
    def add_moderator(self, request, *args, **kwargs):
        """
        Adds a User as a moderator to the selected sub.

        May only be performed by the owner of the sub.
        """
        try:
            item = get_object_or_404(SubQ, slug=kwargs["sub_name"])
        except KeyError:
            item = get_object_or_404(SubQ, pk=kwargs["pk"])
        if item.owner.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = IdUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                follower: SubQFollower = SubQFollower.objects.get(follower__pk=serializer.data["id"], subq=item)
                follower.is_moderator = True
                follower.save()
                return Response(status=200)
            except SubQFollower.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={
            200: "Moderator Removed",
            404: "SubQ Does not Exist | User Not a member of Sub",
            401: "UnAuthorized",
            400: "Bad Request"
        }
    )
    @action(detail=True, methods=['POST'], name="Removes a user as a Moderator", url_name="add_moderator")
    def remove_moderator(self, request, *args, **kwargs):
        """
        Removes a user's moderator permission from the selected Sub.

        May only be performed by the Owner of the Sub
        """
        try:
            item = get_object_or_404(SubQ, slug=kwargs["sub_name"])
        except KeyError:
            item = get_object_or_404(SubQ, pk=kwargs["pk"])
        if item.owner.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = IdUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                follower: SubQFollower = SubQFollower.objects.get(follower__pk=serializer.data["id"], subq=item)
                follower.is_moderator = False
                follower.save()
                return Response(status=200)
            except SubQFollower.DoesNotExist:
                return Response(status=404)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={
            200: "User Banned",
            404: "SubQ Does not Exist | User Not a member of Sub",
            401: "UnAuthorized",
            400: "Bad Request"
        }
    )
    @action(detail=True, methods=['POST'], name="Bans a user from a sub", url_name="ban")
    def ban(self, request, *args, **kwargs):
        """
        Bans a User (follower) from the selected SubQ. Will also archive (delete) then.
        A user will not be able to re-join, unless they have been unbanned.

        Only a Moderator, Owner, or Superuser may perform this function
        """
        try:
            item = get_object_or_404(SubQ, slug=kwargs["sub_name"])
        except KeyError:
            item = get_object_or_404(SubQ, pk=kwargs["pk"])
        if not self._is_moderator_or_owner(request.user, item) and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = IdUserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                follower: SubQFollower = SubQFollower.objects.get(follower__pk=serializer.data["id"], subq=item)
                follower.ban()
                return Response(status=200)
            except SubQFollower.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        responses={
            200: "User Left",
            404: "SubQ Does not Exist | User Not a member of Sub",
            401: "UnAuthorized",
            400: "Bad Request"
        }
    )
    @action(detail=True, methods=['POST'], name="Current User will Leave the Sub", url_name="leave")
    def leave(self, request, *args, **kwargs):
        """
            Currently logged in User will leave the sub if not already a follower.
        """
        try:
            item = get_object_or_404(SubQ, slug=kwargs["sub_name"])
        except KeyError:
            item = get_object_or_404(SubQ, pk=kwargs["pk"])
        if request.user == item.owner:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            follower: SubQFollower = SubQFollower.objects.get(follower=request.user, subq=item)
            follower.archive()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SubQFollower.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={
            200: "Moderator Added",
            404: "SubQ Does not Exist",
            401: "User Previously Banned",
            400: "Bad Request"
        }
    )
    @action(detail=True, methods=['POST'], name="Current User will join the Sub", url_name="join")
    def join(self, request, *args, **kwargs):
        """
        Currently logged in User will join the sub if not already a follower.
        If user was previously banned from the sub, they will be unable to re-join it.
        """
        try:
            item = get_object_or_404(SubQ, slug=kwargs["sub_name"])
        except KeyError:
            item = get_object_or_404(SubQ, pk=kwargs["pk"])
        try:
            follower, created = SubQFollower.objects.get_or_create(follower=request.user, subq=item)
            if follower.is_banned:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            follower.status = False
            follower.save()
            return Response(status=204)
        except SubQFollower.DoesNotExist:
            SubQFollower.join_sub(request.user, item)
            return Response(status=201)

    def _is_moderator_or_owner(self, user: User, subq: SubQ):
        if user == subq.owner:
            return True
        try:
            follower = SubQFollower.objects.get(follower=user, subq=subq)
        except SubQFollower.DoesNotExist:
            return False
        if follower.is_moderator:
            return True
        return False


class SubQFollowerViewSet(ModelViewSet):
    queryset = SubQFollower.objects.order_by('subq__sub_name')
    renderer_classes = (TheraQJsonRenderer,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "status", "created_date", "updated_date", "is_moderator", "notifications_enabled",
                        "is_banned"]
    search_fields = ["sub_name", "slug", "description", "subq__sub_name", "owner__email", "owner__username"]
    serializer_class = ViewSubQFollowerSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateSubQFollowerSerializer
        if self.action == "update" or self.action == "partial_update":
            return UpdateSubQFollowerSerializer
        return ViewSubQFollowerSerializer

    def list(self, request, *args, **kwargs):
        queryset = SubQFollower.objects.order_by('subq__sub_name')
        serializer = ViewSubQFollowerSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        queryset = SubQFollower.objects.all()
        item = get_object_or_404(queryset=queryset, pk=kwargs["pk"])
        serializer = ViewSubQFollowerSerializer(item)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CreateSubQFollowerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        raise SubQFollowerException(theraq_err=BAD_REQUEST_ERR_400, default_code="delete_follower_err")

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(SubQFollower, pk=kwargs["pk"])
        if item.follower.pk != request.user.pk and not request.user.is_superuser:
            raise SubQFollowerException(theraq_err=UNAUTHORIZED_ERR_401, default_code="update_follower_err")
        serializer = UpdateSubQFollowerSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(SubQFollower, pk=kwargs["pk"])
        if item.follower.pk != request.user.pk and not request.user.is_superuser:
            raise SubQFollowerException(theraq_err=UNAUTHORIZED_ERR_401, default_code="delete_follower_err")
        item.archive()
        return Response(status=204)
