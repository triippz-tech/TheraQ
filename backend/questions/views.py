from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.mixins import MultipleFieldLookupMixin
from core.renderers import TheraQJsonRenderer
from core.serializers import EmptySerializer
from questions.models import (
    Comment,
    CommentVote,
    QTag,
    Question,
    QuestionVote,
    QuestionWatchers,
    Reply,
    ReplyVote,
)
from questions.serializers import (
    CommentVoteSerializer,
    CreateCommentVoteSerializer,
    CreateQTagSerializer,
    CreateQuestionCommentSerializer,
    CreateQuestionSerializer,
    CreateQuestionVoteSerializer,
    CreateReplyCommentSerializer,
    CreateReplySerializer,
    CreateReplySerializerForQuestion,
    CreateReplyVoteSerializer,
    QTagSerializer,
    QuestionCommentSerializer,
    QuestionVoteSerializer,
    QuestionWatchersSerializer,
    ReplyCommentSerializer,
    ReplyVoteSerializer,
    ViewQuestionSerializer,
    ViewReplySerializer,
)


# TODO Change Viewers to ViewCount
# TODO Change Followers to FollowerCount
# pylint: disable=too-many-ancestors
class QuestionViewSet(MultipleFieldLookupMixin, ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = ViewQuestionSerializer
    renderer_classes = (TheraQJsonRenderer,)
    lookup_fields = ("slug", "id")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        "id",
        "post_title",
        "author",
        "author__username",
        "author__email",
        "subq__sub_name",
        "subq__slug",
        "slug",
        "status",
    ]
    search_fields = [
        "post_title",
        "slug",
        "post_body",
        "subq__sub_name",
        "subq__slug",
        "author__email",
        "author__username",
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateQuestionSerializer
        if self.action == "add_vote":
            return CreateQuestionVoteSerializer
        if (
            self.action == "add_watch"
            or self.action == "remove_watch"
            or self.action == "remove_vote"
        ):
            return EmptySerializer
        if self.action == "add_comment":
            return CreateQuestionCommentSerializer
        if self.action == "add_reply":
            return CreateReplySerializer
        return ViewQuestionSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(Question, slug=kwargs["slug"])
        except KeyError:
            item = get_object_or_404(Question, pk=kwargs["pk"])
        serializer = ViewQuestionSerializer(item)
        return Response(status=200, data=serializer.data)

    def update(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(Question, slug=kwargs["slug"])
        except KeyError:
            item = get_object_or_404(Question, pk=kwargs["pk"])
        if item.author.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = ViewQuestionSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(Question, slug=kwargs["slug"])
        except KeyError:
            item = get_object_or_404(Question, pk=kwargs["pk"])
        if item.author.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        self.archive(request, item)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=True, name="Add/Update A Vote", url_name="add_watch")
    def add_watch(self, request, *args, **kwargs):
        question: Question = get_object_or_404(Question, pk=kwargs["pk"])
        watcher, _ = QuestionWatchers.objects.get_or_create(user=request.user, question=question)
        serializer = QuestionWatchersSerializer(watcher)
        return Response(serializer.data, status=201)

    @action(methods=["POST"], detail=True, name="Add/Update A Vote", url_name="remove_watch")
    def remove_watch(self, request, *args, **kwargs):
        question: Question = get_object_or_404(Question, pk=kwargs["pk"])
        try:
            watch = QuestionWatchers.objects.get(user=request.user, question=question)
            watch.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except QuestionWatchers.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=["POST"], detail=True, name="Add/Update A Vote", url_name="add_vote")
    def add_vote(self, request, *args, **kwargs):
        question: Question = get_object_or_404(Question, pk=kwargs["pk"])
        serializer = CreateQuestionVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=True, name="Remove A Vote", url_name="remove_vote")
    def remove_vote(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        question: Question = get_object_or_404(Question, pk=pk)
        try:
            watch = QuestionVote.objects.get(user=request.user, question=question)
            watch.delete()
            return Response(status=204)
        except QuestionVote.DoesNotExist:
            return Response(status=404)

    @action(methods=["POST"], detail=True, name="Add A Comment", url_name="add_comment")
    def add_comment(self, request, *args, **kwargs):
        question: Question = get_object_or_404(Question, pk=kwargs["pk"])

        serializer = CreateQuestionCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=True, name="Add Reply", url_name="add_reply")
    def add_reply(self, request, *args, **kwargs):
        question: Question = get_object_or_404(Question, pk=kwargs["pk"])

        serializer = CreateReplySerializerForQuestion(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, question=question)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def archive(self, request, item):
        item.archive()
        return Response(status=204)


