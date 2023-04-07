import pandas as pd
from django.core.management import BaseCommand

from hbl.models import HBLTeam, HBLTeamAbbreviations
from hbl.models.players import HBLProspect


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("xl_file", type=str, help="Name of Excel File")
        parser.add_argument("-d", "--dry_run", action="store_true", help="Testing")

    def handle(self, *args, **options):
        xls = pd.ExcelFile(options["xl_file"])
        df = pd.read_excel(xls, "Farm Rosters")
        curr_df = df.iloc[:,]
        prospect_array = []
        for idx, row in curr_df.iterrows():
            print(row)
            name, primary_position, team_name, hbl_team = (
                row.iloc[1],
                row.iloc[3],
                row.iloc[4],
                row.iloc[6],
            )
            if not name:
                break
            name_split = name.split(" ")
            print(HBLTeamAbbreviations(hbl_team))
            first_name = name_split[0]
            last_name = " ".join(name_split[1:])
            prospect = HBLProspect(
                first_name=first_name,
                last_name=last_name,
                primary_position=primary_position,
                team_name=team_name,
                hbl_team=HBLTeam.objects.get(name=HBLTeamAbbreviations(hbl_team)),
            )
            prospect_array.append(prospect)
        if options["dry_run"]:
            for prospect in prospect_array:
                print(prospect)
        else:
            HBLProspect.objects.bulk_create(prospect_array)
