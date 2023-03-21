import json

import requests
import xmltodict
from decouple import config
from django.core.cache import cache
from django.http import HttpResponse
from rest_framework.views import APIView


class TeamRosterView(APIView):
    def get(self, request, team_id):
        response_xml = requests.get(
            f'{config("YAHOO_LEAGUE_API")}team/{config("HBL_2023_ID")}.t.{team_id}//roster',
            headers={"Authorization": f"Bearer {cache.get('access_token')}"},
        )
        response_json = xmltodict.parse(response_xml.text)
        return HttpResponse(
            json.dumps(response_json["fantasy_content"]["team"]["roster"]["players"])
        )
