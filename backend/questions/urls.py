from django.urls import path, include

# Routes generated by our ViewSets
from rest_framework.routers import DefaultRouter

from questions.views import (
    QTagViewSet,
    ReplyViewSet,
    QuestionCommentViewSet,
    question_list_view,
    question_detail_view,
    QuestionViewSet,
    ReplyCommentViewSet,
)

router = DefaultRouter()

router.register(r"reply", ReplyViewSet, basename="replies")
router.register(r"question-comment", QuestionCommentViewSet, basename="question-comments")
router.register(r"reply-comment", ReplyCommentViewSet, basename="reply-comments")

urlpatterns = [
    path("question/", question_list_view),
    path("question/<int:pk>/", question_detail_view),
    path("question/post/<slug:slug>/", question_detail_view),
    path("question/<int:pk>/add_watch/", QuestionViewSet.as_view({'post': 'add_watch'})),
    path("question/<int:pk>/remove_watch/", QuestionViewSet.as_view({'post': 'remove_watch'})),
    path("question/<int:pk>/add_reply/", QuestionViewSet.as_view({'post': 'add_reply'})),
    path("question/<int:pk>/add_vote/", QuestionViewSet.as_view({'post': 'add_vote'})),
    path("question/<int:pk>/remove_vote/", QuestionViewSet.as_view({'post': 'remove_vote'})),
    path("question/<int:pk>/add_comment/", QuestionViewSet.as_view({'post': 'add_comment'})),
    path("qtag/", QTagViewSet.as_view({'get': 'list', 'post': 'create'})),
    path("qtag/<int:pk>/", QTagViewSet.as_view({'get': 'retrieve'})),
    path("qtag/<slug:slug>/", QTagViewSet.as_view({'get': 'retrieve'})),
    # Add Viewers
]

urlpatterns += router.urls
