
# ============================================================
# CodeCraft Finance Manager
# Input Validation Utilities
# ============================================================

from datetime import date

from app.services.money_service import to_decimal


def validate_text(value, field_name, max_length=200):
    """Validate a required text field."""

    # Make sure the value is a string.
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text.")

    # Remove unnecessary spaces.
    cleaned_value = value.strip()

    # Reject empty text.
    if not cleaned_value:
        raise ValueError(f"{field_name} is required.")

    # Check the maximum allowed length.
    if len(cleaned_value) > max_length:
        raise ValueError(
            f"{field_name} cannot exceed {max_length} characters."
        )

    return cleaned_value


def validate_optional_text(value, field_name, max_length=1000):
    """Validate an optional text field."""

    # Convert an empty value into an empty string.
    if value is None:
        return ""

    # Make sure the value is text.
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text.")

    # Remove unnecessary spaces.
    cleaned_value = value.strip()

    # Check the maximum allowed length.
    if len(cleaned_value) > max_length:
        raise ValueError(
            f"{field_name} cannot exceed {max_length} characters."
        )

    return cleaned_value


def validate_amount(amount):
    """Validate a positive financial amount."""

    # Convert the amount safely into Decimal.
    decimal_amount = to_decimal(amount)

    # Amounts must be greater than zero.
    if decimal_amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    return decimal_amount


def validate_transaction_type(transaction_type):
    """Validate income or expense transaction type."""

    # Normalize the supplied type.
    transaction_type = str(transaction_type).strip().lower()

    # Only income and expense are supported.
    if transaction_type not in ("income", "expense"):
        raise ValueError(
            "Transaction type must be income or expense."
        )

    return transaction_type


def validate_date(date_value):
    """
    Validate a date in YYYY-MM-DD format.

    Also rejects impossible dates such as 2026-02-30.
    """

    # Make sure the date is text.
    if not isinstance(date_value, str):
        raise ValueError("Date must be in YYYY-MM-DD format.")

    try:
        # Parse the date.
        parsed_date = date.fromisoformat(date_value)

    except ValueError:
        raise ValueError(
            "Please enter a valid date in YYYY-MM-DD format."
        )

    # Ensure the supplied value uses the expected format.
    if parsed_date.isoformat() != date_value:
        raise ValueError(
            "Date must use YYYY-MM-DD format."
        )

    return date_value
