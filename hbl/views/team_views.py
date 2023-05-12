import json
import logging

import requests
import xmltodict
from decouple import config
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework.views import APIView

from hbl.decorators import auth_required
from hbl.models import HBLTeam
from hbl.serializers import TeamSerializer

logger = logging.getLogger(__file__)


class TeamsView(APIView):
    """
    The default list of teams in hbl.
    """

    @auth_required
    def get(self, request):
        logger.info("Get HBL Teams")
        response_xml = requests.get(
            f"{config('YAHOO_LEAGUE_API')}league/{config('HBL_2023_ID')}/teams",
            headers={"Authorization": f'Bearer {cache.get("access_token")}'},
        )
        logger.info(f"Response from Yahoo is {response_xml.status_code}")
        response_dict = xmltodict.parse(response_xml.text)
        league = response_dict["fantasy_content"]["league"]["teams"]["team"]
        hbl_team_updates = []
        for team in league:
            try:
                hbl_team = HBLTeam.objects.get(team_id=team["team_id"])
            except ObjectDoesNotExist:
                manager = {
                    "hbl_id": team["managers"]["manager"]["manager_id"],
                    "name": team["managers"]["manager"]["nickname"],
                }
                team["manager"] = manager
                team["yahoo_team_key"] = team["team_key"]
                hbl_team_updates.append(team)
        serializer = TeamSerializer(data=hbl_team_updates, many=True)
        serializer.is_valid()
        serializer.save()

        return HttpResponse(json.dumps(league))


class TeamDetailView(APIView):
    @auth_required
    def get(self, request, team_id):
        response_xml = requests.get(
            f'{config("YAHOO_LEAGUE_API")}team/{config("HBL_2023_ID")}.t.{team_id}',
            headers={"Authorization": f"Bearer {cache.get('access_token')}"},
        )
        logger.info(f"Response from Yahoo is {response_xml.status_code}")
        response_dict = xmltodict.parse(response_xml.text)
        return HttpResponse(json.dumps(response_dict["fantasy_content"]["team"]))
