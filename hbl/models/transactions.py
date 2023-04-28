from django.db import models

from hbl.models import HBLPlayer, HBLTeam


class HBLTrade(models.Model):
    yahoo_id = models.IntegerField()


class HBLTransaction(models.Model):
    player = models.ForeignKey(
        HBLPlayer, related_name="transactions", on_delete=models.CASCADE
    )
    team = models.ForeignKey(
        HBLTeam, related_name="transactions", on_delete=models.CASCADE
    )
    date = models.DateField()
    trade = models.ForeignKey(
        HBLTrade, related_name="transactions", on_delete=models.CASCADE, null=True
    )


class HBLAddPlayer(HBLTransaction):
    yahoo_id = models.IntegerField()
    waiver = models.BooleanField(default=False)


class HBLDropPlayer(HBLTransaction):
    yahoo_id = models.IntegerField()
    add = models.ForeignKey(
        HBLAddPlayer, related_name="dropped_for", on_delete=models.SET_NULL, null=True
    )
