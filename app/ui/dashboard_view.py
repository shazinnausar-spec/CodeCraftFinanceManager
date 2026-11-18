
# ============================================================
# CodeCraft Finance Manager
# Dashboard User Interface
# ============================================================

import customtkinter as ctk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from decimal import Decimal

from config import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE_SMALL,
    FONT_SIZE_NORMAL,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_LARGE,
    FONT_SIZE_TITLE,
)

from app.services.dashboard_service import get_dashboard_data

from app.services.money_service import (
    format_currency,
)


class DashboardView(ctk.CTkFrame):
    """Professional finance dashboard."""

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        # Configure the dashboard layout.
        self.grid_columnconfigure(0, weight=1)

        # Store the currently selected period.
        self.selected_period = "This Month"

        # Create the dashboard components.
        self.create_header()
        self.create_summary_cards()
        self.create_charts()
        self.create_recent_transactions()

        # Load real financial data.
        self.refresh_dashboard()

    def create_header(self):
        """Create the dashboard heading and controls."""

        # Header container.
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 22)
        )

        header.grid_columnconfigure(0, weight=1)

        # Dashboard title.
        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=(
                FONT_FAMILY,
                FONT_SIZE_TITLE,
                "bold"
            ),
            text_color=COLORS["text_primary"]
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        # Dashboard description.
        ctk.CTkLabel(
            header,
            text="Overview of your personal finances",
            font=(
                FONT_FAMILY,
                FONT_SIZE_NORMAL
            ),
            text_color=COLORS["text_secondary"]
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(5, 0)
        )

        # Header controls.
        controls = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        controls.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="e"
        )

        # Period selection.
        self.period_menu = ctk.CTkOptionMenu(
            controls,
            values=[
                "This Month",
                "Last Month",
                "This Year",
                "All Time"
            ],
            width=145,
            height=38,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            command=self.change_period
        )

        self.period_menu.set("This Month")

        self.period_menu.pack(
            side="left",
            padx=(0, 10)
        )

        # Refresh button.
        self.refresh_button = ctk.CTkButton(
            controls,
            text="↻  Refresh",
            width=105,
            height=38,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            command=self.refresh_dashboard
        )

        self.refresh_button.pack(side="left")

    def create_summary_cards(self):
        """Create the four financial summary cards."""

        # Container for the cards.
        cards_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        cards_container.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 22)
        )

        # Give each card equal horizontal space.
        for column in range(4):
            cards_container.grid_columnconfigure(
                column,
                weight=1,
                uniform="summary_cards"
            )

        # Card definitions.
        card_definitions = [
            (
                "TOTAL INCOME",
                "Rs. 0.00",
                "income",
                COLORS["income"]
            ),
            (
                "TOTAL EXPENSES",
                "Rs. 0.00",
                "expenses",
                COLORS["expense"]
            ),
            (
                "NET BALANCE",
                "Rs. 0.00",
                "balance",
                COLORS["primary"]
            ),
            (
                "TRANSACTIONS",
                "0",
                "transactions",
                COLORS["accent"]
            ),
        ]

        # Store labels so they can be updated later.
        self.summary_labels = {}

        # Create each summary card.
        for index, definition in enumerate(card_definitions):

            title, initial_value, key, accent = definition

            # Individual card.
            card = ctk.CTkFrame(
                cards_container,
                fg_color=COLORS["surface"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["border"]
            )

            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(0 if index == 0 else 7, 0 if index == 3 else 7)
            )

            # Card title.
            ctk.CTkLabel(
                card,
                text=title,
                font=(
                    FONT_FAMILY,
                    FONT_SIZE_SMALL,
                    "bold"
                ),
                text_color=COLORS["text_secondary"]
            ).pack(
                anchor="w",
                padx=17,
                pady=(19, 9)
            )

            # Main financial value.
            value_label = ctk.CTkLabel(
                card,
                text=initial_value,
                font=(
                    FONT_FAMILY,
                    FONT_SIZE_LARGE,
                    "bold"
                ),
                text_color=accent
            )

            value_label.pack(
                anchor="w",
                padx=17,
                pady=(0, 19)
            )

            # Store the label for future updates.
            self.summary_labels[key] = value_label

    def create_charts(self):
        """Create the two dashboard chart containers."""

        # Main chart container.
        charts_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        charts_container.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 22)
        )

        charts_container.grid_columnconfigure(
            0,
            weight=2
        )

        charts_container.grid_columnconfigure(
            1,
            weight=1
        )

        # Monthly trend card.
        self.trend_card = ctk.CTkFrame(
            charts_container,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.trend_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7)
        )

        # Expense breakdown card.
        self.expense_card = ctk.CTkFrame(
            charts_container,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.expense_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(7, 0)
        )

        # Monthly chart heading.
        ctk.CTkLabel(
            self.trend_card,
            text="Income vs Expenses",
            font=(
                FONT_FAMILY,
                FONT_SIZE_MEDIUM,
                "bold"
            ),
            text_color=COLORS["text_primary"]
        ).pack(
            anchor="w",
            padx=18,
            pady=(17, 0)
        )

        # Monthly chart subtitle.
        ctk.CTkLabel(
            self.trend_card,
            text="Last six months",
            font=(
                FONT_FAMILY,
                FONT_SIZE_SMALL
            ),
            text_color=COLORS["text_secondary"]
        ).pack(
            anchor="w",
            padx=18,
            pady=(4, 0)
        )

        # Chart drawing area.
        self.trend_chart_frame = ctk.CTkFrame(
            self.trend_card,
            fg_color="transparent"
        )

        self.trend_chart_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Expense chart heading.
        ctk.CTkLabel(
            self.expense_card,
            text="Expense Breakdown",
            font=(
                FONT_FAMILY,
                FONT_SIZE_MEDIUM,
                "bold"
            ),
            text_color=COLORS["text_primary"]
        ).pack(
            anchor="w",
            padx=18,
            pady=(17, 0)
        )

        # Expense chart subtitle.
        ctk.CTkLabel(
            self.expense_card,
            text="By category",
            font=(
                FONT_FAMILY,
                FONT_SIZE_SMALL
            ),
            text_color=COLORS["text_secondary"]
        ).pack(
            anchor="w",
            padx=18,
            pady=(4, 0)
        )

        # Expense chart drawing area.
        self.expense_chart_frame = ctk.CTkFrame(
            self.expense_card,
            fg_color="transparent"
        )

        self.expense_chart_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    def create_recent_transactions(self):
        """Create the recent transactions section."""

        # Main recent transactions card.
        self.recent_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.recent_card.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 20)
        )

        # Recent transaction heading.
        ctk.CTkLabel(
            self.recent_card,
            text="Recent Transactions",
            font=(
                FONT_FAMILY,
                FONT_SIZE_MEDIUM,
                "bold"
            ),
            text_color=COLORS["text_primary"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 15)
        )

        # Transaction table container.
        self.transactions_table = ctk.CTkFrame(
            self.recent_card,
            fg_color="transparent"
        )

        self.transactions_table.pack(
            fill="x",
            padx=18,
            pady=(0, 18)
        )

    def draw_monthly_chart(self, monthly_data):
        """Draw the six-month income and expense chart."""

        # Clear the previous chart.
        for widget in self.trend_chart_frame.winfo_children():
            widget.destroy()

        # Create the chart figure.
        figure = Figure(
            figsize=(6, 3),
            dpi=90
        )

        # Create the chart axes.
        axes = figure.add_subplot(111)

        # Extract the chart data.
        labels = [
            item["label"]
            for item in monthly_data
        ]

        income = [
            item["income"] / 100
            for item in monthly_data
        ]

        expenses = [
            item["expenses"] / 100
            for item in monthly_data
        ]

        # Calculate the bar positions.
        positions = list(range(len(labels)))

        # Set the width of each bar.
        bar_width = 0.35

        # Draw income bars.
        axes.bar(
            [
                position - bar_width / 2
                for position in positions
            ],
            income,
            width=bar_width,
            label="Income",
            color=COLORS["income"]
        )

        # Draw expense bars.
        axes.bar(
            [
                position + bar_width / 2
                for position in positions
            ],
            expenses,
            width=bar_width,
            label="Expenses",
            color=COLORS["expense"]
        )

        # Configure chart labels.
        axes.set_xticks(positions)
        axes.set_xticklabels(labels)

        # Add a legend.
        axes.legend(
            frameon=False,
            fontsize=8
        )

        # Configure chart appearance.
        axes.spines["top"].set_visible(False)
        axes.spines["right"].set_visible(False)

        axes.spines["left"].set_color(COLORS["border"])
        axes.spines["bottom"].set_color(COLORS["border"])

        axes.tick_params(
            axis="both",
            labelsize=8,
            colors=COLORS["text_secondary"]
        )

        axes.set_ylabel(
            "Amount (LKR)",
            fontsize=8
        )

        axes.grid(
            axis="y",
            linestyle="--",
            alpha=0.2
        )

        # Adjust spacing.
        figure.tight_layout()

        # Embed the chart inside CustomTkinter.
        canvas = FigureCanvasTkAgg(
            figure,
            master=self.trend_chart_frame
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    def draw_expense_chart(self, expense_data):
        """Draw the category expense breakdown chart."""

        # Clear the previous chart.
        for widget in self.expense_chart_frame.winfo_children():
            widget.destroy()

        # Create the chart figure.
        figure = Figure(
            figsize=(3, 3),
            dpi=90
        )

        # Create the chart axes.
        axes = figure.add_subplot(111)

        # Check whether expense information exists.
        if not expense_data:

            # Show a useful empty state.
            axes.text(
                0.5,
                0.5,
                "No expense data yet",
                ha="center",
                va="center",
                fontsize=11,
                color=COLORS["text_secondary"]
            )

            axes.set_axis_off()

        else:

            # Extract category names.
            labels = [
                item["category_name"]
                for item in expense_data
            ]

            # Extract expense amounts.
            values = [
                item["total_minor"] / 100
                for item in expense_data
            ]

            # Draw the category chart.
            axes.pie(
                values,
                labels=None,
                autopct="%1.0f%%",
                startangle=90,
                pctdistance=0.75,
                textprops={
                    "fontsize": 8,
                    "color": COLORS["text_primary"]
                }
            )

            # Add a category legend.
            axes.legend(
                labels,
                loc="lower center",
                bbox_to_anchor=(0.5, -0.12),
                fontsize=7,
                frameon=False
            )

        # Remove unnecessary spacing.
        figure.tight_layout()

        # Embed the chart in CustomTkinter.
        canvas = FigureCanvasTkAgg(
            figure,
            master=self.expense_chart_frame
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    def update_recent_transactions(self, transactions):
        """Display the five most recent transactions."""

        # Clear the previous transaction rows.
        for widget in self.transactions_table.winfo_children():
            widget.destroy()

        # Configure the table columns.
        self.transactions_table.grid_columnconfigure(
            0,
            weight=3
        )

        self.transactions_table.grid_columnconfigure(
            1,
            weight=2
        )

        self.transactions_table.grid_columnconfigure(
            2,
            weight=2
        )

        self.transactions_table.grid_columnconfigure(
            3,
            weight=2
        )

        # Table headings.
        headings = [
            "DESCRIPTION",
            "CATEGORY",
            "DATE",
            "AMOUNT"
        ]

        # Create the table heading row.
        for column, heading in enumerate(headings):

            ctk.CTkLabel(
                self.transactions_table,
                text=heading,
                font=(
                    FONT_FAMILY,
                    FONT_SIZE_SMALL,
                    "bold"
                ),
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).grid(
                row=0,
                column=column,
                sticky="ew",
                padx=8,
                pady=(0, 10)
            )

        # Display an empty state when no transactions exist.
        if not transactions:

            ctk.CTkLabel(
                self.transactions_table,
                text="No transactions found for this period.",
                font=(
                    FONT_FAMILY,
                    FONT_SIZE_NORMAL
                ),
                text_color=COLORS["text_secondary"]
            ).grid(
                row=1,
                column=0,
                columnspan=4,
                pady=25
            )

            return

        # Display each transaction.
        for row_index, transaction in enumerate(transactions, start=1):

            # Choose a color based on transaction type.
            amount_color = (
                COLORS["income"]
                if transaction["transaction_type"] == "income"
                else COLORS["expense"]
            )

            # Format the transaction amount.
            amount_text = format_currency(
                transaction["amount"]
            )

            # Add a positive or negative sign.
            if transaction["transaction_type"] == "income":
                amount_text = f"+ {amount_text}"
            else:
                amount_text = f"- {amount_text}"

            # Prepare the row values.
            values = [
                transaction["title"],
                transaction["category_name"],
                transaction["transaction_date"],
                amount_text
            ]

            # Create the row labels.
            for column, value in enumerate(values):

                ctk.CTkLabel(
                    self.transactions_table,
                    text=value,
                    font=(
                        FONT_FAMILY,
                        FONT_SIZE_NORMAL,
                        "bold" if column == 3 else "normal"
                    ),
                    text_color=(
                        amount_color
                        if column == 3
                        else COLORS["text_primary"]
                    ),
                    anchor="w"
                ).grid(
                    row=row_index * 2 - 1,
                    column=column,
                    sticky="ew",
                    padx=8,
                    pady=9
                )

            # Add a separator after each transaction.
            if row_index < len(transactions):

                separator = ctk.CTkFrame(
                    self.transactions_table,
                    height=1,
                    fg_color=COLORS["border"]
                )

                separator.grid(
                    row=row_index * 2,
                    column=0,
                    columnspan=4,
                    sticky="ew",
                    pady=2
                )

    def change_period(self, selected_period):
        """Update the dashboard when the period changes."""

        # Store the selected period.
        self.selected_period = selected_period

        # Reload dashboard information.
        self.refresh_dashboard()

    def refresh_dashboard(self):
        """Retrieve and display the latest financial information."""

        try:

            # Retrieve the dashboard information.
            dashboard_data = get_dashboard_data(
                period=self.selected_period
            )

            # Extract the financial summary.
            summary = dashboard_data["summary"]

            # Update total income.
            self.summary_labels["income"].configure(
                text=format_currency(
                    summary["total_income"]
                )
            )

            # Update total expenses.
            self.summary_labels["expenses"].configure(
                text=format_currency(
                    summary["total_expenses"]
                )
            )

            # Update the net balance.
            self.summary_labels["balance"].configure(
                text=format_currency(
                    summary["balance"]
                )
            )

            # Update the transaction count.
            self.summary_labels["transactions"].configure(
                text=str(
                    summary["total_transactions"]
                )
            )

            # Draw the monthly income and expense chart.
            self.draw_monthly_chart(
                dashboard_data["monthly_trend"]
            )

            # Draw the expense category chart.
            self.draw_expense_chart(
                dashboard_data["expense_breakdown"]
            )

            # Update the recent transactions.
            self.update_recent_transactions(
                dashboard_data["recent_transactions"]
            )

        except Exception as error:

            # Show a readable error if dashboard loading fails.
            import tkinter.messagebox as messagebox

            messagebox.showerror(
                "Dashboard Error",
                f"Unable to load dashboard data:\n\n{error}"
            )
