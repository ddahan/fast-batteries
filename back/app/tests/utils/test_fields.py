from decimal import Decimal

import pytest
from pydantic import BaseModel, SecretStr, ValidationError

from app.utils.fields import Password, Percentage, Price


class PriceModel(BaseModel):
    price: Price


class TestPrice:
    def test_valid_price(self):
        model = PriceModel(price=Decimal("1234.56"))
        assert model.price == Decimal("1234.56")

    def test_invalid_price_negative(self):
        with pytest.raises(ValidationError):
            PriceModel(price=Decimal("-1.00"))

    def test_invalid_price_exceeds_max_digits(self):
        with pytest.raises(ValidationError):
            PriceModel(price=Decimal("123456789.00"))

    def test_invalid_price_exceeds_decimal_places(self):
        with pytest.raises(ValidationError):
            PriceModel(price=Decimal("1234.567"))


# Tests for Percentage
class PercentageModel(BaseModel):
    percentage: Percentage


class TestPercentage:
    def test_valid_percentage_float(self):
        model = PercentageModel(percentage=50.0)
        assert model.percentage == 50.0

    def test_valid_percentage_int(self):
        model = PercentageModel(percentage=50)
        assert model.percentage == 50.0

    def test_invalid_percentage_negative(self):
        with pytest.raises(ValidationError):
            PercentageModel(percentage=-1.0)

    def test_invalid_percentage_exceeds_100(self):
        with pytest.raises(ValidationError):
            PercentageModel(percentage=101.0)


# Tests for Password


class PasswordModel(BaseModel):
    password: Password


class TestPassword:
    def test_valid_password(self):
        model = PasswordModel(password=SecretStr("securepassword123"))
        assert model.password.get_secret_value() == "securepassword123"

    def test_invalid_password_too_short(self):
        with pytest.raises(ValidationError):
            PasswordModel(password=SecretStr("short"))

    def test_invalid_password_too_long(self):
        with pytest.raises(ValidationError):
            PasswordModel(password=SecretStr("a" * 41))

    def test_password_handling(self):
        model = PasswordModel(password=SecretStr("securepassword123"))
        assert model.password.get_secret_value() == "securepassword123"
        assert str(model.password) == "**********"  # SecretStr masks the value
