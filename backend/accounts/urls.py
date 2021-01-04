from dj_rest_auth.registration.views import SocialAccountListView, SocialAccountDisconnectView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.adapters import (
    FacebookConnect,
    GoogleConnect,
    TwitterConnect,
    LinkedInConnect
)
from accounts.views import (
    UserSettingViewSet,
    UserProfileViewSet,
    UserViewSet,
    UserCertificationViewSet,
    UserEmployerViewSet,
    UserLicenseViewSet,
    UserSchoolViewSet
)

auth_urlpatterns = [
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls')),
    # path("facebook/connect/", FacebookConnect.as_view(), name="fb_connect"),
    # path("google/connect/", GoogleConnect.as_view(), name="google_connect"),
    # path("twitter/connect/", TwitterConnect.as_view(), name="twitter_connect"),
    # path("linkedin/connect/", LinkedInConnect.as_view(), name="linkedin_connect"),
    # path("socialaccounts/", SocialAccountListView.as_view(), name="social_account_list"),
    # path("socialaccounts/<int:pk>/disconnect/", SocialAccountDisconnectView.as_view(),
    #      name="social_account_disconnect"),
]

# auth_urlpatterns += [
#     path("api-auth/", include("rest_framework.urls")),
# ]

user_router = DefaultRouter()
user_router.register(r"certifications", UserCertificationViewSet, basename="user-certifications")
user_router.register(r"employers", UserEmployerViewSet, basename="user-employers")
user_router.register(r"licenses", UserLicenseViewSet, basename="user-licenses")
user_router.register(r"schools", UserSchoolViewSet, basename="user-schools")

user_urlpatterns = [
    path("settings/<int:pk>/", UserSettingViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    })),
    path("settings/<slug:slug>/", UserSettingViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    })),
    path("profile/<int:pk>/", UserProfileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    })),
    path("profile/<slug:username>/", UserProfileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    })),
    path("user/", UserViewSet.as_view({
        'get': 'list'
    })),
    path("user/<int:pk>/", UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    })),
    path("user/<slug:username>/", UserViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    })),
]

user_urlpatterns += user_router.urls
