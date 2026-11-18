
# ============================================================
# CodeCraft Finance Manager
# Database Backup and Restore Service
# ============================================================

import os
import sqlite3
import tempfile

from pathlib import Path

from config import DATABASE_PATH


# Required tables and columns for this application.
REQUIRED_TABLES = {
    "categories": {
        "id",
        "name",
        "category_type",
        "is_active",
        "created_at",
    },
    "transactions": {
        "id",
        "title",
        "amount_minor",
        "transaction_type",
        "category_id",
        "transaction_date",
        "payment_method",
        "notes",
        "created_at",
        "updated_at",
    },
    "budgets": {
        "id",
        "category_id",
        "budget_month",
        "amount_minor",
        "created_at",
        "updated_at",
    },
}


def _validate_database_file(database_path):
    """
    Check whether a SQLite file is a valid
    CodeCraft Finance Manager database.
    """

    database_path = Path(database_path)

    if not database_path.exists():
        raise FileNotFoundError(
            "The database file does not exist."
        )

    if not database_path.is_file():
        raise ValueError(
            "The selected path is not a database file."
        )

    try:

        connection = sqlite3.connect(
            str(database_path)
        )

        try:

            # Check SQLite database integrity.
            integrity_result = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            if (
                integrity_result is None
                or integrity_result[0] != "ok"
            ):
                raise ValueError(
                    "The database failed its integrity check."
                )

            # Get all existing table names.
            existing_tables = {
                row[0]
                for row in connection.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                """).fetchall()
            }

            # Make sure every required table exists.
            for table_name, required_columns in REQUIRED_TABLES.items():

                if table_name not in existing_tables:
                    raise ValueError(
                        f"Missing required table: {table_name}"
                    )

                # Read the columns of the current table.
                existing_columns = {
                    row[1]
                    for row in connection.execute(
                        f"PRAGMA table_info({table_name})"
                    ).fetchall()
                }

                # Make sure every required column exists.
                missing_columns = (
                    required_columns - existing_columns
                )

                if missing_columns:
                    raise ValueError(
                        f"Missing columns in {table_name}: "
                        f"{', '.join(sorted(missing_columns))}"
                    )

        finally:

            connection.close()

    except sqlite3.DatabaseError as error:

        raise ValueError(
            "The selected file is not a valid SQLite database."
        ) from error

    return True


def validate_database_backup(backup_path):
    """
    Public function to validate a backup file.
    """

    return _validate_database_file(backup_path)


def _create_database_snapshot(source_path, destination_path):
    """
    Create a consistent SQLite snapshot using
    SQLite's built-in backup API.
    """

    source_connection = sqlite3.connect(
        str(source_path)
    )

    destination_connection = sqlite3.connect(
        str(destination_path)
    )

    try:

        source_connection.backup(
            destination_connection
        )

        destination_connection.commit()

    finally:

        destination_connection.close()
        source_connection.close()


def create_database_backup(
    backup_path,
    db_path=None
):
    """
    Create a database backup at the selected location.

    The backup is first created as a temporary file.
    It replaces the destination only after validation.
    """

    source_path = Path(
        db_path if db_path else DATABASE_PATH
    ).resolve()

    destination_path = Path(
        backup_path
    ).resolve()

    if not source_path.exists():
        raise FileNotFoundError(
            "The application database does not exist."
        )

    if source_path == destination_path:
        raise ValueError(
            "The backup destination cannot be the original database."
        )

    # Make sure the destination folder exists.
    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create a temporary file beside the destination.
    temporary_file = None

    try:

        file_descriptor, temporary_path = tempfile.mkstemp(
            prefix=f".{destination_path.stem}_",
            suffix=".tmp",
            dir=destination_path.parent
        )

        os.close(file_descriptor)

        temporary_file = Path(temporary_path)

        # Create the database snapshot.
        _create_database_snapshot(
            source_path,
            temporary_file
        )

        # Validate the completed backup.
        _validate_database_file(
            temporary_file
        )

        # Replace the destination only after validation.
        os.replace(
            temporary_file,
            destination_path
        )

    finally:

        # Remove any leftover temporary file.
        if (
            temporary_file is not None
            and temporary_file.exists()
        ):
            temporary_file.unlink()

    return destination_path


def restore_database_backup(
    backup_path,
    db_path=None
):
    """
    Restore application data from a valid backup.

    The original database is not replaced until
    the restored temporary database passes validation.
    """

    backup_source = Path(
        backup_path
    ).resolve()

    destination_path = Path(
        db_path if db_path else DATABASE_PATH
    ).resolve()

    if backup_source == destination_path:
        raise ValueError(
            "The backup file and application database cannot be the same file."
        )

    # Validate the selected backup before restoring.
    _validate_database_file(
        backup_source
    )

    # Make sure the destination directory exists.
    destination_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_file = None

    try:

        # Create a temporary database beside the original.
        file_descriptor, temporary_path = tempfile.mkstemp(
            prefix=f".{destination_path.stem}_restore_",
            suffix=".tmp",
            dir=destination_path.parent
        )

        os.close(file_descriptor)

        temporary_file = Path(temporary_path)

        # Copy the backup into the temporary database.
        _create_database_snapshot(
            backup_source,
            temporary_file
        )

        # Validate the restored database.
        _validate_database_file(
            temporary_file
        )

        # Replace the application database only now.
        os.replace(
            temporary_file,
            destination_path
        )

    finally:

        # Clean up temporary files if necessary.
        if (
            temporary_file is not None
            and temporary_file.exists()
        ):
            temporary_file.unlink()

    return True
