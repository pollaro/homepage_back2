from collections import defaultdict

from rest_framework import serializers

from hbl.models import (
    HBLManager,
    HBLTeam,
    HBLTeamAbbreviations,
    HBLTransaction,
    TransactionType,
)
from hbl.models.players import HBLPlayer, HBLProspect


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HBLManager
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer()
    name = serializers.ChoiceField(choices=HBLTeamAbbreviations.choices())

    class Meta:
        model = HBLTeam
        fields = "__all__"

    def create(self, validated_data):
        manager_data = validated_data.pop("manager")
        team = HBLTeam.objects.create(**validated_data)
        manager = HBLManager.objects.create(**manager_data)
        return team


class PlayerSerializer(serializers.ModelSerializer):
    hbl_team = TeamSerializer()
    previous_hbl_team = TeamSerializer()
    yahoo_player_id = serializers.IntegerField(source="player_id")
    yahoo_player_key = serializers.CharField(source="player_key")
    first_name = serializers.CharField(source="name.first")
    last_name = serializers.CharField(source="name.last")
    team_name = serializers.CharField(source="editorial_team_abbr", max_length=3)
    display_positions = serializers.CharField(source="display_position")
    player_status = serializers.CharField(required=False)

    class Meta:
        model = HBLPlayer
        fields = "__all__"


class ProspectSerializer(serializers.ModelSerializer):
    hbl_team = TeamSerializer()
    player_status = serializers.CharField(required=False)

    class Meta:
        model = HBLProspect
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    yahoo_id = serializers.IntegerField(source="transaction_id")
    type = serializers.ChoiceField(choices=TransactionType.choices)
    player = PlayerSerializer(many=True)
    team = TeamSerializer()
    related_transaction = serializers.PrimaryKeyRelatedField(
        queryset=HBLTransaction.objects.all()
    )

    class Meta:
        model = HBLTransaction
        fields = "__all__"
