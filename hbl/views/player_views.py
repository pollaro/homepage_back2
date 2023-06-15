import json

import requests
import xmltodict
from decouple import config
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView

from hbl.models import HBLPlayer, HBLProspect, HBLTeam
from hbl.serializers import PlayerSerializer, ProspectSerializer
from hbl.views.auth_views import get_user


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

        return Response(json.dumps(serializer.data))


class ProspectRosterView(APIView):
    def get(self, request, team_id=""):
        if team_id:
            prospects = HBLProspect.objects.filter(hbl_team_id=team_id)
        else:
            prospects = HBLProspect.objects.filter(hbl_team__isnull=False)

        serializer = ProspectSerializer(prospects, many=True)

        return Response(json.dumps(serializer.data))


class ProspectAddView(APIView):
    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        mlb_team = request.data.get("mlb_team")
        position = request.data.get("position")
        if first_name and last_name and mlb_team:
            prospect_in_db = HBLProspect.objects.filter(
                first_name=first_name, last_name=last_name, team_name=mlb_team
            )
            if prospect_in_db and prospect_in_db.count() == 1:
                prospect_in_db = prospect_in_db.get()
                prospect_in_db.position = position
            elif not prospect_in_db:
                prospect_in_db = HBLProspect(
                    first_name=first_name,
                    last_name=last_name,
                    team_name=mlb_team,
                    primary_position=position,
                )
            else:
                return Response("Too many prospects found", status=400)
            team = HBLTeam.objects.get(manager__guid=get_user())
            if team is None:
                return Response("No HBLTeam found", status=400)
            prospect_in_db.hbl_team = team
            prospect_in_db.save()
            return Response(
                {
                    "msg": f"Prospect {first_name} {last_name} {mlb_team}-{position} added to {team.name}",
                    "hbl_team": {"id": team.id, "name": team.name},
                },
                status=200,
            )

        return Response("No first name, last name, or MLB team provided", status=400)


class ProspectRemoveView(APIView):
    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        mlb_team = request.data.get("mlb_team")
        position = request.data.get("position")
        if first_name and last_name and mlb_team:
            prospect_in_db = HBLProspect.objects.filter(
                first_name=first_name, last_name=last_name, team_name=mlb_team
            )
            if prospect_in_db and prospect_in_db.count() == 1:
                prospect_in_db = prospect_in_db.get()
                team = prospect_in_db.hbl_team
                prospect_in_db.hbl_team = None
                prospect_in_db.save()
                return Response(
                    {
                        "msg": f"Prospect {first_name} {last_name} was dropped from {team.name}",
                        "hbl_team": {"id": team.id, "name": team.name},
                    },
                    status=200,
                )
            else:
                return Response("No Prospect Found", status=400)
        return Response("No first name, last name, or MLB team provided", status=400)
