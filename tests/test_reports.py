
# ============================================================
# CodeCraft Finance Manager
# Financial Reports Service Tests
# ============================================================

import pytest

from app.database.connection import initialize_database

from app.services.category_service import create_category

from app.services.transaction_service import create_transaction

from decimal import Decimal

from app.services.report_service import (
    get_monthly_report_trend,
    get_report_data,
)


# ------------------------------------------------------------
# TEST DATABASE
# ------------------------------------------------------------

@pytest.fixture
def report_database(tmp_path):
    """Create a temporary database for report tests."""

    database_path = tmp_path / "report_test.db"

    initialize_database(database_path)

    return database_path


@pytest.fixture
def report_categories(report_database):
    """Create sample income and expense categories."""

    income_id = create_category(
        "Salary",
        "income",
        report_database,
    )

    food_id = create_category(
        "Food",
        "expense",
        report_database,
    )

    transport_id = create_category(
        "Transport",
        "expense",
        report_database,
    )

    return {
        "income": income_id,
        "food": food_id,
        "transport": transport_id,
    }


@pytest.fixture
def sample_report_transactions(
    report_database,
    report_categories,
):
    """Create sample transactions across three months."""

    # January income.
    create_transaction(
        "January Salary",
        "100000",
        "income",
        report_categories["income"],
        "2026-01-10",
        "Bank Transfer",
        db_path=report_database,
    )

    # January expenses.
    create_transaction(
        "January Food",
        "10000",
        "expense",
        report_categories["food"],
        "2026-01-15",
        "Cash",
        db_path=report_database,
    )

    # March income.
    create_transaction(
        "March Salary",
        "120000",
        "income",
        report_categories["income"],
        "2026-03-10",
        "Bank Transfer",
        db_path=report_database,
    )

    # March expenses.
    create_transaction(
        "March Transport",
        "5000",
        "expense",
        report_categories["transport"],
        "2026-03-12",
        "Cash",
        db_path=report_database,
    )

    return report_database


# ------------------------------------------------------------
# MONTHLY REPORT TREND TESTS
# ------------------------------------------------------------

def test_monthly_report_trend_contains_empty_months(
    sample_report_transactions,
):

    trend = get_monthly_report_trend(
        start_date="2026-01-01",
        end_date="2026-03-31",
        db_path=sample_report_transactions,
    )

    # January, February and March must be included.
    assert len(trend) == 3

    assert trend[0]["month"] == "2026-01"
    assert trend[1]["month"] == "2026-02"
    assert trend[2]["month"] == "2026-03"

    # January income and expenses.
    assert float(trend[0]["income"]) == 100000.00
    assert float(trend[0]["expenses"]) == 10000.00

    # February has no transactions.
    assert float(trend[1]["income"]) == 0.00
    assert float(trend[1]["expenses"]) == 0.00

    # March income and expenses.
    assert float(trend[2]["income"]) == 120000.00
    assert float(trend[2]["expenses"]) == 5000.00


def test_monthly_report_trend_respects_date_range(
    sample_report_transactions,
):

    trend = get_monthly_report_trend(
        start_date="2026-03-01",
        end_date="2026-03-31",
        db_path=sample_report_transactions,
    )

    assert len(trend) == 1

    assert trend[0]["month"] == "2026-03"

    assert float(trend[0]["income"]) == 120000.00
    assert float(trend[0]["expenses"]) == 5000.00


def test_monthly_report_trend_empty_database(
    report_database,
):

    trend = get_monthly_report_trend(
        db_path=report_database
    )

    assert trend == []


def test_monthly_report_trend_rejects_invalid_range(
    report_database,
):

    with pytest.raises(ValueError):

        get_monthly_report_trend(
            start_date="2026-03-31",
            end_date="2026-01-01",
            db_path=report_database,
        )


# ------------------------------------------------------------
# FINANCIAL REPORT TESTS
# ------------------------------------------------------------

def test_report_data_uses_saved_transactions(
    sample_report_transactions,
):

    report = get_report_data(
        db_path=sample_report_transactions
    )

    summary = report["summary"]

    assert float(summary["total_income"]) == 220000.00
    assert float(summary["total_expenses"]) == 15000.00
    assert float(summary["balance"]) == 205000.00

    assert summary["total_transactions"] == 4

    assert len(report["transactions"]) == 4


def test_report_data_respects_date_range(
    sample_report_transactions,
):

    report = get_report_data(
        start_date="2026-03-01",
        end_date="2026-03-31",
        db_path=sample_report_transactions,
    )

    summary = report["summary"]

    assert float(summary["total_income"]) == 120000.00
    assert float(summary["total_expenses"]) == 5000.00
    assert float(summary["balance"]) == 115000.00

    assert summary["total_transactions"] == 2

    assert len(report["transactions"]) == 2

    assert all(
        transaction["transaction_date"].startswith("2026-03")
        for transaction in report["transactions"]
    )

    assert len(report["expense_breakdown"]) == 1

    assert (
        report["expense_breakdown"][0]["category_name"]
        == "Transport"
    )


def test_report_savings_rate(
    sample_report_transactions,
):

    report = get_report_data(
        db_path=sample_report_transactions
    )

    # (Income - Expenses) / Income * 100
    expected_rate = (
        Decimal("205000")
        / Decimal("220000")
    ) * Decimal("100")

    assert report["savings_rate"] == expected_rate


def test_report_savings_rate_without_income(
    report_database,
    report_categories,
):

    create_transaction(
        "Food",
        "5000",
        "expense",
        report_categories["food"],
        "2026-11-10",
        "Cash",
        db_path=report_database,
    )

    report = get_report_data(
        db_path=report_database
    )

    assert float(report["summary"]["total_income"]) == 0.00

    assert float(report["summary"]["total_expenses"]) == 5000.00

    assert report["savings_rate"] == 0
