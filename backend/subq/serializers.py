from rest_framework import serializers

from accounts.serializers import IdUserSerializer
from core.serializers import DynamicFieldsModelSerializer
from subq.models import SubQ, SubQFollower


class SubQFollowerSerializer(DynamicFieldsModelSerializer):
    follower = IdUserSerializer(required=False, allow_null=True)

    class Meta:
        model = SubQFollower
        depth = 1
        fields = (
            "id",
            "is_moderator",
            "join_date",
            "notifications_enabled",
            "follower",
            "is_banned"
        )


class IdSubQSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    follower_count = serializers.IntegerField(source="followers.count", required=False)


class SubQSerializer(DynamicFieldsModelSerializer):
    followers = SubQFollowerSerializer(many=True, allow_null=True)

    class Meta:
        model = SubQ
        depth = 1
        fields = ("id", "sub_name", "description", "slug", "owner", "followers",)
        read_only_fields = ("id",)
        optional = ("sub_name", "description", "slug", "owner", "followers",)
