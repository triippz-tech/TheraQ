from django.urls import path, include
from rest_framework.routers import DefaultRouter

from subq.views import SubQViewSet, SubQFollowerViewSet

router = DefaultRouter()

router.register(r"subqfollower", SubQFollowerViewSet, basename="subq-follower")

urlpatterns = [
    path("subq/", SubQViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path("subq/<int:pk>/", SubQViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    })),
    path("subq/<slug:sub_name>/", SubQViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    })),
    path("subq/<int:pk>/add_moderator/", SubQViewSet.as_view({
        'post': 'add_moderator',
    })),
    path("subq/<slug:sub_name>/add_moderator/", SubQViewSet.as_view({
        'post': 'add_moderator',
    })),
    path("subq/<int:pk>/remove_moderator/", SubQViewSet.as_view({
        'post': 'remove_moderator',
    })),
    path("subq/<slug:sub_name>/remove_moderator/", SubQViewSet.as_view({
        'post': 'remove_moderator',
    })),
    path("subq/<int:pk>/ban/", SubQViewSet.as_view({
        'post': 'ban',
    })),
    path("subq/<slug:sub_name>/ban/", SubQViewSet.as_view({
        'post': 'ban',
    })),
    path("subq/<int:pk>/join/", SubQViewSet.as_view({
        'post': 'join',
    })),
    path("subq/<slug:sub_name>/join/", SubQViewSet.as_view({
        'post': 'join',
    })),
    path("subq/<int:pk>/leave/", SubQViewSet.as_view({
        'post': 'leave',
    })),
    path("subq/<slug:sub_name>/leave/", SubQViewSet.as_view({
        'post': 'leave',
    })),
    ]

urlpatterns += router.urls
