
# ============================================================
# CodeCraft Finance Manager
# Transaction Management and Financial Summary Services
# ============================================================

import sqlite3

from datetime import date
from decimal import Decimal

from app.database.connection import get_connection

from app.services.money_service import (
    to_minor_units,
    from_minor_units,
)

from app.utils.validators import (
    validate_text,
    validate_optional_text,
    validate_amount,
    validate_transaction_type,
    validate_date,
)


def _validate_category(connection, category_id, transaction_type):
    """Check whether a category exists and matches the transaction."""

    # Retrieve the requested category.
    category = connection.execute("""
        SELECT id, category_type, is_active
        FROM categories
        WHERE id = ?
    """, (category_id,)).fetchone()

    # Reject categories that do not exist.
    if category is None:
        raise ValueError("Selected category does not exist.")

    # Reject inactive categories.
    if category["is_active"] != 1:
        raise ValueError("Selected category is inactive.")

    # Ensure the category matches income or expense.
    if category["category_type"] != transaction_type:
        raise ValueError(
            "Selected category does not match the transaction type."
        )


def _transaction_to_dict(row):
    """Convert a database transaction into a Python dictionary."""

    # Convert the SQLite row into a dictionary.
    transaction = dict(row)

    # Convert stored minor units into Decimal rupees.
    transaction["amount"] = from_minor_units(
        transaction["amount_minor"]
    )

    return transaction


def create_transaction(
    title,
    amount,
    transaction_type,
    category_id,
    transaction_date,
    payment_method,
    notes="",
    db_path=None,
):
    """Create a new income or expense transaction."""

    # Validate the transaction title.
    title = validate_text(title, "Transaction title", 200)

    # Validate the transaction amount.
    amount = validate_amount(amount)

    # Validate the transaction type.
    transaction_type = validate_transaction_type(transaction_type)

    # Validate the transaction date.
    transaction_date = validate_date(transaction_date)

    # Validate the payment method.
    payment_method = validate_text(
        payment_method,
        "Payment method",
        100
    )

    # Validate optional notes.
    notes = validate_optional_text(notes, "Notes")

    # Convert rupees into integer minor units.
    amount_minor = to_minor_units(amount)

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Check whether the selected category is valid.
        _validate_category(
            connection,
            category_id,
            transaction_type
        )

        # Insert the transaction into the database.
        cursor = connection.execute("""
            INSERT INTO transactions (
                title,
                amount_minor,
                transaction_type,
                category_id,
                transaction_date,
                payment_method,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            amount_minor,
            transaction_type,
            category_id,
            transaction_date,
            payment_method,
            notes,
        ))

        # Save the transaction.
        connection.commit()

        # Return the new transaction ID.
        return cursor.lastrowid

    finally:

        # Close the connection.
        connection.close()


def get_transaction(transaction_id, db_path=None):
    """Retrieve one transaction using its ID."""

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Retrieve the transaction and its category name.
        row = connection.execute("""
            SELECT
                transactions.*,
                categories.name AS category_name
            FROM transactions
            JOIN categories
                ON transactions.category_id = categories.id
            WHERE transactions.id = ?
        """, (transaction_id,)).fetchone()

        # Return None if the transaction does not exist.
        if row is None:
            return None

        # Return the transaction with a Decimal amount.
        return _transaction_to_dict(row)

    finally:

        # Close the connection.
        connection.close()


def get_all_transactions(
    transaction_type=None,
    category_id=None,
    start_date=None,
    end_date=None,
    search=None,
    db_path=None,
):
    """Retrieve transactions with optional filters."""

    # Validate the transaction type when supplied.
    if transaction_type is not None:
        transaction_type = validate_transaction_type(transaction_type)

    # Validate the date filters.
    if start_date is not None:
        start_date = validate_date(start_date)

    if end_date is not None:
        end_date = validate_date(end_date)

    # Ensure the date range is valid.
    if start_date and end_date and start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    # Validate the search text when supplied.
    if search is not None:
        search = validate_optional_text(search, "Search", 200)

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Start the query with category information.
        query = """
            SELECT
                transactions.*,
                categories.name AS category_name
            FROM transactions
            JOIN categories
                ON transactions.category_id = categories.id
            WHERE 1 = 1
        """

        # Keep SQL parameters separate from the query.
        parameters = []

        # Filter by income or expense.
        if transaction_type is not None:
            query += " AND transactions.transaction_type = ?"
            parameters.append(transaction_type)

        # Filter by category.
        if category_id is not None:
            query += " AND transactions.category_id = ?"
            parameters.append(category_id)

        # Filter from a starting date.
        if start_date is not None:
            query += " AND transactions.transaction_date >= ?"
            parameters.append(start_date)

        # Filter until an ending date.
        if end_date is not None:
            query += " AND transactions.transaction_date <= ?"
            parameters.append(end_date)

        # Search transaction titles and notes.
        if search:
            query += """
                AND (
                    transactions.title LIKE ?
                    OR transactions.notes LIKE ?
                    OR categories.name LIKE ?
                )
            """

            search_value = f"%{search}%"

            parameters.extend([
                search_value,
                search_value,
                search_value,
            ])

        # Show the newest transactions first.
        query += """
            ORDER BY
                transactions.transaction_date DESC,
                transactions.id DESC
        """

        # Execute the query.
        rows = connection.execute(
            query,
            parameters
        ).fetchall()

        # Convert each row into a dictionary.
        return [
            _transaction_to_dict(row)
            for row in rows
        ]

    finally:

        # Close the database connection.
        connection.close()


def update_transaction(
    transaction_id,
    title,
    amount,
    transaction_type,
    category_id,
    transaction_date,
    payment_method,
    notes="",
    db_path=None,
):
    """Update an existing transaction."""

    # Validate all supplied transaction fields.
    title = validate_text(title, "Transaction title", 200)

    amount = validate_amount(amount)

    transaction_type = validate_transaction_type(
        transaction_type
    )

    transaction_date = validate_date(transaction_date)

    payment_method = validate_text(
        payment_method,
        "Payment method",
        100
    )

    notes = validate_optional_text(notes, "Notes")

    # Convert the amount into integer minor units.
    amount_minor = to_minor_units(amount)

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Check whether the transaction exists.
        existing = connection.execute("""
            SELECT id
            FROM transactions
            WHERE id = ?
        """, (transaction_id,)).fetchone()

        if existing is None:
            raise ValueError("Transaction was not found.")

        # Check the selected category.
        _validate_category(
            connection,
            category_id,
            transaction_type
        )

        # Update the transaction.
        connection.execute("""
            UPDATE transactions
            SET
                title = ?,
                amount_minor = ?,
                transaction_type = ?,
                category_id = ?,
                transaction_date = ?,
                payment_method = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            title,
            amount_minor,
            transaction_type,
            category_id,
            transaction_date,
            payment_method,
            notes,
            transaction_id,
        ))

        # Save the updated transaction.
        connection.commit()

    finally:

        # Close the connection.
        connection.close()


