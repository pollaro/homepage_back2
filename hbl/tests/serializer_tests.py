from datetime import datetime
from unittest import TestCase

from hbl.serializers import TransactionSerializer
from hbl.tests.factories import HBLPlayerFactory, HBLTeamFactory, HBLTransactionFactory


class TransactionSerializerTestCase(TestCase):
    def setUp(self):
        self.team1 = HBLTeamFactory()
        self.player1 = HBLPlayerFactory(hbl_team=self.team1)

        self.add_attributes = {
            "yahoo_id": 342,
            "type": "add",
            "players": (self.player1,),
            "team": (self.team1,),
            "waiver": False,
            "related_transaction": None,
            "date": datetime(2022, 1, 1),
            "created": datetime(2022, 1, 1, 0, 0, 0, 0),
            "updated": datetime(2022, 1, 1, 0, 0, 0, 0),
        }

        self.transaction = HBLTransactionFactory(**self.add_attributes)
        self.transaction_serializer = TransactionSerializer(instance=self.transaction)

    def test_contains_expected_fields(self):
        data = self.transaction_serializer.data
        self.assertEqual(
            set(data.keys()),
            {
                "yahoo_id",
                "type",
                "players",
                "team",
                "waiver",
                "related_transaction",
                "date",
                "created",
                "updated",
            },
        )
