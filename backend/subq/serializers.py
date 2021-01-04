from rest_framework import serializers

from accounts.serializers import IdUserSerializer
from core.serializers import DynamicFieldsModelSerializer
from subq.models import SubQ, SubQFollower


class SubQFollowerSerializer(DynamicFieldsModelSerializer):
    follower = IdUserSerializer(required=False, allow_null=True)

    class Meta:
        model = SubQFollower
        fields = (
            "id",
            "is_moderator",
            "join_date",
            "notifications_enabled",
            "follower",
            "is_banned"
        )


class IdSubQFollowerSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    follower = IdUserSerializer(required=False, allow_null=True)
    is_moderator = serializers.BooleanField(required=False, allow_null=True)
    is_banned = serializers.BooleanField(required=False, allow_null=True)


class IdSubQSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    sub_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    slug = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    follower_count = serializers.IntegerField(source="followers.count", required=False)


class CreateSubQSerializer(serializers.ModelSerializer):
    owner = IdUserSerializer(required=False, many=False)
    sub_name = serializers.CharField(required=True, max_length=250, allow_null=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    slug = serializers.SlugField(required=False, max_length=80, allow_null=False, allow_blank=True)

    class Meta:
        model = SubQ
        fields = ("id", "sub_name", "description", "slug", "owner")
        read_only_fields = ("id", "created_date", "updated_date",)
        optional = ("description", "slug", )


class ListSubQSerializer(DynamicFieldsModelSerializer):
    owner = IdUserSerializer(many=False)
    follower_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SubQ
        fields = (
        "id", "sub_name", "description", "slug", "owner", "created_date", "updated_date", "follower_count")
        read_only_fields = ("id", "created_date", "updated_date", "slug", "sub_name", "owner")
        optional = ("sub_name", "description", "slug", "owner",)

    def get_follower_count(self, subq):
        return subq.followers.count()

    def get_moderators(self, subq):
        moderators = SubQFollower.objects.filter(subq=subq, is_moderator=True)
        serializer = IdSubQFollowerSerializer(instance=moderators, many=True)
        return serializer.data


class ViewSubQSerializer(DynamicFieldsModelSerializer):
    sub_name = serializers.CharField(required=False, max_length=250, allow_null=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    slug = serializers.SlugField(required=False, max_length=80, allow_null=False, allow_blank=True)
    followers = IdSubQFollowerSerializer(required=False, many=True, allow_null=False)
    owner = IdUserSerializer(required=False, many=False)
    follower_count = serializers.SerializerMethodField(required=False, read_only=True)
    moderators = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = SubQ
        fields = (
            "id",
            "sub_name",
            "description",
            "slug",
            "owner",
            "followers",
            "created_date",
            "updated_date",
            "follower_count",
            "moderators"
        )
        read_only_fields = ("id", "created_date", "updated_date", "slug", "sub_name", "owner")
        optional = ("description", "owner", "followers",)

    def get_follower_count(self, subq):
        return subq.followers.count()

    def get_moderators(self, subq):
        moderators = SubQFollower.objects.filter(subq=subq, is_moderator=True)
        serializer = IdSubQFollowerSerializer(instance=moderators, many=True)
        return serializer.data


class CreateSubQFollowerSerializer(serializers.ModelSerializer):
    subq = IdSubQSerializer(required=True)

    class Meta:
        model = SubQFollower
        fields = ("id", "notifications_enabled", "subq")
        read_only_fields = ("id", "created_date", "status", "updated_date",)
        optional = ("notifications_enabled",)


class UpdateSubQFollowerSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubQFollower
        fields = ("id", "notifications_enabled", "status")
        read_only_fields = ("id", )


class ViewSubQFollowerSerializer(DynamicFieldsModelSerializer):
    follower = IdSubQFollowerSerializer(many=True, allow_null=True)

    class Meta:
        model = SubQFollower
        fields = ("id", "is_moderator", "join_date", "notifications_enabled", "follower", "subq", "is_banned")
        read_only_fields = ("id", "is_moderator", "join_date", "notifications_enabled", "follower", "subq", "is_banned")


class SubQUserSerializer(serializers.Serializer):
    user = IdUserSerializer(required=True)
