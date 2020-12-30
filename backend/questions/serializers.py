from rest_framework import serializers

from accounts.serializers import UserSerializer, IdUserSerializer
from core.serializers import DynamicFieldsModelSerializer, BaseVoteSerializer
from questions.models import Question, QuestionWatchers, QuestionViews, QTag, QuestionQtag, Reply, Comment, CommentVote, \
    QuestionVote, ReplyVote
from subq.serializers import SubQSerializer, IdSubQSerializer


##########################
##     ID Serializer    ##
##########################
class IdQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    slug = serializers.SlugField(required=False, allow_null=True, allow_blank=True, max_length=80)
    post_title = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    status = serializers.BooleanField(required=False, allow_null=True)


class IdReplySerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    user = IdUserSerializer(required=False, allow_null=True)
    question = IdQuestionSerializer(required=False, allow_null=True)


class CreateCommentVoteSerializer(BaseVoteSerializer):
    class Meta:
        model = Comment
        fields = ('vote_type',)


class CommentVoteSerializer(BaseVoteSerializer):
    user = UserSerializer(
        exclude=("email", "username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True)

    class Meta:
        model = CommentVote
        fields = (
            'id',
            'vote_type',
            'user'
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )


class CreateQuestionVoteSerializer(BaseVoteSerializer):
    class Meta:
        model = Question
        fields = ('vote_type',)


class QuestionVoteSerializer(BaseVoteSerializer):
    user = UserSerializer(
        exclude=("email", "username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True)

    class Meta:
        model = QuestionVote
        fields = (
            'id',
            'vote_type',
            'user'
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )


class CreateReplyVoteSerializer(BaseVoteSerializer):
    class Meta:
        model = Reply
        fields = ('vote_type',)


class ReplyVoteSerializer(BaseVoteSerializer):
    user = UserSerializer(
        exclude=("email", "username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True)

    class Meta:
        model = ReplyVote
        fields = (
            'id',
            'vote_type',
            'user'
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )


class CreateQuestionCommentSerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=True)
    question = IdQuestionSerializer(required=True, allow_null=True)
    comment_body = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ('comment_body', 'user', 'question')
        optional_fields = ('user', 'question')


class UpdateQuestionCommentSerializer(serializers.ModelSerializer):
    comment_body = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ('id', 'comment_body')
        read_only_fields = ('id',)


class QuestionCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(
        exclude=('email',),
        read_only=False,
        required=False,
        allow_null=True)
    comment_votes = CommentVoteSerializer(
        read_only=False,
        required=False,
        allow_null=True,
        many=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'comment_body',
            'user',
            'comment_votes',
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )


class CreateReplyCommentSerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=True)
    reply = IdReplySerializer(required=True, allow_null=True)
    comment_body = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ('comment_body', 'user', 'reply')
        optional_fields = ('user', 'reply')


class UpdateReplyCommentSerializer(serializers.ModelSerializer):
    comment_body = serializers.CharField(required=True)

    class Meta:
        model = Comment
        fields = ('id', 'comment_body')
        read_only_fields = ('id',)


class ReplyCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(
        exclude=('email',),
        read_only=False,
        required=False,
        allow_null=True)
    comment_votes = CommentVoteSerializer(
        read_only=False,
        required=False,
        allow_null=True,
        many=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'comment_body',
            'user',
            'comment_votes',
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )


class QuestionReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(
        exclude=('email',),
        read_only=False,
        required=False,
        allow_null=True)
    comment_votes = CommentVoteSerializer(
        read_only=False,
        required=False,
        allow_null=True,
        many=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'comment_body',
            'user',
            'comment_votes',
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )


class QuestionWatchersSerializer(DynamicFieldsModelSerializer):
    user = UserSerializer(
        exclude=("email", "username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True)

    class Meta:
        model = QuestionWatchers
        fields = (
            'id',
            'user'
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )


class QuestionViewsSerializer(DynamicFieldsModelSerializer):
    user = UserSerializer(
        exclude=("email", "username", "is_staff", "is_superuser"),
        read_only=False,
        required=False,
        allow_null=True)

    class Meta:
        model = QuestionViews
        fields = (
            'id',
            'user'
        )
        read_only_fields = ('id',)


class CreateQTagSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(required=True, allow_null=False, max_length=50)

    class Meta:
        model = QTag
        fields = (
            'slug',
            'tag_name',
        )
        optional_fields = ('slug',)


class QTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = QTag
        fields = (
            'id',
            'tag_name',
            'slug'
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class QuestionQtagSerializer(serializers.ModelSerializer):
    qtag = QTagSerializer(read_only=False, required=False, allow_null=True, many=True)

    class Meta:
        model = QuestionQtag
        fields = (
            'id',
            'qtag',
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )


class CreateReplySerializer(serializers.ModelSerializer):
    user = IdUserSerializer(required=False, allow_null=True)
    question = IdQuestionSerializer(required=False, allow_null=True)

    class Meta:
        model = Reply
        fields = (
            'reply_body',
            'user',
            'question'
        )
        optional_fields = ('user', 'question')


class UpdateReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ('reply_body', 'status')
        read_only_fields = ('id', 'created_date', 'updated_date')
        optional_fields = ('status', 'reply_body')


# TODO Trim relations
class ViewReplySerializer(serializers.ModelSerializer):
    user = IdUserSerializer(read_only=False, required=False, allow_null=True)
    reply_comments = ReplyCommentSerializer(many=True)
    reply_votes = ReplyVoteSerializer(many=True)

    class Meta:
        model = Reply
        depth = 1
        fields = (
            'id',
            'reply_body',
            'user',
            'reply_comments',
            'reply_votes',
            'status',
        )
        read_only_fields = (
            "id",
            "created_at"
            "updated_at",
        )
        optional_fields = (
            'id',
            'reply_body',
            'user',
            'reply_comments',
            'reply_votes',
            'status',
        )


###################################
##          QUESTIONS           ###
###################################

class CreateQuestionSerializer(serializers.Serializer):
    author = IdUserSerializer(required=True)
    subq = IdSubQSerializer(required=True)
    slug = serializers.SlugField(required=False, max_length=80)
    post_title = serializers.CharField(required=True, max_length=100, min_length=10)
    post_body = serializers.CharField(required=True, min_length=50)


class UpdateQuestionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    status = serializers.BooleanField(required=False)
    post_body = serializers.CharField(required=False, min_length=50)


class ViewQuestionSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        exclude=("is_staff", "is_superuser",),
        read_only=False,
        required=False,
        allow_null=True)
    subq = SubQSerializer(
        exclude=('owner', 'description', 'slug'),
        read_only=False,
        required=False,
        allow_null=True)
    watchers = QuestionWatchersSerializer(
        exclude=('user',),
        read_only=False,
        required=False,
        allow_null=True,
        many=True)
    question_views = QuestionViewsSerializer(
        exclude=('user',),
        read_only=False,
        required=False,
        allow_null=True,
        many=True)
    question_replies = ViewReplySerializer(
        read_only=False,
        required=False,
        allow_null=True,
        many=True)
    question_comments = QuestionCommentSerializer(
        read_only=False,
        required=False,
        allow_null=True,
        many=True)

    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = ("id", "created_date", "updated_date")
        optional_fields = (
            "id", "author", "subq", "watchers", "question_views", "question_replies", "question_comments",
            "post_title", "post_body", "slug"
        )
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }
