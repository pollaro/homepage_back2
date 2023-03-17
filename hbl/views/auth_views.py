import requests
from decouple import config
from django.core.cache import cache
from django.http import HttpResponse
from requests_oauthlib import OAuth2Session
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

redirect_uri = (
    config("YAHOO_REDIRECT_URI_DEBUG")
    if config("DEBUG")
    else config("YAHOO_REDIRECT_URI")
)
yahoo_oauth = OAuth2Session(
    client_id=config("YAHOO_CLIENT_ID"), redirect_uri=redirect_uri
)


class OauthView(APIView):
    def post(self, request):
        auth_url, state = yahoo_oauth.authorization_url(
            "https://api.login.yahoo.com/oauth2/request_auth"
        )
        return Response(auth_url)


class RedirectURIView(APIView):
    def get(self, request):
        code = request.query_params.get("code")
        if code:
            token = yahoo_oauth.fetch_token(
                "https://api.login.yahoo.com/oauth2/get_token",
                authorization_response=redirect_uri,
                code=code,
                client_secret=config("YAHOO_CLIENT_SECRET"),
            )
            cache.set(
                "access_token", token["access_token"], timeout=3600
            )  # 1 hour in ms
            cache.set("refresh_token", token["refresh_token"], timeout=None)

            return HttpResponse(
                """
                    <body>
                        <script>
                            window.close()
                        </script>
                    </body>
                """
            )


class RefreshTokenView(APIView):
    def get(self, request):
        if cache.ttl("access_token") <= 0 and cache.get("refresh_token"):
            token = yahoo_oauth.fetch_token(
                "https://api.login.yahoo.com/oauth2/get_token",
                authorization_response=redirect_uri,
                refresh_token=cache.get("refresh_token"),
                client_secret=config("YAHOO_CLIENT_SECRET"),
            )
            cache.set(
                "access_token", token["access_token"], timeout=3600
            )  # 1 hour in ms
            cache.set("refresh_token", token["refresh_token"], timeout=None)
            return Response(True)
        return Response(False)


class CheckLoggedInView(APIView):
    def get(self, request):
        if cache.get("access_token") or cache.get("refresh_token"):
            return Response(True)
        return Response(False)
