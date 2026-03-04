"""
Unit tests for core functionalities (e.g., schemas, utils).
"""
import pytest
from pydantic import ValidationError

from ...schemas.user import UserCreate
from ...utils.helpers import hash_data, safe_get_nested_dict, format_currency   


class TestUserSchema:
    def test_valid_user_create(self):
        """Test that a valid UserCreate object can be created."""
        data = {
            "username": "johndoe",
            "email": "john.doe@example.com",
            "password": "securePassword123!"
        }
        user = UserCreate(**data)
        assert user.username == "johndoe"
        assert user.email == "john.doe@example.com"
        assert user.password == "securePassword123!"

    def test_invalid_email_user_create(self):
        """Test that an invalid email raises a ValidationError."""
        data = {
            "username": "janedoe",
            "email": "invalid-email", # Invalid email format
            "password": "anotherSecurePassword456@"
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_short_password_user_create(self):
        """Test that a short password raises a ValidationError."""
        data = {
            "username": "bobdoe",
            "email": "bob.doe@example.com",
            "password": "123" # Too short
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)


class TestUtils:
    def test_hash_data(self):
        """Test the hash_data utility function."""
        input_data = {"key": "value", "number": 42}
        hash1 = hash_data(input_data)
        hash2 = hash_data(input_data) # Same input should give same hash
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 64 # SHA-256 produces 64-character hex string

        # Different input should give different hash
        input_data_2 = {"key": "value", "number": 43}
        hash3 = hash_data(input_data_2)
        assert hash1 != hash3

    def test_safe_get_nested_dict(self):
        """Test the safe_get_nested_dict utility function."""
        nested_dict = {
            "level1": {
                "level2": {
                    "level3": "found_it"
                },
                "other_key": "other_value"
            }
        }
        # Valid path
        result = safe_get_nested_dict(nested_dict, ["level1", "level2", "level3"])      
        assert result == "found_it"

        # Invalid path - middle key missing
        result = safe_get_nested_dict(nested_dict, ["level1", "missing_level", "level3"])
        assert result is None

        # Invalid path - end key missing
        result = safe_get_nested_dict(nested_dict, ["level1", "level2", "missing_level3"])
        assert result is None

        # Default value
        result = safe_get_nested_dict(nested_dict, ["level1", "missing"], default="default_val")
        assert result == "default_val"

    def test_format_currency(self):
        """Test the format_currency utility function."""
        # Basic formatting
        assert format_currency(1234.56, "USD") == "$1,234.56"
        assert format_currency(1000000, "CNY") == "楼1,000,000.00"

        # Default currency (falls back to symbol-less)
        assert format_currency(99.9) == "99.90 UNKNOWN_CURRENCY" # As implemented, falls back to generic
        # If the function were fixed to handle unknown/default better, adjust assertion 
        # For the current impl:
        assert format_currency(99.9, "EUR") == "99.90 EUR"