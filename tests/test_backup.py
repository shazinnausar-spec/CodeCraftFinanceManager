
# ============================================================
# CodeCraft Finance Manager
# Database Backup and Restore Tests
# ============================================================

import sqlite3

import pytest

from app.database.connection import initialize_database

from app.services.backup_service import (
    create_database_backup,
    validate_database_backup,
    restore_database_backup,
)


def add_category(database_path, name):
    """Insert a category into a test database."""

    connection = sqlite3.connect(database_path)

    try:

        connection.execute(
            """
            INSERT INTO categories (
                name,
                category_type
            )
            VALUES (?, ?)
            """,
            (name, "income")
        )

        connection.commit()

    finally:

        connection.close()


def get_category_names(database_path):
    """Return all category names from a database."""

    connection = sqlite3.connect(database_path)

    try:

        rows = connection.execute(
            "SELECT name FROM categories ORDER BY id"
        ).fetchall()

        return [row[0] for row in rows]

    finally:

        connection.close()


@pytest.fixture
def sample_database(tmp_path):
    """Create an isolated application database."""

    database_path = tmp_path / "finance.db"

    initialize_database(database_path)

    add_category(
        database_path,
        "Salary"
    )

    return database_path


def test_create_database_backup(sample_database, tmp_path):

    backup_path = tmp_path / "backups" / "finance_backup.db"

    result = create_database_backup(
        backup_path,
        db_path=sample_database
    )

    assert result == backup_path
    assert backup_path.exists()

    assert get_category_names(backup_path) == [
        "Salary"
    ]


def test_validate_database_backup(sample_database, tmp_path):

    backup_path = tmp_path / "finance_backup.db"

    create_database_backup(
        backup_path,
        db_path=sample_database
    )

    assert validate_database_backup(backup_path) is True


def test_reject_invalid_database_backup(tmp_path):

    invalid_backup = tmp_path / "invalid_backup.db"

    invalid_backup.write_text(
        "This is not a valid SQLite database."
    )

    with pytest.raises(ValueError):

        validate_database_backup(invalid_backup)


def test_reject_missing_database_backup(tmp_path):

    missing_backup = tmp_path / "missing_backup.db"

    with pytest.raises(FileNotFoundError):

        validate_database_backup(missing_backup)


def test_restore_database_backup(sample_database, tmp_path):

    backup_path = tmp_path / "finance_backup.db"

    # Create a backup containing the original category.
    create_database_backup(
        backup_path,
        db_path=sample_database
    )

    # Add another category to the application database.
    add_category(
        sample_database,
        "Freelance"
    )

    assert get_category_names(sample_database) == [
        "Salary",
        "Freelance"
    ]

    # Restore the original backup.
    result = restore_database_backup(
        backup_path,
        db_path=sample_database
    )

    assert result is True

    # The restored database should contain
    # the original data only.
    assert get_category_names(sample_database) == [
        "Salary"
    ]


def test_restore_rejects_invalid_backup_without_changing_database(
    sample_database,
    tmp_path
):

    invalid_backup = tmp_path / "invalid_backup.db"

    invalid_backup.write_text(
        "Invalid database content."
    )

    original_categories = get_category_names(
        sample_database
    )

    with pytest.raises(ValueError):

        restore_database_backup(
            invalid_backup,
            db_path=sample_database
        )

    # The original database must remain unchanged.
    assert get_category_names(sample_database) == (
        original_categories
    )


def test_backup_rejects_same_source_and_destination(sample_database):

    with pytest.raises(ValueError):

        create_database_backup(
            sample_database,
            db_path=sample_database
        )


def test_restore_rejects_same_source_and_destination(sample_database):

    with pytest.raises(ValueError):

        restore_database_backup(
            sample_database,
            db_path=sample_database
        )
