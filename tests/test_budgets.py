
# ============================================================
# CodeCraft Finance Manager
# Budget Service Tests
# ============================================================

import pytest

from decimal import Decimal

from app.database.connection import initialize_database

from app.services.category_service import create_category

from app.services.transaction_service import create_transaction

from app.services.budget_service import (
    create_budget,
    get_all_budgets,
    get_budget,
    update_budget,
    delete_budget,
    validate_budget_month,
)


def setup_database(tmp_path):
    """Create a separate temporary database for each test."""

    db_path = tmp_path / "test_finance.db"

    initialize_database(db_path)

    return db_path


def create_expense_category(db_path):
    """Create a test expense category."""

    return create_category(
        name="Food",
        category_type="expense",
        db_path=db_path,
    )


def add_expense(db_path, category_id, amount, transaction_date):
    """Create a test expense transaction."""

    return create_transaction(
        title="Test Expense",
        amount=amount,
        transaction_type="expense",
        category_id=category_id,
        transaction_date=transaction_date,
        payment_method="Cash",
        notes="Budget test",
        db_path=db_path,
    )


# ============================================================
# BUDGET CREATION TESTS
# ============================================================

def test_create_budget_successfully(tmp_path):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    budget_id = create_budget(
        category_id=category_id,
        budget_month="2026-11",
        amount="10000.00",
        db_path=db_path,
    )

    assert isinstance(budget_id, int)
    assert budget_id > 0


def test_prevent_duplicate_budget_for_same_category_and_month(
    tmp_path
):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    create_budget(
        category_id,
        "2026-11",
        "10000",
        db_path,
    )

    with pytest.raises(ValueError):

        create_budget(
            category_id,
            "2026-11",
            "15000",
            db_path,
        )


def test_allow_same_category_budget_for_different_months(
    tmp_path
):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    november_id = create_budget(
        category_id,
        "2026-11",
        "10000",
        db_path,
    )

    december_id = create_budget(
        category_id,
        "2026-12",
        "12000",
        db_path,
    )

    assert november_id != december_id


def test_prevent_budget_for_income_category(tmp_path):

    db_path = setup_database(tmp_path)

    income_category_id = create_category(
        "Salary",
        "income",
        db_path,
    )

    with pytest.raises(ValueError):

        create_budget(
            income_category_id,
            "2026-11",
            "50000",
            db_path,
        )


def test_prevent_budget_for_inactive_expense_category(
    tmp_path
):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    from app.services.category_service import deactivate_category

    deactivate_category(
        category_id,
        db_path,
    )

    with pytest.raises(ValueError):

        create_budget(
            category_id,
            "2026-11",
            "10000",
            db_path,
        )


# ============================================================
# BUDGET VALIDATION TESTS
# ============================================================

@pytest.mark.parametrize(
    "invalid_amount",
    [
        "0",
        "-100",
        "-0.01",
        "invalid",
        "NaN",
        "Infinity",
    ]
)
def test_reject_invalid_budget_amounts(
    tmp_path,
    invalid_amount
):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    with pytest.raises(ValueError):

        create_budget(
            category_id,
            "2026-11",
            invalid_amount,
            db_path,
        )


@pytest.mark.parametrize(
    "invalid_month",
    [
        "2026",
        "11-2026",
        "2026-13",
        "2026-00",
        "2026-1",
        "invalid",
        "",
    ]
)
def test_reject_invalid_budget_months(invalid_month):

    with pytest.raises(ValueError):

        validate_budget_month(invalid_month)


def test_accept_valid_budget_month():

    assert validate_budget_month("2026-11") == "2026-11"


# ============================================================
# BUDGET SPENDING CALCULATION TESTS
# ============================================================

def test_budget_spending_calculation(tmp_path):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    create_budget(
        category_id,
        "2026-11",
        "10000",
        db_path,
    )

    add_expense(
        db_path,
        category_id,
        "2500",
        "2026-11-05",
    )

    add_expense(
        db_path,
        category_id,
        "1500",
        "2026-11-12",
    )

    budgets = get_all_budgets(
        "2026-11",
        db_path,
    )

    assert len(budgets) == 1

    budget = budgets[0]

    assert budget["category_name"] == "Food"
    assert budget["budget_amount"] == Decimal("10000.00")
    assert budget["spent_amount"] == Decimal("4000.00")
    assert budget["remaining_amount"] == Decimal("6000.00")
    assert budget["percentage_used"] == Decimal("40.00")
    assert budget["is_over_budget"] is False


def test_budget_calculation_excludes_other_months(
    tmp_path
):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    create_budget(
        category_id,
        "2026-11",
        "10000",
        db_path,
    )

    add_expense(
        db_path,
        category_id,
        "2000",
        "2026-10-25",
    )

    add_expense(
        db_path,
        category_id,
        "3000",
        "2026-11-10",
    )

    budgets = get_all_budgets(
        "2026-11",
        db_path,
    )

    assert budgets[0]["spent_amount"] == Decimal("3000.00")


