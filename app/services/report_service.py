
# ============================================================
# CodeCraft Finance Manager
# Financial Reports Data Services
# ============================================================

import calendar

from datetime import date

from app.database.connection import get_connection

from app.services.transaction_service import (
    get_financial_summary,
    get_all_transactions,
)

from app.services.dashboard_service import (
    get_expense_breakdown,
)

from app.services.money_service import (
    from_minor_units,
)


def get_monthly_report_trend(
    start_date=None,
    end_date=None,
    db_path=None,
):
    """
    Retrieve monthly income and expenses for a report.

    Months without transactions are included with zero values.
    """

    # Open the database connection.
    connection = get_connection(db_path)

    try:

        # Start the SQL query.
        query = """
            SELECT
                MIN(transaction_date) AS first_date,
                MAX(transaction_date) AS last_date
            FROM transactions
            WHERE 1 = 1
        """

        # Store the query parameters.
        parameters = []

        # Apply the starting date.
        if start_date is not None:
            query += " AND transaction_date >= ?"
            parameters.append(start_date)

        # Apply the ending date.
        if end_date is not None:
            query += " AND transaction_date <= ?"
            parameters.append(end_date)

        # Retrieve the available transaction date range.
        date_range = connection.execute(
            query,
            parameters,
        ).fetchone()

        # Determine the first month.
        if start_date is not None:
            first_month = date.fromisoformat(start_date).replace(day=1)

        elif date_range["first_date"]:
            first_month = date.fromisoformat(
                date_range["first_date"]
            ).replace(day=1)

        else:
            return []

        # Determine the last month.
        if end_date is not None:
            last_month = date.fromisoformat(end_date).replace(day=1)

        elif date_range["last_date"]:
            last_month = date.fromisoformat(
                date_range["last_date"]
            ).replace(day=1)

        else:
            return []

        # Reject an invalid month range.
        if first_month > last_month:
            raise ValueError(
                "Start date cannot be after end date."
            )

        # Prepare the monthly report data.
        months = []

        current_month = first_month

        while current_month <= last_month:

            # Create the month information.
            months.append({
                "month": current_month.strftime("%Y-%m"),
                "label": current_month.strftime("%b %Y"),
                "income": 0,
                "expenses": 0,
            })

            # Move to the next month.
            if current_month.month == 12:
                current_month = date(
                    current_month.year + 1,
                    1,
                    1,
                )

            else:
                current_month = date(
                    current_month.year,
                    current_month.month + 1,
                    1,
                )

        # Retrieve the actual monthly totals.
        trend_query = """
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

            WHERE 1 = 1
        """

        # Prepare trend query parameters.
        trend_parameters = []

        # Apply the starting date.
        if start_date is not None:
            trend_query += " AND transaction_date >= ?"
            trend_parameters.append(start_date)

        # Apply the ending date.
        if end_date is not None:
            trend_query += " AND transaction_date <= ?"
            trend_parameters.append(end_date)

        # Group the results by month.
        trend_query += """
            GROUP BY strftime('%Y-%m', transaction_date)
            ORDER BY month
        """

        # Execute the monthly query.
        rows = connection.execute(
            trend_query,
            trend_parameters,
        ).fetchall()

        # Convert database results into a dictionary.
        monthly_results = {
            row["month"]: row
            for row in rows
        }

        # Add the actual values to each month.
        for month in months:

            # Find the matching database result.
            result = monthly_results.get(month["month"])

            if result:

                # Convert minor units into Decimal rupees.
                month["income"] = from_minor_units(
                    result["income"] or 0
                )

                month["expenses"] = from_minor_units(
                    result["expenses"] or 0
                )

            else:

                # Keep empty months at zero.
                month["income"] = from_minor_units(0)
                month["expenses"] = from_minor_units(0)

        # Return the monthly report.
        return months

    finally:

        # Always close the database connection.
        connection.close()


def get_report_data(
    start_date=None,
    end_date=None,
    db_path=None,
):
    """
    Collect all information required by the Reports page.
    """

    # Calculate the financial summary.
    summary = get_financial_summary(
        start_date=start_date,
        end_date=end_date,
        db_path=db_path,
    )

    # Retrieve the filtered transactions.
    transactions = get_all_transactions(
        start_date=start_date,
        end_date=end_date,
        db_path=db_path,
    )

    # Retrieve expense totals grouped by category.
    expense_breakdown = get_expense_breakdown(
        start_date=start_date,
        end_date=end_date,
        db_path=db_path,
    )

    # Retrieve the monthly financial trend.
    monthly_trend = get_monthly_report_trend(
        start_date=start_date,
        end_date=end_date,
        db_path=db_path,
    )

    # Calculate the savings rate.
    if summary["total_income"] > 0:

        savings_rate = (
            summary["balance"]
            / summary["total_income"]
        ) * 100

    else:

        savings_rate = 0

    # Return all report information.
    return {
        "start_date": start_date,
        "end_date": end_date,
        "summary": summary,
        "transactions": transactions,
        "expense_breakdown": expense_breakdown,
        "monthly_trend": monthly_trend,
        "savings_rate": savings_rate,
    }
