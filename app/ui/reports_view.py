
# ============================================================
# CodeCraft Finance Manager
# Reports and Financial Analysis
# ============================================================

import csv
import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE_SMALL,
    FONT_SIZE_NORMAL,
    FONT_SIZE_LARGE,
)

from app.services.report_service import get_report_data
from app.services.money_service import format_currency


class ReportsView(ctk.CTkFrame):
    """Reports page for financial summaries and analysis."""

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent",
            corner_radius=0
        )

        self.report_data = None
        self.current_start_date = None
        self.current_end_date = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_interface()
        self.apply_period("This Month")

    # --------------------------------------------------------
    # INTERFACE
    # --------------------------------------------------------

    def create_interface(self):
        """Build the reports page."""

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        self.scroll_frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Page heading.
        heading = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )

        heading.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        ctk.CTkLabel(
            heading,
            text="Financial Reports",
            font=(FONT_FAMILY, 22, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            heading,
            text="Review your income, expenses and financial performance.",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["text_secondary"]
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # Period filter.
        self.create_filter_section()

        # Summary cards.
        self.create_summary_section()

        # Charts.
        self.create_charts_section()

        # Transaction details.
        self.create_transactions_section()

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    def create_filter_section(self):
        """Create period selection and custom date inputs."""

        filter_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        filter_card.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        filter_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            filter_card,
            text="REPORTING PERIOD",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            text_color=COLORS["text_secondary"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(15, 8)
        )

        controls = ctk.CTkFrame(
            filter_card,
            fg_color="transparent"
        )

        controls.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 12)
        )

        self.period_var = ctk.StringVar(
            value="This Month"
        )

        self.period_menu = ctk.CTkOptionMenu(
            controls,
            variable=self.period_var,
            values=[
                "Today",
                "This Month",
                "Last Month",
                "This Year",
                "All Time",
                "Custom Range",
            ],
            width=165,
            height=36,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            command=self.on_period_changed
        )

        self.period_menu.pack(
            side="left",
            padx=(0, 12)
        )

        self.refresh_button = ctk.CTkButton(
            controls,
            text="Apply / Refresh",
            width=125,
            height=36,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.refresh_report
        )

        self.refresh_button.pack(side="left")

        self.export_button = ctk.CTkButton(
            controls,
            text="Export CSV",
            width=105,
            height=36,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            fg_color=COLORS["sidebar"],
            hover_color=COLORS["sidebar_hover"],
            command=self.export_csv
        )

        self.export_button.pack(
            side="right"
        )

        # Custom date range fields.
        custom_frame = ctk.CTkFrame(
            filter_card,
            fg_color="transparent"
        )

        custom_frame.grid(
            row=2,
            column=0,
            sticky="w",
            padx=18,
            pady=(0, 15)
        )

        self.custom_frame = custom_frame

        ctk.CTkLabel(
            custom_frame,
            text="From:",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["text_secondary"]
        ).pack(
            side="left",
            padx=(0, 7)
        )

        self.start_date_entry = ctk.CTkEntry(
            custom_frame,
            width=125,
            height=34,
            placeholder_text="YYYY-MM-DD"
        )

        self.start_date_entry.pack(
            side="left",
            padx=(0, 16)
        )

        ctk.CTkLabel(
            custom_frame,
            text="To:",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["text_secondary"]
        ).pack(
            side="left",
            padx=(0, 7)
        )

        self.end_date_entry = ctk.CTkEntry(
            custom_frame,
            width=125,
            height=34,
            placeholder_text="YYYY-MM-DD"
        )

        self.end_date_entry.pack(side="left")

        today = date.today()

        self.start_date_entry.insert(
            0,
            today.replace(day=1).isoformat()
        )

        self.end_date_entry.insert(
            0,
            today.isoformat()
        )

        self.custom_frame.grid_remove()

    def on_period_changed(self, selected_period):
        """Show date inputs only for a custom range."""

        if selected_period == "Custom Range":
            self.custom_frame.grid()
        else:
            self.custom_frame.grid_remove()

    # --------------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------------

    def create_summary_section(self):
        """Create the four financial summary cards."""

        self.summary_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )

        self.summary_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        for column in range(4):
            self.summary_frame.grid_columnconfigure(
                column,
                weight=1
            )

        self.summary_values = {}

        cards = [
            ("income", "Total Income", COLORS["income"]),
            ("expenses", "Total Expenses", COLORS["expense"]),
            ("balance", "Net Balance", COLORS["primary"]),
            ("savings", "Savings Rate", COLORS["accent"]),
        ]

        for column, (key, title, accent) in enumerate(cards):

            card = ctk.CTkFrame(
                self.summary_frame,
                fg_color=COLORS["surface"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["border"]
            )

            card.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=(0 if column == 0 else 6, 6 if column < 3 else 0)
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
                text_color=COLORS["text_secondary"]
            ).pack(
                anchor="w",
                padx=15,
                pady=(15, 7)
            )

            value_label = ctk.CTkLabel(
                card,
                text="Rs. 0.00",
                font=(FONT_FAMILY, 19, "bold"),
                text_color=accent
            )

            value_label.pack(
                anchor="w",
                padx=15,
                pady=(0, 15)
            )

            self.summary_values[key] = value_label

    # --------------------------------------------------------
    # CHARTS
    # --------------------------------------------------------

    def create_charts_section(self):
        """Create the two chart containers."""

        charts_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )

        charts_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        charts_frame.grid_columnconfigure(0, weight=3)
        charts_frame.grid_columnconfigure(1, weight=2)

        # Monthly income and expense chart.
        trend_card = ctk.CTkFrame(
            charts_frame,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        trend_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8)
        )

        ctk.CTkLabel(
            trend_card,
            text="Income vs Expenses",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(
            anchor="w",
            padx=16,
            pady=(15, 0)
        )

        self.trend_chart_frame = ctk.CTkFrame(
            trend_card,
            fg_color="transparent"
        )

        self.trend_chart_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Expense breakdown chart.
        expense_card = ctk.CTkFrame(
            charts_frame,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        expense_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0)
        )

        ctk.CTkLabel(
            expense_card,
            text="Expense Breakdown",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(
            anchor="w",
            padx=16,
            pady=(15, 0)
        )

        self.expense_chart_frame = ctk.CTkFrame(
            expense_card,
            fg_color="transparent"
        )

        self.expense_chart_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    def clear_chart(self, chart_frame):
        """Remove an old chart before drawing a new one."""

        for widget in chart_frame.winfo_children():
            widget.destroy()

    def draw_trend_chart(self, monthly_trend):
        """Draw monthly income and expense bars."""

        self.clear_chart(self.trend_chart_frame)

        figure = Figure(
            figsize=(6, 3),
            dpi=90
        )

        axis = figure.add_subplot(111)

        if not monthly_trend:
            axis.text(
                0.5,
                0.5,
                "No transaction data available",
                ha="center",
                va="center",
                transform=axis.transAxes
            )

            axis.set_axis_off()

        else:
            labels = [
                item["label"]
                for item in monthly_trend
            ]

            incomes = [
                float(item["income"])
                for item in monthly_trend
            ]

            expenses = [
                float(item["expenses"])
                for item in monthly_trend
            ]

            positions = list(range(len(labels)))
            bar_width = 0.35

            axis.bar(
                [position - bar_width / 2 for position in positions],
                incomes,
                width=bar_width,
                label="Income",
                color=COLORS["income"]
            )

            axis.bar(
                [position + bar_width / 2 for position in positions],
                expenses,
                width=bar_width,
                label="Expenses",
                color=COLORS["expense"]
            )

            axis.set_xticks(positions)
            axis.set_xticklabels(
                labels,
                rotation=30,
                ha="right"
            )

            axis.legend(
                frameon=False,
                fontsize=8
            )

            axis.grid(
                axis="y",
                alpha=0.2
            )

            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(
            figure,
            master=self.trend_chart_frame
        )

        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    def draw_expense_chart(self, expense_breakdown):
        """Draw the expense category pie chart."""

        self.clear_chart(self.expense_chart_frame)

        figure = Figure(
            figsize=(4, 3),
            dpi=90
        )

        axis = figure.add_subplot(111)

        valid_items = [
            item for item in expense_breakdown
            if item["total_minor"] > 0
        ]

        if not valid_items:
            axis.text(
                0.5,
                0.5,
                "No expenses recorded",
                ha="center",
                va="center",
                transform=axis.transAxes
            )

            axis.set_axis_off()

        else:
            labels = [
                item["category_name"]
                for item in valid_items
            ]

            amounts = [
                item["total_minor"]
                for item in valid_items
            ]

            axis.pie(
                amounts,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"fontsize": 8}
            )

            axis.axis("equal")

        figure.tight_layout()

        canvas = FigureCanvasTkAgg(
            figure,
            master=self.expense_chart_frame
        )

        canvas.draw()
        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    # --------------------------------------------------------
    # TRANSACTION TABLE
    # --------------------------------------------------------

    def create_transactions_section(self):
        """Create the detailed transaction report table."""

        table_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        table_card.grid(
            row=4,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        ctk.CTkLabel(
            table_card,
            text="Detailed Transactions",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(
            anchor="w",
            padx=16,
            pady=(15, 12)
        )

        table_container = ctk.CTkFrame(
            table_card,
            fg_color="transparent"
        )

        table_container.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 16)
        )

        columns = (
            "date",
            "title",
            "type",
            "category",
            "payment",
            "amount",
        )

        self.transaction_table = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=10
        )

        headings = {
            "date": "Date",
            "title": "Title",
            "type": "Type",
            "category": "Category",
            "payment": "Payment Method",
            "amount": "Amount",
        }

        widths = {
            "date": 100,
            "title": 180,
            "type": 90,
            "category": 140,
            "payment": 120,
            "amount": 130,
        }

        for column in columns:
            self.transaction_table.heading(
                column,
                text=headings[column]
            )

            self.transaction_table.column(
                column,
                width=widths[column],
                minwidth=70,
                anchor="w"
            )

        self.transaction_table.column(
            "amount",
            anchor="e"
        )

        scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.transaction_table.yview
        )

        self.transaction_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.transaction_table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.transaction_table.tag_configure(
            "income",
            foreground=COLORS["income"]
        )

        self.transaction_table.tag_configure(
            "expense",
            foreground=COLORS["expense"]
        )

        self.table_status = ctk.CTkLabel(
            table_card,
            text="",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=COLORS["text_secondary"]
        )

        self.table_status.pack(
            anchor="w",
            padx=16,
            pady=(0, 12)
        )

    # --------------------------------------------------------
    # PERIOD CALCULATIONS
    # --------------------------------------------------------

    def get_period_dates(self, period):
        """Calculate the selected reporting period."""

        today = date.today()

        if period == "Today":
            return today.isoformat(), today.isoformat()

        if period == "This Month":
            start = today.replace(day=1)
            return start.isoformat(), today.isoformat()

        if period == "Last Month":
            first_day_this_month = today.replace(day=1)
            last_day_previous_month = first_day_this_month - timedelta(days=1)
            first_day_previous_month = last_day_previous_month.replace(day=1)

            return (
                first_day_previous_month.isoformat(),
                last_day_previous_month.isoformat()
            )

        if period == "This Year":
            start = date(today.year, 1, 1)
            return start.isoformat(), today.isoformat()

        if period == "All Time":
            return None, None

        if period == "Custom Range":

            start_text = self.start_date_entry.get().strip()
            end_text = self.end_date_entry.get().strip()

            try:
                start = date.fromisoformat(start_text)
                end = date.fromisoformat(end_text)

            except ValueError:
                raise ValueError(
                    "Enter valid dates using YYYY-MM-DD format."
                )

            if start > end:
                raise ValueError(
                    "The start date cannot be after the end date."
                )

            return start.isoformat(), end.isoformat()

        return None, None

    def apply_period(self, period):
        """Load the report for the selected period."""

        self.period_var.set(period)
        self.refresh_report()

    # --------------------------------------------------------
    # LOAD AND DISPLAY REPORT
    # --------------------------------------------------------

    def refresh_report(self):
        """Fetch report data and update the interface."""

        try:
            start_date, end_date = self.get_period_dates(
                self.period_var.get()
            )

            self.current_start_date = start_date
            self.current_end_date = end_date

            self.report_data = get_report_data(
                start_date=start_date,
                end_date=end_date
            )

            self.update_summary()
            self.update_charts()
            self.update_transaction_table()

        except ValueError as error:
            messagebox.showwarning(
                "Invalid Reporting Period",
                str(error)
            )

        except Exception as error:
            messagebox.showerror(
                "Report Error",
                f"Unable to load the report.\n\n{error}"
            )

    def update_summary(self):
        """Update the four summary cards."""

        summary = self.report_data["summary"]

        self.summary_values["income"].configure(
            text=format_currency(summary["total_income"])
        )

        self.summary_values["expenses"].configure(
            text=format_currency(summary["total_expenses"])
        )

        self.summary_values["balance"].configure(
            text=format_currency(summary["balance"])
        )

        savings_rate = self.report_data["savings_rate"]

        self.summary_values["savings"].configure(
            text=f"{savings_rate:.1f}%"
        )

    def update_charts(self):
        """Refresh both report charts."""

        self.draw_trend_chart(
            self.report_data["monthly_trend"]
        )

        self.draw_expense_chart(
            self.report_data["expense_breakdown"]
        )

    def update_transaction_table(self):
        """Display transactions for the selected period."""

        for item in self.transaction_table.get_children():
            self.transaction_table.delete(item)

        transactions = self.report_data["transactions"]

        for transaction in transactions:

            transaction_type = transaction["transaction_type"]

            self.transaction_table.insert(
                "",
                "end",
                values=(
                    transaction["transaction_date"],
                    transaction["title"],
                    transaction_type.title(),
                    transaction["category_name"],
                    transaction["payment_method"],
                    format_currency(transaction["amount"]),
                ),
                tags=(transaction_type,)
            )

        self.table_status.configure(
            text=f"{len(transactions)} transaction(s) found"
        )

    # --------------------------------------------------------
    # CSV EXPORT
    # --------------------------------------------------------

    def export_csv(self):
        """Export the currently displayed report transactions."""

        if self.report_data is None:
            messagebox.showwarning(
                "No Report",
                "Please load a report before exporting."
            )
            return

        transactions = self.report_data["transactions"]

        if not transactions:
            messagebox.showinfo(
                "No Transactions",
                "There are no transactions to export for this period."
            )
            return

        filename = filedialog.asksaveasfilename(
            title="Export Financial Report",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
            initialfile="finance_report.csv"
        )

        if not filename:
            return

        try:
            with open(
                filename,
                "w",
                newline="",
                encoding="utf-8-sig"
            ) as csv_file:

                writer = csv.writer(csv_file)

                writer.writerow([
                    "Date",
                    "Title",
                    "Type",
                    "Category",
                    "Payment Method",
                    "Amount (LKR)",
                    "Notes",
                ])

                for transaction in transactions:

                    writer.writerow([
                        transaction["transaction_date"],
                        transaction["title"],
                        transaction["transaction_type"].title(),
                        transaction["category_name"],
                        transaction["payment_method"],
                        str(transaction["amount"]),
                        transaction["notes"] or "",
                    ])

            messagebox.showinfo(
                "Export Successful",
                f"Report exported successfully:\n{filename}"
            )

        except OSError as error:
            messagebox.showerror(
                "Export Error",
                f"Unable to export the report.\n\n{error}"
            )
