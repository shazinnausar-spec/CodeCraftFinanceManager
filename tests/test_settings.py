
# ============================================================
# CodeCraft Finance Manager
# Application Settings Tests
# ============================================================

import json

import pytest

import app.services.settings_service as settings_service

from app.services.money_service import format_currency


@pytest.fixture
def settings_environment(tmp_path, monkeypatch):
    """Create an isolated settings environment for testing."""

    data_directory = tmp_path / "data"
    settings_file = data_directory / "settings.json"

    monkeypatch.setattr(
        settings_service,
        "DATA_DIR",
        data_directory
    )

    monkeypatch.setattr(
        settings_service,
        "SETTINGS_FILE",
        settings_file
    )

    return settings_file


# ------------------------------------------------------------
# LOAD SETTINGS TESTS
# ------------------------------------------------------------

def test_load_default_settings(settings_environment):

    settings = settings_service.load_settings()

    assert settings == {
        "currency": "LKR",
        "appearance": "light",
    }


def test_load_saved_settings(settings_environment):

    settings_service.save_settings(
        currency="Rs.",
        appearance="dark"
    )

    settings = settings_service.load_settings()

    assert settings["currency"] == "Rs."
    assert settings["appearance"] == "dark"


def test_load_settings_with_invalid_values(settings_environment):

    settings_environment.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        settings_environment,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "currency": ["invalid"],
                "appearance": {"invalid": True},
            },
            file
        )

    settings = settings_service.load_settings()

    assert settings == {
        "currency": "LKR",
        "appearance": "light",
    }


def test_load_settings_with_unsupported_currency(settings_environment):

    settings_environment.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        settings_environment,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "currency": "USD",
                "appearance": "dark",
            },
            file
        )

    settings = settings_service.load_settings()

    assert settings["currency"] == "LKR"
    assert settings["appearance"] == "dark"


def test_load_corrupted_settings_file(settings_environment):

    settings_environment.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    settings_environment.write_text(
        "{ invalid json",
        encoding="utf-8"
    )

    settings = settings_service.load_settings()

    assert settings == {
        "currency": "LKR",
        "appearance": "light",
    }


# ------------------------------------------------------------
# SAVE SETTINGS TESTS
# ------------------------------------------------------------

def test_save_settings(settings_environment):

    settings = settings_service.save_settings(
        currency="Rs.",
        appearance="dark"
    )

    assert settings == {
        "currency": "Rs.",
        "appearance": "dark",
    }

    assert settings_environment.exists()


def test_save_partial_settings(settings_environment):

    settings_service.save_settings(
        currency="Rs.",
        appearance="dark"
    )

    updated_settings = settings_service.save_settings(
        currency="LKR"
    )

    assert updated_settings == {
        "currency": "LKR",
        "appearance": "dark",
    }


def test_reject_invalid_currency(settings_environment):

    with pytest.raises(ValueError):

        settings_service.save_settings(
            currency="INVALID"
        )


def test_reject_foreign_currency(settings_environment):

    for currency in ["USD", "EUR", "GBP"]:

        with pytest.raises(ValueError):

            settings_service.save_settings(
                currency=currency
            )


def test_reject_invalid_appearance(settings_environment):

    with pytest.raises(ValueError):

        settings_service.save_settings(
            appearance="invalid"
        )


def test_reject_wrong_data_types(settings_environment):

    with pytest.raises(ValueError):

        settings_service.save_settings(
            currency=["LKR"]
        )

    with pytest.raises(ValueError):

        settings_service.save_settings(
            appearance={"mode": "dark"}
        )


# ------------------------------------------------------------
# RESET SETTINGS TESTS
# ------------------------------------------------------------

def test_reset_settings(settings_environment):

    settings_service.save_settings(
        currency="Rs.",
        appearance="dark"
    )

    settings = settings_service.reset_settings()

    assert settings == {
        "currency": "LKR",
        "appearance": "light",
    }

    assert settings_service.load_settings() == settings


# ------------------------------------------------------------
# GET SETTING TESTS
# ------------------------------------------------------------

def test_get_setting(settings_environment):

    settings_service.save_settings(
        currency="Rs."
    )

    assert settings_service.get_setting("currency") == "Rs."


def test_get_unknown_setting(settings_environment):

    with pytest.raises(ValueError):

        settings_service.get_setting("unknown_setting")


# ------------------------------------------------------------
# CURRENCY FORMATTING TESTS
# ------------------------------------------------------------

def test_format_currency_uses_lkr_preference(settings_environment):

    settings_service.save_settings(
        currency="LKR"
    )

    assert format_currency("1500.50") == "LKR 1,500.50"


def test_format_currency_uses_rupee_preference(settings_environment):

    settings_service.save_settings(
        currency="Rs."
    )

    assert format_currency("1500.50") == "Rs. 1,500.50"


def test_format_currency_defaults_to_lkr(settings_environment):

    assert format_currency("1500.50") == "LKR 1,500.50"


def test_format_currency_keeps_amount_unchanged(settings_environment):

    settings_service.save_settings(
        currency="Rs."
    )

    result = format_currency("250000.75")

    assert result == "Rs. 250,000.75"
