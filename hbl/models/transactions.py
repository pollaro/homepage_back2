from datetime import datetime

from django.db import models

from hbl.models import HBLPlayer, HBLTeam


class TransactionType(models.TextChoices):
    ADD = "Add"
    DROP = "Drop"
    TRADE = "Trade"


class HBLTransaction(models.Model):
    yahoo_id = models.IntegerField(null=True)
    type = models.CharField(
        choices=TransactionType.choices, max_length=5, default=TransactionType.ADD.value
    )
    players = models.ManyToManyField(HBLPlayer, related_name="transactions")
    team = models.ManyToManyField(HBLTeam, related_name="transactions")
    waiver = models.BooleanField(default=False)
    related_transaction = models.OneToOneField(
        "self",
        related_name="corresponding_transaction",
        on_delete=models.CASCADE,
        null=True,
    )
    date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
