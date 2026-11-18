
# ============================================================
# CodeCraft Finance Manager
# Category Management Services
# ============================================================

import sqlite3

from app.database.connection import get_connection

from app.utils.validators import (
    validate_text,
    validate_transaction_type,
)


def create_category(name, category_type, db_path=None):
    """Create a new income or expense category."""

    # Validate the category name.
    name = validate_text(name, "Category name", 100)

    # Validate the category type.
    category_type = validate_transaction_type(category_type)

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Insert the category using parameterized SQL.
        cursor = connection.execute("""
            INSERT INTO categories (name, category_type)
            VALUES (?, ?)
        """, (name, category_type))

        # Save the changes.
        connection.commit()

        # Return the new category ID.
        return cursor.lastrowid

    except sqlite3.IntegrityError as error:

        # Convert duplicate-name errors into a readable message.
        raise ValueError(
            "A category with this name and type already exists."
        ) from error

    finally:

        # Close the connection.
        connection.close()


def get_all_categories(
    category_type=None,
    include_inactive=False,
    db_path=None
):
    """Retrieve categories, optionally filtered by type."""

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Start building the SQL query.
        query = "SELECT * FROM categories WHERE 1 = 1"

        # Store SQL parameters separately.
        parameters = []

        # Apply the category type filter when provided.
        if category_type is not None:

            category_type = validate_transaction_type(category_type)

            query += " AND category_type = ?"
            parameters.append(category_type)

        # Hide inactive categories by default.
        if not include_inactive:
            query += " AND is_active = 1"

        # Sort categories alphabetically.
        query += " ORDER BY name COLLATE NOCASE"

        # Execute the query.
        rows = connection.execute(
            query,
            parameters
        ).fetchall()

        # Return ordinary dictionaries.
        return [dict(row) for row in rows]

    finally:

        # Close the connection.
        connection.close()


def update_category(category_id, name, db_path=None):
    """Rename an existing category."""

    # Validate the category name.
    name = validate_text(name, "Category name", 100)

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Update the category name.
        cursor = connection.execute("""
            UPDATE categories
            SET name = ?
            WHERE id = ? AND is_active = 1
        """, (name, category_id))

        # Reject missing or inactive categories.
        if cursor.rowcount == 0:
            raise ValueError("Category was not found or is inactive.")

        # Save the changes.
        connection.commit()

    except sqlite3.IntegrityError as error:

        # Prevent duplicate names within the same category type.
        raise ValueError(
            "A category with this name and type already exists."
        ) from error

    finally:

        # Close the connection.
        connection.close()


def deactivate_category(category_id, db_path=None):
    """Deactivate a category without deleting its history."""

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Mark the category as inactive.
        cursor = connection.execute("""
            UPDATE categories
            SET is_active = 0
            WHERE id = ? AND is_active = 1
        """, (category_id,))

        # Check whether the category existed.
        if cursor.rowcount == 0:
            raise ValueError("Category was not found or is inactive.")

        # Save the changes.
        connection.commit()

    finally:

        # Close the connection.
        connection.close()
