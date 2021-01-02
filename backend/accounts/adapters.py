from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.linkedin_oauth2.views import LinkedInOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from dj_rest_auth.registration.views import SocialConnectView
from dj_rest_auth.social_serializers import TwitterLoginSerializer


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class TwitterConnect(SocialConnectView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter


class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter


class LinkedInConnect(SocialConnectView):
    adapter_class = LinkedInOAuth2Adapter
