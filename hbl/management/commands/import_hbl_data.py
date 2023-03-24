import requests
import xmltodict
from decouple import config
from django.core.cache import cache
from django.core.management import BaseCommand

from hbl.decorators import auth_required
from hbl.views.auth_views import refresh_token


class Command(BaseCommand):
    help = "Calls the yahoo api to get the teams for initial db"

    def add_arguments(self, parser):
        parser.add_argument(
            "-t",
            "--team_id",
            nargs=1,
            type=int,
            help="Team id for importing one team only",
        )
        parser.add_argument("-d", "--dry_run", action="store_true")

    def handle(self, *args, **kwargs):
        if not cache.get("access_token"):
            return BaseException
        elif cache.ttl("access_token") <= 0 and cache.get("refresh_token"):
            refresh_token()
            access_token = cache.get("access_token")

        response_xml = requests.get(
            f'{config("YAHOO_LEAGUE_API")}league/{config("HBL_2023_ID")}/teams"',
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_dict = xmltodict.parse(response_xml.text)
        print(response_dict)
        teams = response_dict["fantasy_content"]["league"]["teams"]

        for key in teams["team"].keys():
            print(teams["team"])
