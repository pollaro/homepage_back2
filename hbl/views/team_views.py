import requests
from decouple import config
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

TEAMS_API = "".join([config("YAHOO_LEAGUE_API"), "/", config("HBL_2023_ID")])


class TeamsView(ListAPIView):
    def get(self, request):
        access_token = f'Bearer {request.sessions.get("yahoo_access_token")}'
        resp = requests.get(TEAMS_API, headers={"Authorization": access_token})
        return Response(resp)
