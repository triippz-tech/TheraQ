from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action, api_view
from rest_framework.viewsets import ViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework import filters, mixins
from rest_framework.response import Response

from core.mixins import MultipleFieldLookupMixin
from core.renderers import TheraQJsonRenderer
from core.serializers import EmptySerializer, BaseVoteSerializer
from questions.serializers import (
    ViewQuestionSerializer,
    CreateQuestionSerializer,
    UpdateQuestionSerializer,
    QTagSerializer,
    QuestionQtagSerializer,
    ViewReplySerializer,
    CommentVoteSerializer,
    QuestionVoteSerializer,
    ReplyVoteSerializer,
    CreateReplySerializer,
    CreateQTagSerializer,
    UpdateReplySerializer,
    QuestionCommentSerializer,
    CreateQuestionCommentSerializer,
    UpdateQuestionCommentSerializer, ReplyCommentSerializer, UpdateReplyCommentSerializer, CreateReplyCommentSerializer,
    CreateCommentVoteSerializer, CreateQuestionVoteSerializer, CreateReplyVoteSerializer
)
from questions.models import (
    Question,
    QuestionWatchers,
    QuestionViews,
    QTag,
    QuestionQtag,
    Reply,
    Comment,
    CommentVote,
    QuestionVote,
    ReplyVote
)


# TODO Change Viewers to ViewCount
# TODO Change Followers to FollowerCount
class QuestionViewSet(MultipleFieldLookupMixin, ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = ViewQuestionSerializer
    renderer_classes = (TheraQJsonRenderer,)
    lookup_fields = ('slug', 'id')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "post_title", "author", "author__username", "author__email", "slug", "status"]
    search_fields = ["post_title", "slug", "post_body", "subq__sub_name", "subq__slug", "author__email",
                     "author__username"]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateQuestionSerializer
        if self.action == "update" or self.action == "partial_update":
            return UpdateQuestionSerializer
        if self.action == "add_vote":
            return CreateQuestionVoteSerializer
        if self.action == "add_watch" \
            or self.action == "remove_watch" \
            or self.action == "remove_vote":
            return EmptySerializer
        if self.action == "add_comment":
            return CreateQuestionCommentSerializer
        if self.action == "add_reply":
            return CreateReplySerializer
        return ViewQuestionSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateQuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(Question, slug=kwargs["slug"])
        except KeyError:
            item = get_object_or_404(Question, slug=kwargs["pk"])
        serializer = ViewQuestionSerializer(item)
        return Response(status=200, data=serializer.data)

    def update(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(Question, slug=kwargs["slug"])
        except KeyError:
            item = get_object_or_404(Question, slug=kwargs["pk"])
        serializer = UpdateQuestionSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        try:
            item = get_object_or_404(Question, slug=kwargs["slug"])
        except KeyError:
            item = get_object_or_404(Question, slug=kwargs["pk"])
        self.archive(request, item)

    @action(methods=['POST'], detail=True, name="Add/Update A Vote", url_name="add_watch")
    def add_watch(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        question: Question = get_object_or_404(Question, pk=pk)
        QuestionWatchers.objects.get_or_create(user=request.user, question=question)
        return Response(status=204)

    @action(methods=['POST'], detail=True, name="Add/Update A Vote", url_name="remove_watch")
    def remove_watch(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        question: Question = get_object_or_404(Question, pk=pk)
        try:
            watch = QuestionWatchers.objects.get(user=request.user, question=question)
            watch.delete()
            return Response(status=204)
        except QuestionWatchers.DoesNotExist:
            return Response(status=404)

    @action(methods=['POST'], detail=True, name="Add/Update A Vote", url_name="add_vote")
    def add_vote(self, request, *args, **kwargs):
        question: Question = get_object_or_404(Question, pk=kwargs["pk"])
        serializer = CreateQuestionVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, question=question)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=['POST'], detail=True, name="Remove A Vote", url_name="remove_vote")
    def remove_vote(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        question: Question = get_object_or_404(Question, pk=pk)
        try:
            watch = QuestionVote.objects.get(user=request.user, question=question)
            watch.delete()
            return Response(status=204)
        except QuestionVote.DoesNotExist:
            return Response(status=404)

    @action(methods=['POST'], detail=True, name="Add A Comment", url_name="add_comment")
    def add_comment(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        question: Question = get_object_or_404(Question, pk=pk)

        serializer = CreateQuestionCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, question=question)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=['POST'], detail=True, name="Add Reply", url_name="add_reply")
    def add_reply(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        question: Question = get_object_or_404(Question, pk=pk)

        serializer = CreateReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, question=question)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def archive(self, request, item):
        item.archive()
        return Response(status=204)


question_list_view = QuestionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

question_detail_view = question_list = QuestionViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})


