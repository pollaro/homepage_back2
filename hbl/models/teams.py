from django.db import models

from hbl.models.managers import HBLManager


class HBLTeam(models.Model):
    team_id = models.IntegerField()
    name = models.CharField(max_length=64)
    yahoo_team_key = models.CharField(max_length=20)
    manager = models.ForeignKey(
        HBLManager, related_name="team", on_delete=models.SET_NULL
    )
