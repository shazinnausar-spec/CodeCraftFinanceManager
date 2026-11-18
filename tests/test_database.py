
# ============================================================
# CodeCraft Finance Manager
# Database Architecture Tests
# ============================================================

import sqlite3

import pytest

from app.database.connection import (
    get_connection,
    initialize_database,
)


@pytest.fixture
def test_database(tmp_path):
    """Create a temporary database for testing."""

    # Create a temporary database path.
    database_path = tmp_path / "test_finance.db"

    # Initialize the database.
    initialize_database(database_path)

    return database_path


def test_database_tables_created(test_database):
    """Check that all required database tables exist."""

    # Connect to the test database.
    connection = get_connection(test_database)

    # Retrieve all table names.
    tables = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    ).fetchall()

    # Convert the results into a list of names.
    table_names = [row["name"] for row in tables]

    connection.close()

    # Verify the required tables.
    assert "categories" in table_names
    assert "transactions" in table_names
    assert "budgets" in table_names


def test_database_connection_enables_foreign_keys(test_database):
    """Check that foreign key enforcement is enabled."""

    connection = get_connection(test_database)

    result = connection.execute(
        "PRAGMA foreign_keys"
    ).fetchone()

    connection.close()

    assert result[0] == 1


def test_database_category_insert(test_database):
    """Check that a category can be inserted."""

    connection = get_connection(test_database)

    connection.execute(
        """
        INSERT INTO categories (name, category_type)
        VALUES (?, ?)
        """,
        ("Salary", "income"),
    )

    connection.commit()

    category = connection.execute(
        "SELECT * FROM categories WHERE name = ?",
        ("Salary",),
    ).fetchone()

    connection.close()

    assert category is not None
    assert category["name"] == "Salary"
    assert category["category_type"] == "income"


def test_database_rejects_invalid_category_type(test_database):
    """Check that invalid category types are rejected."""

    connection = get_connection(test_database)

    with pytest.raises(sqlite3.IntegrityError):

        connection.execute(
            """
            INSERT INTO categories (name, category_type)
            VALUES (?, ?)
            """,
            ("Invalid", "unknown"),
        )

    connection.close()


def test_database_rejects_invalid_transaction_category(test_database):
    """Check that transactions cannot use missing categories."""

    connection = get_connection(test_database)

    with pytest.raises(sqlite3.IntegrityError):

        connection.execute(
            """
            INSERT INTO transactions (
                title,
                amount_minor,
                transaction_type,
                category_id,
                transaction_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Test transaction", 10000, "income", 9999, "2026-11-16"),
        )

    connection.close()


def test_database_rejects_zero_transaction_amount(test_database):
    """Check that transaction amounts must be positive."""

    connection = get_connection(test_database)

    connection.execute(
        """
        INSERT INTO categories (name, category_type)
        VALUES (?, ?)
        """,
        ("Salary", "income"),
    )

    connection.commit()

    category = connection.execute(
        "SELECT id FROM categories WHERE name = ?",
        ("Salary",),
    ).fetchone()

    with pytest.raises(sqlite3.IntegrityError):

        connection.execute(
            """
            INSERT INTO transactions (
                title,
                amount_minor,
                transaction_type,
                category_id,
                transaction_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Invalid transaction", 0, "income", category["id"], "2026-11-16"),
        )

    connection.close()
