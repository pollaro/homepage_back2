import json
import logging

import requests
import xmltodict
from decouple import config
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.views import APIView

from hbl.decorators import auth_required
from hbl.models import HBLPlayer, HBLTeam, HBLTransaction
from hbl.serializers import TransactionSerializer

logger = logging.getLogger(__name__)


class TransactionsView(APIView):
    """
    Retrieve Transactions from yahoo
    """

    @auth_required
    def get(self, request):
        logger.info("Get HBL Transactions")
        response_xml = requests.get(
            f"{config('YAHOO_LEAGUE_API')}league/{config('HBL_2023_ID')}/transactions",
            headers={"Authorization": f"Bearer {cache.get('access_token')}"},
        )
        logger.info(f"Response from Yahoo is {response_xml.status_code}")
        response_dict = xmltodict.parse(response_xml.text)
        transactions = response_dict["fantasy_content"]["league"]["transactions"]
        new_transactions = []
        last_transaction = HBLTransaction.objects.all().latest("yahoo_id")
        for transaction in transactions:
            if transaction["transaction_id"] <= last_transaction.yahoo_id:
                break
            new_transactions.append(transaction)
        new_transactions = new_transactions[::-1]
        updated_transaction = []
        for transaction in new_transactions:
            if transaction["type"] == "trade":
                team1_transaction = transaction
                team1_transaction["team"] = transaction["trader_team_name"]
                team1_transaction["player"] = []
                team2_transaction = transaction.copy()
                team2_transaction["team"] = transaction["tradee_team_name"]
                team2_transaction["player"] = []
                team2_transaction["related_transaction"] = team1_transaction
            elif transaction["type"] == "add/drop":
                add_transaction = transaction
                drop_transaction = transaction.copy()
                drop_transaction["related_transaction"] = add_transaction
            elif transaction["type"] == "add":
                add_transaction = transaction
            else:
                drop_transaction = transaction
            for player in transaction["players"]:
                hbl_team = HBLTeam.objects.get(
                    name=player["transaction_data"]["destination_team_name"]
                )
                try:
                    player = HBLPlayer.objects.get(player_id=player["player_id"])
                    if player.previous_hbl_team != hbl_team:
                        player["previous_hbl_team"] = hbl_team
                        player["keeper_cost_next"] = 1
                    else:
                        player["previous_hbl_team"] = player.previous_hbl_team
                        player["keeper_cost_next"] = player.keeper_cost_next
                        player["keeper_cost_current"] = player.keeper_cost_current
                        player["seasons_on_team"] = player.seasons_on_team
                except ObjectDoesNotExist:
                    player["previous_hbl_team"] = hbl_team
                if player["transaction_data"]["type"] == "add":
                    add_transaction["player"] = player
                elif player["transaction_data"]["type"] == "drop":
                    drop_transaction["player"] = player
                elif (
                    player["transaction_data"]["type"] == "trade"
                    and player["transaction_data"]["destination_team_name"]
                    == team1_transaction["team"]
                ):
                    team1_transaction["player"].append(player)
                elif player["transaction_data"]["type"] == "trade":
                    team2_transaction["player"].append(player)
            if transaction["type"] == "add" or transaction["type"] == "add/drop":
                updated_transaction.append(add_transaction)
            if transaction["type"] == "drop" or transaction["type"] == "add/drop":
                updated_transaction.append(drop_transaction)
            if transaction["type"] == "trade":
                updated_transaction.append(team1_transaction)
                updated_transaction.append(team2_transaction)
        serializer = TransactionSerializer(data=updated_transaction, many=True)
        serializer.is_valid()
        serializer.save()

        return Response(json.dumps(serializer.data))
