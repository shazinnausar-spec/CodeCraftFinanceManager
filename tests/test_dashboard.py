
# ============================================================
# CodeCraft Finance Manager
# Dashboard Service Tests
# ============================================================

from datetime import date, timedelta

import pytest

from app.database.connection import initialize_database

from app.services.category_service import create_category

from app.services.transaction_service import create_transaction

from app.services.dashboard_service import (
    get_period_dates,
    get_monthly_trend,
    get_expense_breakdown,
    get_dashboard_data,
)


@pytest.fixture
def dashboard_database(tmp_path):
    """Create a temporary database for dashboard tests."""

    database_path = tmp_path / "dashboard_test.db"

    initialize_database(database_path)

    return database_path


def test_all_time_period():

    start_date, end_date = get_period_dates("All Time")

    assert start_date is None
    assert end_date is None


def test_last_month_period():

    start_date, end_date = get_period_dates("Last Month")

    today = date.today()

    current_month_start = today.replace(day=1)

    previous_month_end = current_month_start - timedelta(days=1)

    previous_month_start = previous_month_end.replace(day=1)

    assert start_date == previous_month_start.isoformat()
    assert end_date == previous_month_end.isoformat()


def test_unsupported_period():

    with pytest.raises(ValueError):

        get_period_dates("Invalid Period")


def test_monthly_trend_contains_six_months(
    dashboard_database,
):

    trend = get_monthly_trend(
        db_path=dashboard_database
    )

    assert len(trend) == 6

    assert all(
        "month" in item
        and "income" in item
        and "expenses" in item
        for item in trend
    )


def test_expense_breakdown(
    dashboard_database,
):

    income_category = create_category(
        "Salary",
        "income",
        dashboard_database,
    )

    food_category = create_category(
        "Food",
        "expense",
        dashboard_database,
    )

    transport_category = create_category(
        "Transport",
        "expense",
        dashboard_database,
    )

    create_transaction(
        "Monthly Salary",
        "100000",
        "income",
        income_category,
        date.today().isoformat(),
        "Bank Transfer",
        db_path=dashboard_database,
    )

    create_transaction(
        "Lunch",
        "1500",
        "expense",
        food_category,
        date.today().isoformat(),
        "Cash",
        db_path=dashboard_database,
    )

    create_transaction(
        "Bus",
        "500",
        "expense",
        transport_category,
        date.today().isoformat(),
        "Cash",
        db_path=dashboard_database,
    )

    breakdown = get_expense_breakdown(
        db_path=dashboard_database
    )

    assert len(breakdown) == 2

    amounts = {
        item["category_name"]: item["total_minor"]
        for item in breakdown
    }

    assert amounts["Food"] == 150000
    assert amounts["Transport"] == 50000


def test_dashboard_data_uses_saved_transactions(
    dashboard_database,
):

    income_category = create_category(
        "Salary",
        "income",
        dashboard_database,
    )

    expense_category = create_category(
        "Food",
        "expense",
        dashboard_database,
    )

    today = date.today().isoformat()

    create_transaction(
        "Salary",
        "100000",
        "income",
        income_category,
        today,
        "Bank Transfer",
        db_path=dashboard_database,
    )

    create_transaction(
        "Food",
        "15000",
        "expense",
        expense_category,
        today,
        "Cash",
        db_path=dashboard_database,
    )

    dashboard = get_dashboard_data(
        period="All Time",
        db_path=dashboard_database,
    )

    summary = dashboard["summary"]

    assert summary["total_income"] == 100000.00
    assert summary["total_expenses"] == 15000.00
    assert summary["balance"] == 85000.00

    assert summary["total_transactions"] == 2

    assert len(dashboard["recent_transactions"]) == 2
