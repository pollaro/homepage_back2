import json

import requests
import xmltodict
from decouple import config
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from hbl.models import HBLPlayer, HBLTeam
from hbl.serializers import PlayerSerializer


class TeamRosterView(APIView):
    def get(self, request, team_id):
        response_xml = requests.get(
            f'{config("YAHOO_LEAGUE_API")}team/{config("HBL_2023_ID")}.t.{team_id}//roster',
            headers={"Authorization": f"Bearer {cache.get('access_token')}"},
        )
        response_dict = xmltodict.parse(response_xml.text)
        roster = response_dict["fantasy_content"]["team"]["roster"]["players"]
        hbl_team = HBLTeam.objects.get(
            team_id=response_dict["fantasy_content"]["team"]["team_id"]
        )
        player_updates = []
        for player in roster["player"]:
            try:
                hbl_player = HBLPlayer.objects.get(player_id=player["player_id"])
                if hbl_player.previous_hbl_team != hbl_team:
                    player["previous_hbl_team"] = hbl_team
                    player["keeper_cost_next"] = 1
                else:
                    player["previous_hbl_team"] = hbl_player.previous_hbl_team
                    player["keeper_cost_current"] = hbl_player.keeper_cost_current
                    player["keeper_cost_next"] = hbl_player.keeper_cost_next
                    player["seasons_on_team"] = hbl_player.seasons_on_team
            except ObjectDoesNotExist:
                player["previous_hbl_team"] = hbl_team
            player["hbl_team"] = hbl_team
            player_updates.append(player)
        serializer = PlayerSerializer(data=player_updates, many=True)
        serializer.is_valid()
        serializer.save()

        return Response(serializer.data)
