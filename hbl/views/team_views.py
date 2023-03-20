import json

import requests
import xmltodict
from decouple import config
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework.views import APIView

from hbl.decorators import auth_required


class TeamsView(APIView):
    """
    The default list of teams in hbl.
    """

    @auth_required
    def get(self, request):
        response_xml = requests.get(
            f"{config('YAHOO_LEAGUE_API')}league/{config('HBL_2023_ID')}/teams",
            headers={"Authorization": f'Bearer {cache.get("access_token")}'},
        )
        response_json = xmltodict.parse(response_xml.text)
        league = response_json["fantasy_content"]["league"]
        return HttpResponse(json.dumps(league["teams"]["team"]))


class TeamDetailView(APIView):
    @auth_required
    def get(self, request, team_id):
        response_xml = requests.get(
            f'{config("YAHOO_LEAGUE_API")}team/{config("HBL_2023_ID")}.t.{team_id}',
            headers={"Authorization": f"Bearer {cache.get('access_token')}"},
        )
        response_json = xmltodict.parse(response_xml.text)
        return HttpResponse(json.dumps(response_json["fantasy_content"]["team"]))