class QTagViewSet(MultipleFieldLookupMixin, ModelViewSet):
    http_method_names = ['get', 'post', 'head']
    queryset = QTag.objects.all()
    renderer_classes = (TheraQJsonRenderer,)
    lookup_fields = ('slug', 'id')
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
            item = get_object_or_404(QTag, slug=kwargs["pk"])
        serializer = QTagSerializer(item)
        return Response(status=200, data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = CreateQTagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ReplyViewSet(ModelViewSet):
    queryset = Reply.objects.all()
    renderer_classes = (TheraQJsonRenderer,)
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "reply_body", "status"]
    search_fields = ["id", "reply_body", "user__username", "user__email", "question__slug", "question__post_title"]
    serializer_class = ViewReplySerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateReplySerializer
        if self.action == "update" or self.action == "partial_update":
            return UpdateReplySerializer
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
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(Reply, pk=kwargs["pk"])
        serializer = ViewReplySerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(Reply, pk=kwargs["pk"])
        item.archive()
        return Response(status=204)

    @action(methods=['POST'], detail=True, name="Add/Update A Vote", url_name="add_vote")
    def add_vote(self, request, *args, **kwargs):
        reply: Reply = get_object_or_404(Reply, pk=kwargs["pk"])
        serializer = CreateReplyVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, reply=reply)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=['POST'], detail=True, name="Remove A Vote", url_name="remove_vote")
    def remove_vote(self, request, *args, **kwargs):
        reply: Reply = get_object_or_404(Reply, pk=kwargs["pk"])
        try:
            watch = ReplyVote.objects.get(user=request.user, reply=reply)
            watch.delete()
            return Response(status=204)
        except ReplyVote.DoesNotExist:
            return Response(status=404)

    @action(methods=['POST'], detail=True, name="Add A Comment", url_name="add_comment")
    def add_comment(self, request, *args, **kwargs):
        reply: Reply = get_object_or_404(Reply, pk=kwargs["pk"])

        serializer = CreateReplyCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, reply=reply)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class QuestionCommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    renderer_classes = (TheraQJsonRenderer,)
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "comment_body", "status"]
    search_fields = ["id", "comment_body", "user__username", "user__email",
                     "question__slug", "question__post_title", "reply__reply_body"]
    serializer_class = QuestionCommentSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateQuestionCommentSerializer
        if self.action == "update" or self.action == "partial_update":
            return UpdateQuestionCommentSerializer
        if self.action == "add_vote":
            return CreateCommentVoteSerializer
        if self.action == "remove_vote":
            return EmptySerializer
        return QuestionCommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateQuestionCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(Comment, pk=kwargs["pk"])
        serializer = UpdateQuestionCommentSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=200, data=serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(Comment, pk=kwargs["pk"])
        item.archive()
        return Response(status=204)

    @action(methods=['POST'], detail=True, name="Add/Update A Vote", url_name="add_vote")
    def add_vote(self, request, *args, **kwargs):
        comment: Comment = get_object_or_404(Comment, pk=kwargs["pk"])
        serializer = CreateCommentVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, comment=comment)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=['POST'], detail=True, name="Remove A Vote", url_name="remove_vote")
    def remove_vote(self, request, *args, **kwargs):
        comment: Comment = get_object_or_404(Comment, pk=kwargs["pk"])
        try:
            comment_vote = CommentVote.objects.get(user=request.user, comment=comment)
            comment_vote.delete()
            return Response(status=204)
        except CommentVote.DoesNotExist:
            return Response(status=404)


class ReplyCommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    renderer_classes = (TheraQJsonRenderer,)
    lookup_field = 'id'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["id", "comment_body", "status"]
    search_fields = ["id", "comment_body", "user__username", "user__email",
                     "question__slug", "question__post_title", "reply__reply_body"]
    serializer_class = ReplyCommentSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateReplyCommentSerializer
        if self.action == "update" or self.action == "partial_update":
            return UpdateReplyCommentSerializer
        if self.action == "add_vote":
            return CreateCommentVoteSerializer
        if self.action == "remove_vote":
            return EmptySerializer
        return ReplyCommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateReplyCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, *args, **kwargs):
        item = get_object_or_404(Comment, pk=kwargs["pk"])
        serializer = UpdateReplyCommentSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=200, data=serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, *args, **kwargs):
        item = get_object_or_404(Comment, pk=kwargs["pk"])
        item.archive()
        return Response(status=204)

    @action(methods=['POST'], detail=True, name="Add/Update A Vote", url_name="add_vote")
    def add_vote(self, request, *args, **kwargs):
        comment: Comment = get_object_or_404(Comment, pk=kwargs["pk"])
        serializer = CreateCommentVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, comment=comment)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(methods=['POST'], detail=True, name="Remove A Vote", url_name="remove_vote")
    def remove_vote(self, request, *args, **kwargs):
        comment: Comment = get_object_or_404(Comment, pk=kwargs["pk"])
        comment_vote = get_object_or_404(CommentVote, user=request.user, comment=comment)
        comment_vote.delete()
        return Response(status=204)


class CommentVoteViewSet(ModelViewSet):
    queryset = CommentVote.objects.all()
    serializer_class = CommentVoteSerializer
    renderer_classes = (TheraQJsonRenderer,)

    def list(self, request):
        queryset = CommentVote.objects.order_by('pk')
        serializer = CommentVoteSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = CommentVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = CommentVote.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = CommentVoteSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = CommentVote.objects.get(pk=pk)
        except CommentVote.DoesNotExist:
            return Response(status=404)
        serializer = CommentVoteSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = CommentVote.objects.get(pk=pk)
        except CommentVote.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class QuestionVoteViewSet(ModelViewSet):
    queryset = QuestionVote.objects.all()
    serializer_class = QuestionVoteSerializer
    renderer_classes = (TheraQJsonRenderer,)

    def list(self, request):
        queryset = QuestionVote.objects.order_by('pk')
        serializer = QuestionVoteSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = QuestionVoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        queryset = QuestionVote.objects.all()
        item = get_object_or_404(queryset, pk=pk)
        serializer = QuestionVoteSerializer(item)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            item = QuestionVote.objects.get(pk=pk)
        except QuestionVote.DoesNotExist:
            return Response(status=404)
        serializer = QuestionVoteSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            item = QuestionVote.objects.get(pk=pk)
        except QuestionVote.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class ReplyVoteViewSet(ModelViewSet):
    queryset = ReplyVote.objects.all()
    serializer_class = ReplyVoteSerializer
    renderer_classes = (TheraQJsonRenderer,)

    def list(self, request, *args, **kwargs):
        queryset = ReplyVote.objects.order_by('pk')
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
