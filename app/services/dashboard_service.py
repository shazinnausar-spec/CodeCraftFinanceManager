
# ============================================================
# CodeCraft Finance Manager
# Dashboard Data Services
# ============================================================

import calendar

from datetime import date, timedelta

from app.database.connection import get_connection

from app.services.transaction_service import (
    get_financial_summary,
    get_all_transactions,
)


def get_period_dates(period):
    """
    Return the start and end dates for a dashboard period.

    Supported periods:
    - This Month
    - Last Month
    - This Year
    - All Time
    """

    # Get today's date.
    today = date.today()

    # Calculate the first day of the current month.
    current_month_start = today.replace(day=1)

    # Calculate the last day of the current month.
    current_month_end = today.replace(
        day=calendar.monthrange(today.year, today.month)[1]
    )

    # Handle the current month.
    if period == "This Month":

        return (
            current_month_start.isoformat(),
            current_month_end.isoformat()
        )

    # Handle the previous month.
        # Handle the previous month.
    if period == "Last Month":

        # Find the last day of the previous month.
        previous_month_end = current_month_start - timedelta(days=1)

        # Find the first day of the previous month.
        previous_month_start = previous_month_end.replace(day=1)

        # Return the previous month's date range.
        return (
            previous_month_start.isoformat(),
            previous_month_end.isoformat()
        )
    
    # Handle the current year.
    if period == "This Year":

        return (
            date(today.year, 1, 1).isoformat(),
            date(today.year, 12, 31).isoformat()
        )

    # Handle all saved transactions.
    if period == "All Time":

        return None, None

    # Reject unsupported periods.
    raise ValueError("Unsupported dashboard period.")


def get_monthly_trend(db_path=None):
    """
    Retrieve income and expenses for the last six months.

    Months without transactions are included with zero values.
    """

    # Get today's date.
    today = date.today()

    # Prepare the six-month period.
    months = []

    for offset in range(5, -1, -1):

        # Calculate the month and year.
        month_index = today.month - offset
        year = today.year

        while month_index <= 0:
            month_index += 12
            year -= 1

        # Create the first day of the month.
        month_start = date(year, month_index, 1)

        # Create a readable month label.
        month_label = calendar.month_abbr[month_index]

        # Store the month information.
        months.append({
            "month": month_start.strftime("%Y-%m"),
            "label": month_label,
            "income": 0,
            "expenses": 0,
        })

    # Determine the first month in the trend.
    first_month = months[0]["month"]

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Retrieve monthly income and expenses.
        rows = connection.execute("""
            SELECT
                strftime('%Y-%m', transaction_date) AS month,

                SUM(
                    CASE
                        WHEN transaction_type = 'income'
                        THEN amount_minor
                        ELSE 0
                    END
                ) AS income,

                SUM(
                    CASE
                        WHEN transaction_type = 'expense'
                        THEN amount_minor
                        ELSE 0
                    END
                ) AS expenses

            FROM transactions

            WHERE transaction_date >= ?

            GROUP BY strftime('%Y-%m', transaction_date)

            ORDER BY month
        """, (first_month + "-01",)).fetchall()

        # Convert the query results into a dictionary.
        monthly_results = {
            row["month"]: row
            for row in rows
        }

        # Fill the six months with their actual values.
        for month in months:

            result = monthly_results.get(month["month"])

            if result:

                month["income"] = result["income"] or 0
                month["expenses"] = result["expenses"] or 0

        # Return the monthly trend.
        return months

    finally:

        # Close the database connection.
        connection.close()


def get_expense_breakdown(
    start_date=None,
    end_date=None,
    db_path=None
):
    """
    Retrieve expense totals grouped by category.
    """

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Build the expense breakdown query.
        query = """
            SELECT
                categories.id AS category_id,
                categories.name AS category_name,
                SUM(transactions.amount_minor) AS total_minor

            FROM transactions

            JOIN categories
                ON transactions.category_id = categories.id

            WHERE transactions.transaction_type = 'expense'
        """

        # Store query parameters.
        parameters = []

        # Apply the starting date.
        if start_date is not None:

            query += " AND transactions.transaction_date >= ?"
            parameters.append(start_date)

        # Apply the ending date.
        if end_date is not None:

            query += " AND transactions.transaction_date <= ?"
            parameters.append(end_date)

        # Group expenses by category.
        query += """
            GROUP BY categories.id, categories.name

            ORDER BY total_minor DESC
        """

        # Execute the query.
        rows = connection.execute(
            query,
            parameters
        ).fetchall()

        # Convert the results into dictionaries.
        return [
            {
                "category_id": row["category_id"],
                "category_name": row["category_name"],
                "total_minor": row["total_minor"],
            }
            for row in rows
        ]

    finally:

        # Close the database connection.
        connection.close()


def get_dashboard_data(period="This Month", db_path=None):
    """
    Collect all data required by the dashboard.
    """

    # Determine the selected date range.
    start_date, end_date = get_period_dates(period)

    # Calculate the financial summary.
    summary = get_financial_summary(
        start_date=start_date,
        end_date=end_date,
        db_path=db_path
    )

    # Retrieve monthly income and expense information.
    monthly_trend = get_monthly_trend(
        db_path=db_path
    )

    # Retrieve expenses grouped by category.
    expense_breakdown = get_expense_breakdown(
        start_date=start_date,
        end_date=end_date,
        db_path=db_path
    )

    # Retrieve the latest five transactions.
    recent_transactions = get_all_transactions(
        start_date=start_date,
        end_date=end_date,
        db_path=db_path
    )[:5]

    # Return all dashboard information.
    return {
        "period": period,
        "summary": summary,
        "monthly_trend": monthly_trend,
        "expense_breakdown": expense_breakdown,
        "recent_transactions": recent_transactions,
    }
