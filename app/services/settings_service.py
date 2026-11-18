
# ============================================================
# CodeCraft Finance Manager
# Application Settings Service
# ============================================================

import json

from config import DATA_DIR


# ------------------------------------------------------------
# DEFAULT SETTINGS
# ------------------------------------------------------------

DEFAULT_SETTINGS = {
    "currency": "LKR",
    "appearance": "light",
}


# ------------------------------------------------------------
# AVAILABLE SETTINGS
# ------------------------------------------------------------

# Both options represent the same underlying LKR currency.
# They only change how amounts are displayed.
AVAILABLE_CURRENCIES = {
    "LKR": "LKR",
    "Rs.": "Rs.",
}

AVAILABLE_APPEARANCES = [
    "light",
    "dark",
    "system",
]


# Settings file location.
SETTINGS_FILE = DATA_DIR / "settings.json"


# ------------------------------------------------------------
# LOAD SETTINGS
# ------------------------------------------------------------

def load_settings():
    """
    Load application settings from the JSON file.

    If the file does not exist or contains invalid data,
    default settings are returned.
    """

    settings = DEFAULT_SETTINGS.copy()

    try:

        if not SETTINGS_FILE.exists():
            return settings

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as settings_file:

            saved_settings = json.load(settings_file)

        if not isinstance(saved_settings, dict):
            return settings

        currency = saved_settings.get("currency")
        appearance = saved_settings.get("appearance")

        if (
            isinstance(currency, str)
            and currency in AVAILABLE_CURRENCIES
        ):
            settings["currency"] = currency

        if (
            isinstance(appearance, str)
            and appearance in AVAILABLE_APPEARANCES
        ):
            settings["appearance"] = appearance

    except (OSError, json.JSONDecodeError):
        return settings

    return settings


# ------------------------------------------------------------
# SAVE SETTINGS
# ------------------------------------------------------------

def save_settings(currency=None, appearance=None):
    """
    Save application settings.

    Unspecified values retain their existing settings.
    """

    current_settings = load_settings()

    if currency is not None:

        if (
            not isinstance(currency, str)
            or currency not in AVAILABLE_CURRENCIES
        ):
            raise ValueError("Unsupported currency display preference.")

        current_settings["currency"] = currency

    if appearance is not None:

        if (
            not isinstance(appearance, str)
            or appearance not in AVAILABLE_APPEARANCES
        ):
            raise ValueError("Unsupported appearance preference.")

        current_settings["appearance"] = appearance

    # Ensure the data directory exists.
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Write the updated settings.
    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as settings_file:

        json.dump(
            current_settings,
            settings_file,
            indent=4
        )

    return current_settings


# ------------------------------------------------------------
# RESET SETTINGS
# ------------------------------------------------------------

def reset_settings():
    """
    Restore all application preferences to their defaults.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as settings_file:

        json.dump(
            DEFAULT_SETTINGS,
            settings_file,
            indent=4
        )

    return DEFAULT_SETTINGS.copy()


# ------------------------------------------------------------
# GET ONE SETTING
# ------------------------------------------------------------

def get_setting(setting_name):
    """
    Return the value of one saved setting.
    """

    settings = load_settings()

    if setting_name not in settings:
        raise ValueError("Unknown application setting.")

    return settings[setting_name]
