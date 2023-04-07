import aenum
from django.db import models

from hbl.models.managers import HBLManager


class HBLTeamAbbreviations(aenum.Enum):
    _init_ = "value string"

    ARGON_CONCLUSIONS = "AC", "Argon Conclusions"
    BOTTOM_OF_THE_LINEUP_CARD = "BotLC", "Back of the Lineup Card"
    CVILLE_STRANGERS = "CS", "C-ville Strangers"
    DIGITAL_SPACE_LOOP = "DSL", "Digital Space Loop"
    JAY_AND_BOBS_BOYS = "JBB", "Jay and Bobs Boys"
    JIM_WOHLFORD_CLONES = "JWC", "Jim Wohlford's Clones"
    LITTLE_GIANTS_II = "LGII", "Little Giants II"
    MGS_WONDERBOYS = "MGWB", "MG's WonderBoys"
    THE_STORAGE_JARS = "SJ", "THE STORAGE JARS"
    WABASH_GOATS = "WG", "Wabash Goats"

    def __str__(self):
        return self.string

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class HBLTeam(models.Model):
    team_id = models.IntegerField()
    name = models.CharField(max_length=25, choices=HBLTeamAbbreviations.choices())
    yahoo_team_key = models.CharField(max_length=20)
    manager = models.ForeignKey(
        HBLManager, related_name="team", on_delete=models.SET_NULL, null=True
    )
