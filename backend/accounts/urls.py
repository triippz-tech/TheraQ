from django.urls import path, include
from accounts import views


auth_urlpatterns = [
    path("login-set-cookie/", views.login_set_cookie, name="login-view"),
    path("login/", views.login_view, name="login-view"),
    path("logout/", views.logout_view, name="logout-view"),
    # Social Auth Callbacks
    path("social/<backend>/", views.exchange_token, name="social-auth",),
]

auth_urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
]

user_urlpatterns = [

]
