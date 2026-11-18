
# ============================================================
# CodeCraft Finance Manager
# Budget Management Services
# ============================================================

import sqlite3

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from app.database.connection import get_connection

from app.services.money_service import (
    to_decimal,
    to_minor_units,
    from_minor_units,
)


def validate_budget_month(budget_month):
    """
    Validate a budget month.

    Expected format: YYYY-MM
    Example: 2026-11
    """

    if not isinstance(budget_month, str):
        raise ValueError("Please select a valid budget month.")

    try:
        parsed_month = datetime.strptime(
            budget_month,
            "%Y-%m"
        )

    except ValueError:
        raise ValueError(
            "Budget month must use the YYYY-MM format."
        )

    # Ensure the supplied month has exactly the expected format.
    if parsed_month.strftime("%Y-%m") != budget_month:
        raise ValueError(
            "Budget month must use the YYYY-MM format."
        )

    return budget_month


def validate_budget_amount(amount):
    """Validate and convert a budget amount into minor units."""

    decimal_amount = to_decimal(amount)

    if decimal_amount <= 0:
        raise ValueError("Budget amount must be greater than zero.")

    amount_minor = to_minor_units(decimal_amount)

    if amount_minor <= 0:
        raise ValueError(
            "Budget amount must be at least Rs. 0.01."
        )

    return amount_minor


def validate_category_id(category_id):
    """Ensure the category ID is a valid positive integer."""

    if isinstance(category_id, bool):
        raise ValueError("Please select a valid category.")

    try:
        category_id = int(category_id)

    except (ValueError, TypeError):
        raise ValueError("Please select a valid category.")

    if category_id <= 0:
        raise ValueError("Please select a valid category.")

    return category_id


def get_month_date_range(budget_month):
    """
    Return the first day of a month and the first day
    of the following month.

    Example:
    2026-11 returns 2026-11-01 and 2026-12-01.
    """

    budget_month = validate_budget_month(budget_month)

    year, month = map(int, budget_month.split("-"))

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)

    else:
        end_date = date(year, month + 1, 1)

    return start_date.isoformat(), end_date.isoformat()


def _get_expense_category(connection, category_id):
    """
    Retrieve an active expense category.

    New budgets cannot be assigned to income or inactive
    categories.
    """

    category = connection.execute("""
        SELECT *
        FROM categories
        WHERE id = ?
          AND category_type = 'expense'
          AND is_active = 1
    """, (category_id,)).fetchone()

    if category is None:
        raise ValueError(
            "Please select an active expense category."
        )

    return category


