from django.db import models

from hbl.models.teams import HBLTeam


class Position(models.TextChoices):
    CATCHER = "C"
    FIRST_BASE = "1B"
    SECOND_BASE = "2B"
    THIRD_BASE = "3B"
    SHORTSTOP = "SS"
    LEFT_FIELD = "LF"
    CENTER_FIELD = "CF"
    RIGHT_FIELD = "RF"
    UTIL = "Util"
    PITCHER = "P"


class HBLPlayer(models.Model):
    player_id = models.IntegerField()
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    yahoo_player_key = models.CharField(max_length=20)
    team_name = models.CharField(max_length=30, null=True)
    primary_position = models.CharField(
        max_length=4, choices=Position.choices, default=Position.UTIL
    )
    eligible_positions = models.CharField(max_length=20, default=primary_position)
    hbl_team = models.ForeignKey(
        HBLTeam, related_name="team", on_delete=models.SET_NULL, null=True
    )
    previous_hbl_team = models.ForeignKey(
        HBLTeam, related_name="previous_team", on_delete=models.SET_NULL, null=True
    )
    keeper_cost = models.IntegerField(default=0)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class HBLProspect(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    yahoo_player_key = models.CharField(max_length=20, null=True)
    team_name = models.CharField(max_length=30, null=True)
    primary_position = models.CharField(
        max_length=4, choices=Position.choices, default=Position.Util
    )
    hbl_team = models.ForeignKey(
        HBLTeam, related_name="team", on_delete=models.SET_NULL, null=True
    )
    player_status = models.CharField(max_length=10, null=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_eligible(self):
        if self.player_status == "NA":
            return True
