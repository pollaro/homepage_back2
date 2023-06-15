from datetime import datetime

import factory
from faker import Faker

from hbl.models import (
    HBLManager,
    HBLPlayer,
    HBLTeamAbbreviations,
    HBLTransaction,
    Position,
    TransactionType,
)

faker = Faker()


class HBLManagerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HBLManager

    hbl_id = factory.Sequence(lambda x: "%04d" % x)
    name = factory.LazyAttribute(lambda _: faker.name())
    email = factory.LazyAttribute(lambda _: faker.unique.email())
    guid = factory.LazyAttribute(lambda _: faker.pyint())


class HBLTeamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HBLTeam

    team_id = factory.Sequence(lambda x: "%04d" % x)
    name = factory.Faker(
        "random_element", elements=[x[0] for x in HBLTeamAbbreviations.choices()]
    )
    manager = factory.SubFactory(HBLManagerFactory)
    yahoo_team_key = factory.Sequence(lambda x: "422.l.48574.t.%01d" % x)


class HBLPlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HBLPlayer

    player_id = factory.Sequence(lambda x: "%04d" % x)
    first_name = factory.LazyAttribute(lambda _: faker.first_name())
    last_name = factory.LazyAttribute(lambda _: faker.last_name())
    yahoo_player_key = factory.Sequence(lambda x: "422.p.%05d" % x)
    team_name = factory.LazyAttribute(lambda _: faker.company())
    primary_position = factory.Faker(
        "random_element", elements=[x[0] for x in Position.choices]
    )
    display_positions = factory.SelfAttribute("primary_position")
    player_status = None
    hbl_team = factory.SubFactory(HBLTeamFactory)
    previous_hbl_team = factory.SubFactory(HBLTeamFactory)
    keeper_cost_current = factory.LazyAttribute(
        lambda _: faker.int(min_value=1, max_value=4)
    )
    keeper_cost_next = factory.LazyAttribute(
        lambda _: faker.int(min_value=1, max_value=4)
    )
    seasons_on_team = factory.LazyAttribute(lambda _: faker.int())
    four_keeper_cost = factory.LazyAttribute(lambda _: faker.pybool())


class HBLTransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HBLTransaction

    yahoo_id = factory.Sequence(int)
    type = factory.Faker(
        "random_element", elements=[x[0] for x in TransactionType.choices]
    )
    waiver = factory.LazyAttribute(lambda _: faker.pybool())
    related_transaction = factory.LazyAttribute(lambda _: faker.pyobject())
    date = factory.LazyAttribute(
        lambda _: faker.date_between(
            start_date=datetime(2023, 4, 1), end_date=datetime(2023, 9, 1)
        )
    )

    @factory.post_generation
    def players(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for player in extracted:
                self.players.add(player)

    @factory.post_generation
    def team(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.team.add(extracted)