question_list_view = QuestionViewSet.as_view({"get": "list", "post": "create"})

question_detail_view = question_list = QuestionViewSet.as_view(
    {"get": "retrieve", "put": "update", "delete": "destroy"}
)


# pylint: disable=too-many-ancestors
class QTagViewSet(MultipleFieldLookupMixin, ModelViewSet):
    http_method_names = ["get", "post", "head"]
    queryset = QTag.objects.all()
    renderer_classes = (TheraQJsonRenderer,)
    lookup_fields = ("slug", "id")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "slug", "tag_name", "status"]
    search_fields = ["tag_name", "slug"]
    serializer_class = QTagSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateQTagSerializer
        return QTagSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(QTag, slug=kwargs["slug"])
        except KeyError:
            item = get_object_or_404(QTag, pk=kwargs["pk"])
        serializer = QTagSerializer(item)
        return Response(status=200, data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CreateQTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# pylint: disable=too-many-ancestors
class ReplyViewSet(ModelViewSet):
    queryset = Reply.objects.all()
    renderer_classes = (TheraQJsonRenderer,)
    lookup_field = "id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        "id",
        "user__username",
        "user__email",
        "question__id",
        "question__slug",
        "question__post_title",
        "status",
    ]
    search_fields = [
        "id",
        "reply_body",
        "user__username",
        "user__email",
        "question__slug",
        "question__post_title",
    ]
    serializer_class = ViewReplySerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateReplySerializer
        if self.action == "add_vote":
            return CreateReplyVoteSerializer
        if self.action == "remove_vote":
            return EmptySerializer
        if self.action == "add_comment":
            return CreateReplyCommentSerializer
        return ViewReplySerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateReplySerializer(data=request.data)
        if serializer.is_valid():
            if not hasattr(serializer.validated_data, "user"):
                serializer.save(user=request.user)
            else:
                serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(Reply, pk=kwargs["id"])
        serializer = ViewReplySerializer(item, data=request.data)
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(Reply, pk=kwargs["id"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        item.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=True, name="Add/Update A Vote", url_name="add_vote")
    def add_vote(self, request, *args, **kwargs):
        reply: Reply = get_object_or_404(Reply, pk=kwargs["id"])
        serializer = CreateReplyVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, reply=reply)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=["POST"], detail=True, name="Remove A Vote", url_name="remove_vote")
    def remove_vote(self, request, *args, **kwargs):
        reply: Reply = get_object_or_404(Reply, pk=kwargs["id"])
        try:
            watch = ReplyVote.objects.get(user=request.user, reply=reply)
            watch.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ReplyVote.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=["POST"], detail=True, name="Add A Comment", url_name="add_comment")
    def add_comment(self, request, *args, **kwargs):
        reply: Reply = get_object_or_404(Reply, pk=kwargs["id"])

        serializer = CreateReplyCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, reply=reply)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# pylint: disable=too-many-ancestors
class QuestionCommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    renderer_classes = (TheraQJsonRenderer,)
    lookup_field = "id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        "id",
        "user__username",
        "user__email",
        "question__slug",
        "question__post_title",
        "status"]
    search_fields = [
        "id",
        "comment_body",
        "user__username",
        "user__email",
        "question__slug",
        "question__post_title",
        "reply__reply_body",
    ]
    serializer_class = QuestionCommentSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateQuestionCommentSerializer
        if self.action == "add_vote":
            return CreateCommentVoteSerializer
        if self.action == "remove_vote":
            return EmptySerializer
        return QuestionCommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateQuestionCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(Comment, pk=kwargs["id"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        serializer = QuestionCommentSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=200, data=serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(Comment, pk=kwargs["id"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=401)
        item.archive()
        return Response(status=204)

    @action(methods=["POST"], detail=True, name="Add/Update A Vote", url_name="add_vote")
    def add_vote(self, request, *args, **kwargs):
        comment: Comment = get_object_or_404(Comment, pk=kwargs["id"])
        serializer = CreateCommentVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, comment=comment)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=["POST"], detail=True, name="Remove A Vote", url_name="remove_vote")
    def remove_vote(self, request, *args, **kwargs):
        comment: Comment = get_object_or_404(Comment, pk=kwargs["id"])
        try:
            comment_vote = CommentVote.objects.get(user=request.user, comment=comment)
            comment_vote.delete()
            return Response(status=204)
        except CommentVote.DoesNotExist:
            return Response(status=404)


# pylint: disable=too-many-ancestors
class ReplyCommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    renderer_classes = (TheraQJsonRenderer,)
    lookup_field = "id"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = [
        "id",
        "comment_body",
        "status",
        "user__username",
        "user__email",
        "question__slug",
        "question__post_title"]
    search_fields = [
        "id",
        "comment_body",
        "user__username",
        "user__email",
        "question__slug",
        "question__post_title",
        "reply__reply_body",
    ]
    serializer_class = ReplyCommentSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateReplyCommentSerializer
        if self.action == "add_vote":
            return CreateCommentVoteSerializer
        if self.action == "remove_vote":
            return EmptySerializer
        return ReplyCommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateReplyCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(Comment, pk=kwargs["id"])
        if item.user.pk != request.user.pk and not request.user.is_superuser:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = ReplyCommentSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(Comment, pk=kwargs["id"])
        item.archive()
        return Response(status=204)

    @action(methods=["POST"], detail=True, name="Add/Update A Vote", url_name="add_vote")
    def add_vote(self, request, *args, **kwargs):
        comment: Comment = get_object_or_404(Comment, pk=kwargs["id"])
        serializer = CreateCommentVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, comment=comment)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=["POST"], detail=True, name="Remove A Vote", url_name="remove_vote")
    def remove_vote(self, request, *args, **kwargs):
        comment: Comment = get_object_or_404(Comment, pk=kwargs["id"])
        comment_vote = get_object_or_404(CommentVote, user=request.user, comment=comment)
        comment_vote.delete()
        return Response(status=204)


# pylint: disable=too-many-ancestors
class CommentVoteViewSet(ModelViewSet):
    queryset = CommentVote.objects.all()
    serializer_class = CommentVoteSerializer
    renderer_classes = (TheraQJsonRenderer,)

    def list(self, request, *args, **kwargs):
        queryset = CommentVote.objects.order_by("pk")
        serializer = CommentVoteSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CommentVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, *args, **kwargs):
        queryset = CommentVote.objects.all()
        item = get_object_or_404(queryset, pk=kwargs["pk"])
        serializer = CommentVoteSerializer(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        try:
            item = CommentVote.objects.get(pk=kwargs["pk"])
        except CommentVote.DoesNotExist:
            return Response(status=404)
        serializer = CommentVoteSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        try:
            item = CommentVote.objects.get(pk=kwargs["pk"])
        except CommentVote.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class QuestionVoteViewSet(ModelViewSet):
    queryset = QuestionVote.objects.all()
    serializer_class = QuestionVoteSerializer
    renderer_classes = (TheraQJsonRenderer,)

    def create(self, request, *args, **kwargs):
        serializer = QuestionVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, *args, **kwargs):
        queryset = QuestionVote.objects.all()
        item = get_object_or_404(queryset, pk=kwargs["pk"])
        serializer = QuestionVoteSerializer(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        try:
            item = QuestionVote.objects.get(pk=kwargs["pk"])
        except QuestionVote.DoesNotExist:
            return Response(status=404)
        serializer = QuestionVoteSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        try:
            item = QuestionVote.objects.get(pk=kwargs["pk"])
        except QuestionVote.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ReplyVoteViewSet(ModelViewSet):
    queryset = ReplyVote.objects.all()
    serializer_class = ReplyVoteSerializer
    renderer_classes = (TheraQJsonRenderer,)

    def list(self, request, *args, **kwargs):
        queryset = ReplyVote.objects.order_by("pk")
        serializer = ReplyVoteSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = ReplyVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, *args, **kwargs):
        queryset = ReplyVote.objects.all()
        item = get_object_or_404(queryset, pk=kwargs["pk"])
        serializer = ReplyVoteSerializer(item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        try:
            item = ReplyVote.objects.get(pk=kwargs["pk"])
        except ReplyVote.DoesNotExist:
            return Response(status=404)
        serializer = ReplyVoteSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        try:
            item = ReplyVote.objects.get(pk=kwargs["pk"])
        except ReplyVote.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)
