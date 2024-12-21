# type: ignore - no stub files

import factory
from faker import Faker

from app.factories.base import MySQLAlchemyModelFactory
from app.models.user import User
from app.schemas.user import UserClassicIn, UserLinkedinIn
from app.utils.strings import make_random_str

fake = Faker()


class ClassicUserBase(factory.Factory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone_number = "06 12 23 34 45"  # TODO: # use fake.phone_number() instead
    password = factory.LazyFunction(lambda: fake.password(length=8))


class ClassicUserFactory(MySQLAlchemyModelFactory, ClassicUserBase):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_session_factory = lambda: MySQLAlchemyModelFactory.get_session()

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> User:
        """Override the factory_boy `_create` method with our custom call."""
        return model_class.register_user(
            user_payload=UserClassicIn(**kwargs),
            session=cls._meta.sqlalchemy_session_factory(),
        )


class ClassicUserDictFactory(factory.DictFactory, ClassicUserBase):
    pass


class UserFactory(ClassicUserFactory):
    pass


class LinkedInUserFactory(MySQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
        sqlalchemy_session_factory = lambda: MySQLAlchemyModelFactory.get_session()

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    linkedin_id = factory.LazyAttribute(lambda _: make_random_str(10))

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> User:
        """Override the factory_boy `_create` method with our custom call."""
        return model_class.register_linkedin_user(
            user_payload=UserLinkedinIn(**kwargs),
            session=cls._meta.sqlalchemy_session_factory(),
        )


class LinkedInProfileDictFactory(factory.DictFactory):
    given_name = factory.Faker("first_name")
    family_name = factory.Faker("last_name")
    email = factory.Faker("email")
    sub = factory.LazyAttribute(lambda _: make_random_str(10))
