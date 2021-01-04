from django.conf.urls import include, url  # noqa
from django.urls import path
from django.contrib import admin
import django_js_reverse.views
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from accounts.urls import auth_urlpatterns, user_urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="TheraQ API",
        default_version='v1',
        description="TheraQ API",
        terms_of_service="https://www.theraq.com/policies/terms/",
        contact=openapi.Contact(email="contact@theraq.com"),
        license=openapi.License(name="Private"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

openapi_urls = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api.json/', schema_view.without_ui(cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('baton/', include('baton.urls')),
    path("api/openapi/", include(openapi_urls), name="openapi"),
    path("api/account/", include('allauth.urls'), name="account"),
    path("api/account/auth/", include(auth_urlpatterns), name="account-auth"),
    path("api/users/", include(user_urlpatterns), name="users"),
    path("api/questions/", include("questions.urls"), name="questions"),
    path("api/subqs/", include("subq.urls"), name="subq"),

    path("", include("core.urls"), name="core"),
    path("jsreverse/", django_js_reverse.views.urls_js, name="js_reverse"),
]
