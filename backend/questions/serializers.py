from rest_framework import serializers

from accounts.serializers import IdUserSerializer, UserSerializer
from core.models import VOTE_TYPES
from core.serializers import BaseVoteSerializer, ChoicesField, DynamicFieldsModelSerializer
from questions.models import (
    Comment,
    CommentVote,
    QTag,
    Question,
    QuestionQtag,
    QuestionViews,
    QuestionVote,
    QuestionWatchers,
    Reply,
    ReplyVote,
    SubQ,
)
from subq.serializers import IdSubQSerializer, ViewSubQSerializer


##########################
##     ID Serializer    ##
##########################

# pylint: disable=abstract-method
class IdQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    slug = serializers.SlugField(required=False, allow_null=True, allow_blank=True, max_length=80)
    post_title = serializers.CharField(
        max_length=100, required=False, allow_null=True, allow_blank=True
    )
    status = serializers.BooleanField(required=False, allow_null=True)


# pylint: disable=abstract-method
class IdReplySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    user = IdUserSerializer(required=False, allow_null=True)
    question = IdQuestionSerializer(required=False, allow_null=True)


class IdCommentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    user = IdUserSerializer(required=False, allow_null=False)
    question = IdQuestionSerializer(required=False, allow_null=True)
    reply = IdReplySerializer(required=False, allow_null=True)


class IdQTagSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class CreateCommentVoteSerializer(BaseVoteSerializer):
    vote_type = ChoicesField(choices=VOTE_TYPES)
    user = IdUserSerializer(required=False, allow_null=False)
    comment = IdCommentSerializer(required=False, allow_null=False)

    class Meta:
        model = CommentVote
        fields = ("vote_type", "user", "comment")