def test_budget_calculation_excludes_other_categories(
    tmp_path
):

    db_path = setup_database(tmp_path)

    food_category_id = create_expense_category(db_path)

    transport_category_id = create_category(
        "Transport",
        "expense",
        db_path,
    )

    create_budget(
        food_category_id,
        "2026-11",
        "10000",
        db_path,
    )

    add_expense(
        db_path,
        food_category_id,
        "2000",
        "2026-11-10",
    )

    add_expense(
        db_path,
        transport_category_id,
        "5000",
        "2026-11-12",
    )

    budgets = get_all_budgets(
        "2026-11",
        db_path,
    )

    assert budgets[0]["spent_amount"] == Decimal("2000.00")


def test_budget_calculation_excludes_income_transactions(
    tmp_path
):

    db_path = setup_database(tmp_path)

    expense_category_id = create_expense_category(db_path)

    income_category_id = create_category(
        "Salary",
        "income",
        db_path,
    )

    create_budget(
        expense_category_id,
        "2026-11",
        "10000",
        db_path,
    )

    add_expense(
        db_path,
        expense_category_id,
        "2000",
        "2026-11-10",
    )

    create_transaction(
        title="Monthly Salary",
        amount="50000",
        transaction_type="income",
        category_id=income_category_id,
        transaction_date="2026-11-15",
        payment_method="Bank Transfer",
        notes="Test income",
        db_path=db_path,
    )

    budgets = get_all_budgets(
        "2026-11",
        db_path,
    )

    assert budgets[0]["spent_amount"] == Decimal("2000.00")


def test_detect_budget_overspending(tmp_path):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    create_budget(
        category_id,
        "2026-11",
        "5000",
        db_path,
    )

    add_expense(
        db_path,
        category_id,
        "6500",
        "2026-11-10",
    )

    budgets = get_all_budgets(
        "2026-11",
        db_path,
    )

    budget = budgets[0]

    assert budget["spent_amount"] == Decimal("6500.00")
    assert budget["remaining_amount"] == Decimal("-1500.00")
    assert budget["percentage_used"] == Decimal("130.00")
    assert budget["is_over_budget"] is True


def test_budget_with_no_transactions(tmp_path):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    create_budget(
        category_id,
        "2026-11",
        "10000",
        db_path,
    )

    budgets = get_all_budgets(
        "2026-11",
        db_path,
    )

    budget = budgets[0]

    assert budget["spent_amount"] == Decimal("0.00")
    assert budget["remaining_amount"] == Decimal("10000.00")
    assert budget["percentage_used"] == Decimal("0.00")
    assert budget["is_over_budget"] is False


# ============================================================
# RETRIEVE BUDGET TESTS
# ============================================================

def test_get_single_budget(tmp_path):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    budget_id = create_budget(
        category_id,
        "2026-11",
        "10000",
        db_path,
    )

    budget = get_budget(
        budget_id,
        db_path,
    )

    assert budget["id"] == budget_id
    assert budget["category_name"] == "Food"
    assert budget["budget_amount"] == Decimal("10000.00")


def test_get_missing_budget_raises_error(tmp_path):

    db_path = setup_database(tmp_path)

    with pytest.raises(ValueError):

        get_budget(
            999,
            db_path,
        )


def test_get_budgets_for_month_returns_empty_list(
    tmp_path
):

    db_path = setup_database(tmp_path)

    budgets = get_all_budgets(
        "2026-11",
        db_path,
    )

    assert budgets == []


# ============================================================
# BUDGET UPDATE TESTS
# ============================================================

def test_update_budget_amount(tmp_path):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    budget_id = create_budget(
        category_id,
        "2026-11",
        "10000",
        db_path,
    )

    update_budget(
        budget_id,
        "15000",
        db_path,
    )

    budget = get_budget(
        budget_id,
        db_path,
    )

    assert budget["budget_amount"] == Decimal("15000.00")


def test_update_budget_rejects_invalid_amount(tmp_path):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    budget_id = create_budget(
        category_id,
        "2026-11",
        "10000",
        db_path,
    )

    with pytest.raises(ValueError):

        update_budget(
            budget_id,
            "-500",
            db_path,
        )


def test_update_missing_budget_raises_error(tmp_path):

    db_path = setup_database(tmp_path)

    with pytest.raises(ValueError):

        update_budget(
            999,
            "15000",
            db_path,
        )


# ============================================================
# BUDGET DELETE TESTS
# ============================================================

def test_delete_budget(tmp_path):

    db_path = setup_database(tmp_path)

    category_id = create_expense_category(db_path)

    budget_id = create_budget(
        category_id,
        "2026-11",
        "10000",
        db_path,
    )

    delete_budget(
        budget_id,
        db_path,
    )

    budgets = get_all_budgets(
        "2026-11",
        db_path,
    )

    assert budgets == []


def test_delete_missing_budget_raises_error(tmp_path):

    db_path = setup_database(tmp_path)

    with pytest.raises(ValueError):

        delete_budget(
            999,
            db_path,
        )
