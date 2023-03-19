import requests
from decouple import config
from django.core.cache import cache
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from hbl.decorators import auth_required
from hbl.views.auth_views import refresh_token

TEAMS_API = "".join([config("YAHOO_LEAGUE_API"), "/", config("HBL_2023_ID")])


class TeamsView(ListAPIView):
    @auth_required
    def get(self, request):
        teams = requests.get(
            TEAMS_API, headers={"Authorization": f'Bearer {cache.get("access_token")}'}
        )
        print(teams.content)
        return Response(teams.json())
