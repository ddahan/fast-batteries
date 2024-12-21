# type: ignore - no stub files

import random
from datetime import datetime, timedelta

import factory
from faker import Faker

from app.factories.base import MySQLAlchemyModelFactory
from app.models.badge import Badge

fake = Faker()


class BadgeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Badge
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_session_factory = lambda: MySQLAlchemyModelFactory.get_session()

    owner = factory.SubFactory("app.factories.user.UserFactory")
    owner_id = factory.SelfAttribute("owner.id")
    expire_at = factory.LazyAttribute(
        lambda _: datetime.now() + timedelta(days=random.randint(-100, 500))
    )
    is_active = True
