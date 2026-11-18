
# ============================================================
# CodeCraft Finance Manager
# Service Layer Tests
# ============================================================

from datetime import date

import pytest

from app.database.connection import initialize_database

from app.services.money_service import (
    to_minor_units,
    from_minor_units,
    format_currency,
)

from app.services.category_service import (
    create_category,
    get_all_categories,
    update_category,
    deactivate_category,
)

from app.services.transaction_service import (
    create_transaction,
    get_transaction,
    get_all_transactions,
    update_transaction,
    delete_transaction,
    get_financial_summary,
)


@pytest.fixture
def service_database(tmp_path):
    """Create a temporary database for service tests."""

    database_path = tmp_path / "service_test.db"

    initialize_database(database_path)

    return database_path


@pytest.fixture
def sample_categories(service_database):
    """Create sample income and expense categories."""

    income_id = create_category(
        "Salary", "income", service_database
    )

    expense_id = create_category(
        "Food", "expense", service_database
    )

    return {
        "income": income_id,
        "expense": expense_id,
    }


@pytest.fixture
def sample_transaction(service_database, sample_categories):
    """Create one sample income transaction."""

    return create_transaction(
        title="Monthly Salary",
        amount="100000",
        transaction_type="income",
        category_id=sample_categories["income"],
        transaction_date="2026-11-01",
        payment_method="Bank Transfer",
        notes="November salary",
        db_path=service_database,
    )


# ------------------------------------------------------------
# Money Service Tests
# ------------------------------------------------------------

def test_money_to_minor_units():
    assert to_minor_units("125.50") == 12550


def test_money_from_minor_units():
    assert from_minor_units(12550) == 125.50


def test_money_rejects_invalid_amount():
    with pytest.raises(ValueError):
        to_minor_units("invalid")


def test_money_formats_currency():
    result = format_currency("1500.50")

    assert "1,500.50" in result


# ------------------------------------------------------------
# Category Service Tests
# ------------------------------------------------------------

def test_create_category(service_database):

    category_id = create_category(
        "Salary",
        "income",
        service_database,
    )

    assert category_id is not None

    categories = get_all_categories(
        db_path=service_database
    )

    assert len(categories) == 1
    assert categories[0]["name"] == "Salary"


def test_create_duplicate_category(service_database):

    create_category("Salary", "income", service_database)

    with pytest.raises(ValueError):

        create_category(
            "Salary",
            "income",
            service_database,
        )


def test_get_categories_by_type(service_database):

    create_category("Salary", "income", service_database)
    create_category("Food", "expense", service_database)

    categories = get_all_categories(
        category_type="expense",
        db_path=service_database,
    )

    assert len(categories) == 1
    assert categories[0]["name"] == "Food"


def test_update_category(service_database):

    category_id = create_category(
        "Food",
        "expense",
        service_database,
    )

    update_category(
        category_id,
        "Groceries",
        service_database,
    )

    categories = get_all_categories(
        db_path=service_database
    )

    assert categories[0]["name"] == "Groceries"


def test_deactivate_category(service_database):

    category_id = create_category(
        "Food",
        "expense",
        service_database,
    )

    deactivate_category(
        category_id,
        service_database,
    )

    categories = get_all_categories(
        db_path=service_database
    )

    assert len(categories) == 0

    inactive_categories = get_all_categories(
        include_inactive=True,
        db_path=service_database,
    )

    assert len(inactive_categories) == 1
    assert inactive_categories[0]["is_active"] == 0


# ------------------------------------------------------------
# Transaction Service Tests
# ------------------------------------------------------------

def test_create_transaction(
    service_database,
    sample_categories,
):

    transaction_id = create_transaction(
        "Monthly Salary",
        "100000",
        "income",
        sample_categories["income"],
        "2026-11-01",
        "Bank Transfer",
        "Monthly payment",
        service_database,
    )

    transaction = get_transaction(
        transaction_id,
        service_database,
    )

    assert transaction is not None
    assert transaction["title"] == "Monthly Salary"
    assert transaction["amount"] == 100000.00
    assert transaction["transaction_type"] == "income"


def test_transaction_rejects_wrong_category(
    service_database,
    sample_categories,
):

    with pytest.raises(ValueError):

        create_transaction(
            "Incorrect transaction",
            "500",
            "income",
            sample_categories["expense"],
            "2026-11-01",
            "Cash",
            db_path=service_database,
        )


def test_get_all_transactions(
    service_database,
    sample_transaction,
):

    transactions = get_all_transactions(
        db_path=service_database
    )

    assert len(transactions) == 1
    assert transactions[0]["id"] == sample_transaction


def test_filter_transactions_by_type(
    service_database,
    sample_categories,
):

    create_transaction(
        "Salary",
        "100000",
        "income",
        sample_categories["income"],
        "2026-11-01",
        "Bank Transfer",
        db_path=service_database,
    )

    create_transaction(
        "Lunch",
        "1500",
        "expense",
        sample_categories["expense"],
        "2026-11-02",
        "Cash",
        db_path=service_database,
    )

    transactions = get_all_transactions(
        transaction_type="expense",
        db_path=service_database,
    )

    assert len(transactions) == 1
    assert transactions[0]["title"] == "Lunch"


def test_search_transactions(
    service_database,
    sample_transaction,
):

    transactions = get_all_transactions(
        search="Salary",
        db_path=service_database,
    )

    assert len(transactions) == 1
    assert transactions[0]["id"] == sample_transaction


def test_update_transaction(
    service_database,
    sample_categories,
    sample_transaction,
):

    update_transaction(
        sample_transaction,
        "Updated Salary",
        "120000",
        "income",
        sample_categories["income"],
        "2026-11-01",
        "Bank Transfer",
        "Updated amount",
        service_database,
    )

    transaction = get_transaction(
        sample_transaction,
        service_database,
    )

    assert transaction["title"] == "Updated Salary"
    assert transaction["amount"] == 120000.00


def test_delete_transaction(
    service_database,
    sample_transaction,
):

    delete_transaction(
        sample_transaction,
        service_database,
    )

    transaction = get_transaction(
        sample_transaction,
        service_database,
    )

    assert transaction is None


def test_financial_summary(
    service_database,
    sample_categories,
):

    create_transaction(
        "Salary",
        "100000",
        "income",
        sample_categories["income"],
        "2026-11-01",
        "Bank Transfer",
        db_path=service_database,
    )

    create_transaction(
        "Food",
        "15000",
        "expense",
        sample_categories["expense"],
        "2026-11-02",
        "Cash",
        db_path=service_database,
    )

    summary = get_financial_summary(
        db_path=service_database
    )

    assert summary["total_income"] == 100000.00
    assert summary["total_expenses"] == 15000.00
    assert summary["balance"] == 85000.00
    assert summary["total_transactions"] == 2
