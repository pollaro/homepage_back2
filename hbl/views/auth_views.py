import datetime

import requests
from decouple import config
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
            request.session["yahoo_access_token"] = token["access_token"]
            request.session["yahoo_refresh_token"] = token["refresh_token"]

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
        if request.session.get("yahoo_refresh_token"):
            token = yahoo_oauth.fetch_token(
                "https://api.login.yahoo.com/oauth2/get_token",
                authorization_response=redirect_uri,
                refresh_token=request.session.get("yahoo_refresh_token"),
                client_secret=config("YAHOO_CLIENT_SECRET"),
            )
            request.session["yahoo_access_token"] = token["access_token"]
            request.session["yahoo_refresh_token"] = token["refresh_token"]
            request.session[
                "refresh_time"
            ] = datetime.datetime.now() + datetime.timedelta(seconds=3600)
            return Response(status=200)
        return Response(data=AuthenticationFailed)


class CheckLoggedInView(APIView):
    def get(self, request):
        return Response(
            bool(request.session.get("yahoo_access_token"))
            or bool(request.session.get("yahoo_refresh_token"))
        )