def delete_transaction(transaction_id, db_path=None):
    """Delete a transaction using its ID."""

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Delete the requested transaction.
        cursor = connection.execute("""
            DELETE FROM transactions
            WHERE id = ?
        """, (transaction_id,))

        # Check whether a transaction was deleted.
        if cursor.rowcount == 0:
            raise ValueError("Transaction was not found.")

        # Save the deletion.
        connection.commit()

    finally:

        # Close the connection.
        connection.close()


def get_financial_summary(
    start_date=None,
    end_date=None,
    db_path=None,
):
    """
    Calculate income, expenses, and balance
    from actual saved transactions.
    """

    # Validate optional date filters.
    if start_date is not None:
        start_date = validate_date(start_date)

    if end_date is not None:
        end_date = validate_date(end_date)

    # Check the date range.
    if start_date and end_date and start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Build the financial summary query.
        query = """
            SELECT

                COALESCE(
                    SUM(
                        CASE
                            WHEN transaction_type = 'income'
                            THEN amount_minor
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_income,

                COALESCE(
                    SUM(
                        CASE
                            WHEN transaction_type = 'expense'
                            THEN amount_minor
                            ELSE 0
                        END
                    ),
                    0
                ) AS total_expenses

            FROM transactions

            WHERE 1 = 1
        """

        # Store filter values.
        parameters = []

        # Apply the starting date.
        if start_date is not None:
            query += " AND transaction_date >= ?"
            parameters.append(start_date)

        # Apply the ending date.
        if end_date is not None:
            query += " AND transaction_date <= ?"
            parameters.append(end_date)

        # Execute the summary query.
        result = connection.execute(
            query,
            parameters
        ).fetchone()

        # Convert integer minor units into Decimal.
        total_income = from_minor_units(
            result["total_income"]
        )

        total_expenses = from_minor_units(
            result["total_expenses"]
        )

        # Calculate the net balance for the selected period.
        balance = total_income - total_expenses

        # Return the financial summary.
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": balance,
            "total_transactions": connection.execute("""
                SELECT COUNT(*) AS total
                FROM transactions
                WHERE 1 = 1
            """ + (
                " AND transaction_date >= ?"
                if start_date is not None else ""
            ) + (
                " AND transaction_date <= ?"
                if end_date is not None else ""
            ), parameters).fetchone()["total"],
        }

    finally:

        # Close the connection.
        connection.close()
