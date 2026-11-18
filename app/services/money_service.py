
# ============================================================
# CodeCraft Finance Manager
# Money Conversion and Formatting Services
# ============================================================

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from app.services.settings_service import (
    AVAILABLE_CURRENCIES,
    get_setting,
)


# Number of minor units in one LKR.
# LKR 1.00 = 100 minor units.
MINOR_UNITS_PER_RUPEE = Decimal("100")


def to_decimal(amount):
    """
    Convert an amount into Decimal safely.

    Decimal is used instead of float to avoid
    financial rounding problems.
    """

    # Do not accept boolean values as amounts.
    if isinstance(amount, bool):
        raise ValueError("Amount must be a valid number.")

    try:
        # Convert the supplied value into Decimal.
        value = Decimal(str(amount).strip())

    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Please enter a valid amount.")

    # Reject infinity and NaN.
    if not value.is_finite():
        raise ValueError("Amount must be a finite number.")

    # Round to two decimal places.
    return value.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def to_minor_units(amount):
    """
    Convert an LKR amount into integer minor units.

    Example:
    LKR 1250.50 becomes 125050.
    """

    # Convert the amount into Decimal.
    decimal_amount = to_decimal(amount)

    # Multiply by 100 to get minor units.
    minor_amount = decimal_amount * MINOR_UNITS_PER_RUPEE

    # Return the exact integer value.
    return int(minor_amount)


def from_minor_units(amount_minor):
    """
    Convert integer minor units back into Decimal rupees.
    """

    # Reject boolean values.
    if isinstance(amount_minor, bool):
        raise ValueError("Invalid stored amount.")

    # Only integer minor units are accepted.
    if not isinstance(amount_minor, int):
        raise ValueError("Stored amount must be an integer.")

    # Convert the integer into Decimal rupees.
    return Decimal(amount_minor) / MINOR_UNITS_PER_RUPEE


def format_currency(amount, symbol=None):
    """
    Format an amount using the saved LKR display preference.

    Examples:
    LKR 1250.50 becomes LKR 1,250.50.
    Rs. 1250.50 becomes Rs. 1,250.50.

    This function does not perform currency conversion.
    """

    # Convert the supplied amount into Decimal.
    decimal_amount = to_decimal(amount)

    # Use the saved display preference when no symbol
    # has been explicitly supplied.
    if symbol is None:

        currency_preference = get_setting("currency")

        symbol = AVAILABLE_CURRENCIES.get(
            currency_preference,
            "LKR"
        )

    # Format the amount with comma separators.
    formatted_amount = f"{decimal_amount:,.2f}"

    # Return the complete currency string.
    return f"{symbol} {formatted_amount}"