def _build_budget_result(row, start_date, end_date, connection):
    """
    Build a budget result containing its spending calculations.
    """

    # Calculate actual expense transactions for this category
    # during the selected budget month.
    spending_result = connection.execute("""
        SELECT COALESCE(SUM(amount_minor), 0) AS spent_minor
        FROM transactions
        WHERE category_id = ?
          AND transaction_type = 'expense'
          AND transaction_date >= ?
          AND transaction_date < ?
    """, (
        row["category_id"],
        start_date,
        end_date,
    )).fetchone()

    # Retrieve the actual amount spent in minor units.
    spent_minor = spending_result["spent_minor"]

    # Retrieve the budget limit.
    budget_minor = row["amount_minor"]

    # Calculate the remaining budget.
    remaining_minor = budget_minor - spent_minor

    # Calculate the percentage of the budget used.
    percentage_used = (
        Decimal(spent_minor) * Decimal("100")
        / Decimal(budget_minor)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # Return the budget information and calculations.
    return {
        "id": row["id"],
        "category_id": row["category_id"],
        "category_name": row["category_name"],
        "category_active": bool(row["category_active"]),
        "budget_month": row["budget_month"],

        "budget_amount": from_minor_units(budget_minor),
        "spent_amount": from_minor_units(spent_minor),
        "remaining_amount": from_minor_units(remaining_minor),

        "percentage_used": percentage_used,
        "is_over_budget": spent_minor > budget_minor,
    }


def create_budget(category_id, budget_month, amount, db_path=None):
    """Create a monthly budget for an expense category."""

    # Validate the supplied information.
    category_id = validate_category_id(category_id)
    budget_month = validate_budget_month(budget_month)
    amount_minor = validate_budget_amount(amount)

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Ensure that the selected category is an active
        # expense category.
        _get_expense_category(connection, category_id)

        # Insert the new budget.
        cursor = connection.execute("""
            INSERT INTO budgets (
                category_id,
                budget_month,
                amount_minor
            )
            VALUES (?, ?, ?)
        """, (
            category_id,
            budget_month,
            amount_minor,
        ))

        # Save the changes.
        connection.commit()

        # Return the newly created budget ID.
        return cursor.lastrowid

    except sqlite3.IntegrityError as error:

        # Handle duplicate budgets and other database
        # integrity errors.
        raise ValueError(
            "A budget already exists for this category and month."
        ) from error

    finally:

        # Close the database connection.
        connection.close()


def get_all_budgets(budget_month, db_path=None):
    """
    Retrieve all budgets for a selected month.

    Includes inactive categories so historical budgets
    remain visible.
    """

    # Validate the selected month.
    budget_month = validate_budget_month(budget_month)

    # Get the date range for the selected month.
    start_date, end_date = get_month_date_range(budget_month)

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Retrieve budgets and their category information.
        rows = connection.execute("""
            SELECT
                budgets.id,
                budgets.category_id,
                budgets.budget_month,
                budgets.amount_minor,
                categories.name AS category_name,
                categories.is_active AS category_active

            FROM budgets

            INNER JOIN categories
                ON budgets.category_id = categories.id

            WHERE budgets.budget_month = ?

            ORDER BY categories.name COLLATE NOCASE
        """, (budget_month,)).fetchall()

        # Calculate spending information for every budget.
        return [
            _build_budget_result(
                row,
                start_date,
                end_date,
                connection
            )
            for row in rows
        ]

    finally:

        # Close the database connection.
        connection.close()


def get_budget(budget_id, db_path=None):
    """Retrieve one budget with its spending calculations."""

    # Validate the budget ID.
    if isinstance(budget_id, bool):
        raise ValueError("Invalid budget ID.")

    try:
        budget_id = int(budget_id)

    except (ValueError, TypeError):
        raise ValueError("Invalid budget ID.")

    if budget_id <= 0:
        raise ValueError("Invalid budget ID.")

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Retrieve the selected budget.
        row = connection.execute("""
            SELECT
                budgets.id,
                budgets.category_id,
                budgets.budget_month,
                budgets.amount_minor,
                categories.name AS category_name,
                categories.is_active AS category_active

            FROM budgets

            INNER JOIN categories
                ON budgets.category_id = categories.id

            WHERE budgets.id = ?
        """, (budget_id,)).fetchone()

        # Reject missing budgets.
        if row is None:
            raise ValueError("Budget was not found.")

        # Calculate the selected month's date range.
        start_date, end_date = get_month_date_range(
            row["budget_month"]
        )

        # Return the complete budget information.
        return _build_budget_result(
            row,
            start_date,
            end_date,
            connection
        )

    finally:

        # Close the database connection.
        connection.close()


def update_budget(budget_id, amount, db_path=None):
    """Update the amount of an existing budget."""

    # Validate the budget ID.
    if isinstance(budget_id, bool):
        raise ValueError("Invalid budget ID.")

    try:
        budget_id = int(budget_id)

    except (ValueError, TypeError):
        raise ValueError("Invalid budget ID.")

    if budget_id <= 0:
        raise ValueError("Invalid budget ID.")

    # Validate the new budget amount.
    amount_minor = validate_budget_amount(amount)

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Update the budget amount.
        cursor = connection.execute("""
            UPDATE budgets

            SET
                amount_minor = ?,
                updated_at = CURRENT_TIMESTAMP

            WHERE id = ?
        """, (
            amount_minor,
            budget_id,
        ))

        # Check whether the budget exists.
        if cursor.rowcount == 0:
            raise ValueError("Budget was not found.")

        # Save the changes.
        connection.commit()

    finally:

        # Close the database connection.
        connection.close()


def delete_budget(budget_id, db_path=None):
    """Delete an existing monthly budget."""

    # Validate the budget ID.
    if isinstance(budget_id, bool):
        raise ValueError("Invalid budget ID.")

    try:
        budget_id = int(budget_id)

    except (ValueError, TypeError):
        raise ValueError("Invalid budget ID.")

    if budget_id <= 0:
        raise ValueError("Invalid budget ID.")

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Delete the selected budget.
        cursor = connection.execute("""
            DELETE FROM budgets
            WHERE id = ?
        """, (budget_id,))

        # Check whether the budget existed.
        if cursor.rowcount == 0:
            raise ValueError("Budget was not found.")

        # Save the changes.
        connection.commit()

    finally:

        # Close the database connection.
        connection.close()
