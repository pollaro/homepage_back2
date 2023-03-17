import requests
from decouple import config
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

TEAMS_API = "".join([config("YAHOO_LEAGUE_API"), "/", config("HBL_2023_ID")])


class TeamsView(ListAPIView):
    def get(self, request):
        pass