class CommentVoteSerializer(BaseVoteSerializer):
    user = UserSerializer(
        exclude=("username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CommentVote
        fields = ("id", "vote_type", "user")
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class CreateQuestionVoteSerializer(BaseVoteSerializer):
    vote_type = ChoicesField(
        VOTE_TYPES,
        required=True,
        allow_null=False,
        error_messages={"required": "Must select a Vote Type"},
    )

    class Meta:
        model = QuestionVote
        fields = ("vote_type",)


class QuestionVoteSerializer(BaseVoteSerializer):
    user = UserSerializer(
        exclude=("username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = QuestionVote
        fields = ("id", "vote_type", "user")
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class CreateReplyVoteSerializer(BaseVoteSerializer):
    user = IdUserSerializer(required=False, allow_null=False)
    reply = IdReplySerializer(required=False, allow_null=False)
    vote_type = ChoicesField(choices=VOTE_TYPES)

    class Meta:
        model = ReplyVote
        fields = ("id", "vote_type", "user", "reply")


class ReplyVoteSerializer(BaseVoteSerializer):
    user = UserSerializer(
        exclude=("username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ReplyVote
        fields = ("id", "vote_type", "user")
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class CreateQuestionCommentSerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=False)
    question = IdQuestionSerializer(required=False, allow_null=False)
    comment_body = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ("id", "comment_body", "user", "question")
        read_only_fields = ("id",)

    def create(self, validated_data):
        if not isinstance(validated_data.get("question"), Question):
            question_data = validated_data.pop("question")
            question = Question.objects.get(**question_data)
            return Comment.objects.create(question=question, **validated_data)
        return Comment.objects.create(**validated_data)


class QuestionCommentSerializer(serializers.ModelSerializer):
    comment_body = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user = UserSerializer(read_only=False, required=False, allow_null=False)
    comment_votes = CommentVoteSerializer(
        read_only=False, required=False, allow_null=False, many=True
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "comment_body",
            "user",
            "comment_votes",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class CreateReplyCommentSerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=False, allow_null=False)
    reply = IdReplySerializer(required=False, allow_null=False)
    comment_body = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ("comment_body", "user", "reply")
        optional_fields = ("user", "reply")

    def create(self, validated_data):
        if not isinstance(validated_data.get("reply"), Reply):
            reply_data = validated_data.pop("reply")
            reply = Reply.objects.get(**reply_data)
            return Comment.objects.create(reply=reply, **validated_data)
        return Comment.objects.create(**validated_data)


class ReplyCommentSerializer(serializers.ModelSerializer):
    comment_body = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user = UserSerializer(read_only=False, required=False, allow_null=True)
    comment_votes = CommentVoteSerializer(
        read_only=False, required=False, allow_null=True, many=True
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "comment_body",
            "user",
            "comment_votes",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class QuestionReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False, required=False, allow_null=True)
    comment_votes = CommentVoteSerializer(
        read_only=False, required=False, allow_null=True, many=True
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "comment_body",
            "user",
            "comment_votes",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class QuestionWatchersSerializer(DynamicFieldsModelSerializer):
    user = UserSerializer(
        exclude=("username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = QuestionWatchers
        fields = ("id", "user")
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class QuestionViewsSerializer(DynamicFieldsModelSerializer):
    user = UserSerializer(
        exclude=("username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = QuestionViews
        fields = ("id", "user")
        read_only_fields = ("id",)


class CreateQTagSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(required=True, allow_null=False, max_length=50)

    class Meta:
        model = QTag
        fields = (
            "slug",
            "tag_name",
        )
        optional_fields = ("slug",)


class QTagSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(required=False, allow_null=False, read_only=True)
    slug = serializers.CharField(required=False, allow_null=False, read_only=True)

    class Meta:
        model = QTag
        fields = ("id", "tag_name", "slug")
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )
        lookup_field = "slug"
        extra_kwargs = {"url": {"lookup_field": "slug"}}


class QuestionQtagSerializer(serializers.ModelSerializer):
    qtag = QTagSerializer(read_only=False, required=False, allow_null=True, many=True)

    class Meta:
        model = QuestionQtag
        fields = (
            "id",
            "qtag",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class CreateReplySerializerForQuestion(serializers.ModelSerializer):
    user = IdUserSerializer(required=False, allow_null=False)
    question = IdQuestionSerializer(required=False, allow_null=False)

    class Meta:
        model = Reply
        fields = ("reply_body", "user", "question")
        optional_fields = ("user", "question")


class CreateReplySerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=False, allow_null=False)
    question = IdQuestionSerializer(required=False, allow_null=False)

    class Meta:
        model = Reply
        fields = ("reply_body", "user", "question")
        optional_fields = ("user", "question")

    def create(self, validated_data):
        question_data = validated_data.pop("question")
        question = Question.objects.get(**question_data)
        return Reply.objects.create(question=question, **validated_data)


class UpdateReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ("reply_body", "status")
        read_only_fields = ("id", "created_date", "updated_date")
        optional_fields = ("status", "reply_body")


# TODO Trim relations
class ViewReplySerializer(serializers.ModelSerializer):
    user = IdUserSerializer(read_only=False, required=False, allow_null=False)
    reply_comments = ReplyCommentSerializer(many=True, allow_null=False, required=False)
    reply_votes = ReplyVoteSerializer(many=True, allow_null=False, required=False)
    reply_body = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Reply
        depth = 1
        fields = (
            "id",
            "reply_body",
            "user",
            "reply_comments",
            "reply_votes",
            "status",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )
        optional_fields = (
            "id",
            "reply_body",
            "user",
            "reply_comments",
            "reply_votes",
            "status",
        )


################################### nopep8
##          QUESTIONS           ### nopep8
################################### nopep8


class CreateQuestionSerializer(serializers.ModelSerializer):
    author = IdUserSerializer(required=False, allow_null=False)
    subq = IdSubQSerializer(required=True, allow_null=False)
    slug = serializers.SlugField(required=False, max_length=80, allow_null=False, allow_blank=True)
    post_title = serializers.CharField(
        required=True, max_length=100, min_length=10, allow_null=False, allow_blank=False
    )
    post_body = serializers.CharField(
        required=True, min_length=50, allow_null=False, allow_blank=True
    )
    qtags = IdQTagSerializer(many=True, required=False, allow_null=True)
    question_tags = serializers.SerializerMethodField(required=False, allow_null=True)

    class Meta:
        model = Question
        fields = ("id", "author", "subq", "slug", "post_title", "post_body", "qtags", "question_tags")
        read_only_fields = ("id", "created_date", "updated_date", "status")
        optional_fields = ("id", "slug", "author", "qtags", "question_tags")

    def get_question_tags(self, question):
        qtags = QTag.objects.filter(question_tags__question=question)
        serializer = QTagSerializer(qtags, many=True)
        return serializer.data

    def create(self, validated_data):
        subq_data = validated_data.pop("subq")
        subq = SubQ.objects.get(**subq_data)

        qtag_data = validated_data.pop("qtags")

        question = Question.objects.create(subq=subq, **validated_data)

        for qtag in qtag_data:
            found_qtag = QTag.objects.get(**qtag)
            QuestionQtag.objects.create(qtag=found_qtag, question=question)

        question = Question.objects.get(pk=question.pk)
        return question


class ViewQuestionSerializer(serializers.ModelSerializer):
    post_body = serializers.CharField(
        required=False, min_length=50, allow_null=True, allow_blank=True
    )
    author = UserSerializer(
        exclude=("is_staff", "is_superuser", "user_settings"),
        read_only=True,
        required=False,
        allow_null=False,
    )
    subq = ViewSubQSerializer(
        exclude=("owner", "description", "slug"),
        read_only=True,
        required=False,
        allow_null=False,
    )
    watchers = QuestionWatchersSerializer(
        exclude=("user",), read_only=True, required=False, allow_null=False, many=True
    )
    question_views = QuestionViewsSerializer(
        exclude=("user",), read_only=True, required=False, allow_null=False, many=True
    )
    question_replies = ViewReplySerializer(
        read_only=False, required=False, allow_null=True, many=True
    )
    question_comments = QuestionCommentSerializer(
        read_only=False, required=False, allow_null=True, many=True
    )
    view_count = serializers.SerializerMethodField(read_only=True)
    votes = serializers.SerializerMethodField(read_only=True)
    qtags = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = ("id", "created_date", "updated_date", "status")
        optional_fields = (
            "id",
            "author",
            "subq",
            "watchers",
            "question_views",
            "question_replies",
            "question_comments",
            "post_title",
            "post_body",
            "slug",
            "qtags"
        )
        lookup_field = "slug"
        extra_kwargs = {"url": {"lookup_field": "slug"}}

    def get_qtags(self, question):
        qtags = QTag.objects.filter(question_tags__question=question)
        serializer = QTagSerializer(qtags, many=True)
        return serializer.data

    def get_view_count(self, question):
        return question.question_views.count()

    def get_votes(self, question):
        return QuestionVote.objects.filter(question=question, vote_type="UP_VOTE").count()
