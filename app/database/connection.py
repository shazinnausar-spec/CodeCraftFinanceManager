
# ============================================================
# CodeCraft Finance Manager
# Database Connection and Initialization
# ============================================================

import sqlite3

from pathlib import Path

from config import DATABASE_PATH


def get_connection(db_path=None):
    """
    Create and return a connection to the SQLite database.

    An optional database path is supported so that tests
    can use temporary databases without touching real data.
    """

    # Use the supplied path or the application's default path.
    database_path = Path(db_path) if db_path else DATABASE_PATH

    # Make sure the database directory exists.
    database_path.parent.mkdir(parents=True, exist_ok=True)

    # Open the SQLite database connection.
    connection = sqlite3.connect(database_path)

    # Return database rows as dictionary-like objects.
    connection.row_factory = sqlite3.Row

    # Enable foreign key relationships.
    connection.execute("PRAGMA foreign_keys = ON")

    # Return the ready-to-use connection.
    return connection


def initialize_database(db_path=None):
    """
    Create all application database tables if they
    do not already exist.
    """

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Execute all database table creation statements.
        connection.executescript("""

            -- =================================================
            -- CATEGORIES TABLE
            -- Stores income and expense categories.
            -- =================================================

            CREATE TABLE IF NOT EXISTS categories (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                category_type TEXT NOT NULL
                    CHECK(category_type IN ('income', 'expense')),

                is_active INTEGER NOT NULL DEFAULT 1
                    CHECK(is_active IN (0, 1)),

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(name, category_type)
            );


            -- =================================================
            -- TRANSACTIONS TABLE
            -- Stores all income and expense transactions.
            -- =================================================

            CREATE TABLE IF NOT EXISTS transactions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title TEXT NOT NULL,

                amount_minor INTEGER NOT NULL
                    CHECK(amount_minor > 0),

                transaction_type TEXT NOT NULL
                    CHECK(transaction_type IN ('income', 'expense')),

                category_id INTEGER NOT NULL,

                transaction_date TEXT NOT NULL,

                payment_method TEXT NOT NULL,

                notes TEXT DEFAULT '',

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (category_id)
                    REFERENCES categories(id)
                    ON DELETE RESTRICT
            );


            -- =================================================
            -- BUDGETS TABLE
            -- Stores monthly spending limits.
            -- =================================================

            CREATE TABLE IF NOT EXISTS budgets (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                category_id INTEGER NOT NULL,

                budget_month TEXT NOT NULL,

                amount_minor INTEGER NOT NULL
                    CHECK(amount_minor > 0),

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (category_id)
                    REFERENCES categories(id)
                    ON DELETE RESTRICT,

                UNIQUE(category_id, budget_month)
            );


            -- =================================================
            -- DATABASE INDEXES
            -- Improve frequently used database searches.
            -- =================================================

            CREATE INDEX IF NOT EXISTS idx_transactions_date
                ON transactions(transaction_date);

            CREATE INDEX IF NOT EXISTS idx_transactions_category
                ON transactions(category_id);

            CREATE INDEX IF NOT EXISTS idx_transactions_type
                ON transactions(transaction_type);

            CREATE INDEX IF NOT EXISTS idx_budgets_month
                ON budgets(budget_month);

        """)

        # Save the database changes.
        connection.commit()

    finally:

        # Always close the database connection.
        connection.close()
