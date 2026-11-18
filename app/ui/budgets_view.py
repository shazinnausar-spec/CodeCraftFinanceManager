
# ============================================================
# CodeCraft Finance Manager
# Budget Management Interface
# ============================================================

import customtkinter as ctk

from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal

from config import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE_NORMAL,
    FONT_SIZE_SMALL,
    FONT_SIZE_MEDIUM,
)

from app.services.budget_service import (
    create_budget,
    get_all_budgets,
    update_budget,
    delete_budget,
)

from app.services.category_service import get_all_categories

from app.services.money_service import format_currency


class BudgetsView(ctk.CTkFrame):
    """Page for managing monthly expense budgets."""

    def __init__(self, master):
        super().__init__(
            master,
            fg_color=COLORS["background"]
        )

        # Store the selected month.
        self.selected_month = date.today().strftime("%Y-%m")

        # Store retrieved budget records.
        self.budget_lookup = {}

        # Configure the page layout.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.create_header()
        self.create_month_controls()
        self.create_summary_cards()
        self.create_budget_table()

        self.refresh_budgets()

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    def create_header(self):
        """Create the page heading."""

        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=25,
            pady=(25, 15)
        )

        ctk.CTkLabel(
            header_frame,
            text="Budget Management",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text=(
                "Set monthly spending limits and monitor "
                "your expenses by category."
            ),
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["text_secondary"]
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

    # ---------------------------------------------------------
    # MONTH CONTROLS
    # ---------------------------------------------------------

    def create_month_controls(self):
        """Create the month selector and action buttons."""

        controls_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        controls_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 15)
        )

        controls_frame.grid_columnconfigure(0, weight=1)

        # Month label.
        ctk.CTkLabel(
            controls_frame,
            text="Budget Month (YYYY-MM)",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            text_color=COLORS["text_primary"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(18, 8),
            pady=15
        )

        # Month input.
        self.month_entry = ctk.CTkEntry(
            controls_frame,
            width=130,
            height=36,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            border_color=COLORS["border"],
            corner_radius=8
        )

        self.month_entry.insert(
            0,
            self.selected_month
        )

        self.month_entry.grid(
            row=0,
            column=1,
            padx=8,
            pady=15
        )

        # Apply month button.
        ctk.CTkButton(
            controls_frame,
            text="Apply",
            command=self.apply_selected_month,
            width=75,
            height=36,
            corner_radius=8,
            fg_color=COLORS["sidebar_hover"],
            hover_color=COLORS["sidebar_active"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        ).grid(
            row=0,
            column=2,
            padx=8,
            pady=15
        )

        # Add budget button.
        ctk.CTkButton(
            controls_frame,
            text="+ Add Budget",
            command=self.open_add_budget_form,
            width=130,
            height=36,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
        ).grid(
            row=0,
            column=3,
            padx=(8, 18),
            pady=15
        )

    # ---------------------------------------------------------
    # SUMMARY CARDS
    # ---------------------------------------------------------

    def create_summary_cards(self):
        """Create the four monthly budget summary cards."""

        self.summary_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.summary_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 15)
        )

        for column in range(4):
            self.summary_frame.grid_columnconfigure(
                column,
                weight=1
            )

        self.summary_values = {}

        summary_items = [
            ("budget", "Total Budget", "Rs. 0.00"),
            ("spent", "Total Spent", "Rs. 0.00"),
            ("remaining", "Remaining", "Rs. 0.00"),
            ("usage", "Budget Usage", "0.00%"),
        ]

        for column, (key, title, default_value) in enumerate(
            summary_items
        ):

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
                sticky="nsew",
                padx=(0 if column == 0 else 7, 0 if column == 3 else 7)
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=(FONT_FAMILY, FONT_SIZE_SMALL),
                text_color=COLORS["text_secondary"]
            ).pack(
                anchor="w",
                padx=16,
                pady=(15, 5)
            )

            value_label = ctk.CTkLabel(
                card,
                text=default_value,
                font=(FONT_FAMILY, 20, "bold"),
                text_color=COLORS["text_primary"]
            )

            value_label.pack(
                anchor="w",
                padx=16,
                pady=(0, 15)
            )

            self.summary_values[key] = value_label

    # ---------------------------------------------------------
    # BUDGET TABLE
    # ---------------------------------------------------------

    def create_budget_table(self):
        """Create the table displaying monthly budgets."""

        table_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        table_container.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(0, 25)
        )

        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)

        # Table heading.
        self.table_title = ctk.CTkLabel(
            table_container,
            text="Monthly Category Budgets",
            font=(FONT_FAMILY, FONT_SIZE_MEDIUM, "bold"),
            text_color=COLORS["text_primary"]
        )

        self.table_title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(18, 12)
        )

        # Configure Treeview style.
        style = ttk.Style()

        style.configure(
            "Budgets.Treeview",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            rowheight=38,
            background=COLORS["surface"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["surface"]
        )

        style.configure(
            "Budgets.Treeview.Heading",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            background=COLORS["background"],
            foreground=COLORS["text_primary"],
            padding=10
        )

        style.map(
            "Budgets.Treeview",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", "#FFFFFF")]
        )

        # Table frame.
        tree_frame = ctk.CTkFrame(
            table_container,
            fg_color="transparent"
        )

        tree_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(0, 10)
        )

        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Create Treeview.
        self.budget_table = ttk.Treeview(
            tree_frame,
            columns=(
                "category",
                "budget",
                "spent",
                "remaining",
                "usage",
                "status"
            ),
            show="headings",
            style="Budgets.Treeview",
            selectmode="browse"
        )

        column_settings = [
            ("category", "Category", 150, "w"),
            ("budget", "Budget Amount", 130, "e"),
            ("spent", "Spent", 130, "e"),
            ("remaining", "Remaining", 130, "e"),
            ("usage", "Used", 85, "center"),
            ("status", "Status", 110, "center"),
        ]

        for column, heading, width, anchor in column_settings:

            self.budget_table.heading(
                column,
                text=heading
            )

            self.budget_table.column(
                column,
                width=width,
                anchor=anchor
            )

        self.budget_table.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        # Vertical scrollbar.
        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=self.budget_table.yview
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.budget_table.configure(
            yscrollcommand=scrollbar.set
        )

        # Row colors.
        self.budget_table.tag_configure(
            "normal",
            foreground=COLORS["text_primary"]
        )

        self.budget_table.tag_configure(
            "warning",
            foreground=COLORS["expense"]
        )

        self.budget_table.tag_configure(
            "inactive",
            foreground=COLORS["text_secondary"]
        )

        # Double-click to edit a budget.
        self.budget_table.bind(
            "<Double-1>",
            self.edit_selected_budget
        )

        # Action buttons.
        actions_frame = ctk.CTkFrame(
            table_container,
            fg_color="transparent"
        )

        actions_frame.grid(
            row=2,
            column=0,
            sticky="e",
            padx=18,
            pady=(5, 18)
        )

        ctk.CTkButton(
            actions_frame,
            text="Refresh",
            command=self.refresh_budgets,
            width=90,
            height=34,
            corner_radius=8,
            fg_color=COLORS["sidebar_hover"],
            hover_color=COLORS["sidebar_active"],
            font=(FONT_FAMILY, FONT_SIZE_SMALL)
        ).pack(
            side="left",
            padx=(0, 10)
        )

        ctk.CTkButton(
            actions_frame,
            text="Edit Selected",
            command=self.edit_selected_budget,
            width=120,
            height=34,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(FONT_FAMILY, FONT_SIZE_SMALL)
        ).pack(
            side="left",
            padx=(0, 10)
        )

        ctk.CTkButton(
            actions_frame,
            text="Delete Selected",
            command=self.delete_selected_budget,
            width=125,
            height=34,
            corner_radius=8,
            fg_color=COLORS["expense"],
            hover_color="#B91C1C",
            font=(FONT_FAMILY, FONT_SIZE_SMALL)
        ).pack(side="left")

    # ---------------------------------------------------------
    # MONTH SELECTION
    # ---------------------------------------------------------

    def apply_selected_month(self):
        """Apply the month entered by the user."""

        selected_month = self.month_entry.get().strip()

        try:
            # The service validates the YYYY-MM format.
            get_all_budgets(selected_month)

            self.selected_month = selected_month

            self.refresh_budgets()

        except ValueError as error:
            messagebox.showwarning(
                "Invalid Month",
                str(error),
                parent=self
            )

        except Exception as error:
            messagebox.showerror(
                "Budget Error",
                f"Unable to load budgets.\n\n{error}",
                parent=self
            )

    # ---------------------------------------------------------
    # REFRESH BUDGETS
    # ---------------------------------------------------------

    def refresh_budgets(self):
        """Load budgets and update the table and summary."""

        # Clear existing table rows.
        for item in self.budget_table.get_children():
            self.budget_table.delete(item)

        self.budget_lookup.clear()

        try:
            budgets = get_all_budgets(
                self.selected_month
            )

            total_budget = sum(
                (item["budget_amount"] for item in budgets),
                Decimal("0.00")
            )

            total_spent = sum(
                (item["spent_amount"] for item in budgets),
                Decimal("0.00")
            )

            total_remaining = total_budget - total_spent

            # Calculate total budget usage.
            if total_budget > 0:

                total_usage = (
                    total_spent / total_budget
                ) * Decimal("100")

            else:
                total_usage = Decimal("0.00")

            # Update summary cards.
            self.summary_values["budget"].configure(
                text=format_currency(total_budget)
            )

            self.summary_values["spent"].configure(
                text=format_currency(total_spent)
            )

            self.summary_values["remaining"].configure(
                text=format_currency(total_remaining),
                text_color=(
                    COLORS["expense"]
                    if total_remaining < 0
                    else COLORS["income"]
                )
            )

            self.summary_values["usage"].configure(
                text=f"{total_usage:.2f}%"
            )

            # Update the table heading.
            self.table_title.configure(
                text=f"Monthly Category Budgets - {self.selected_month}"
            )

            # Add each budget to the table.
            for budget in budgets:

                budget_id = budget["id"]

                is_over_budget = budget["is_over_budget"]

                is_inactive = not budget["category_active"]

                if is_inactive:
                    status = "Inactive Category"
                    tag = "inactive"

                elif is_over_budget:
                    status = "Over Budget"
                    tag = "warning"

                else:
                    status = "Within Budget"
                    tag = "normal"

                self.budget_table.insert(
                    "",
                    "end",
                    iid=str(budget_id),
                    values=(
                        budget["category_name"],
                        format_currency(budget["budget_amount"]),
                        format_currency(budget["spent_amount"]),
                        format_currency(budget["remaining_amount"]),
                        f'{budget["percentage_used"]:.2f}%',
                        status
                    ),
                    tags=(tag,)
                )

                self.budget_lookup[budget_id] = budget

        except Exception as error:

            messagebox.showerror(
                "Budget Error",
                f"Unable to load budgets.\n\n{error}",
                parent=self
            )

    # ---------------------------------------------------------
    # ADD BUDGET
    # ---------------------------------------------------------

    def open_add_budget_form(self):
        """Open the form for creating a monthly budget."""

        BudgetForm(
            self,
            budget_month=self.selected_month,
            on_success=self.refresh_budgets
        )

    # ---------------------------------------------------------
    # EDIT BUDGET
    # ---------------------------------------------------------

    def edit_selected_budget(self, event=None):
        """Edit the selected budget amount."""

        selected_item = self.budget_table.selection()

        if not selected_item:
            if event is None:
                messagebox.showwarning(
                    "No Selection",
                    "Please select a budget first.",
                    parent=self
                )
            return

        budget_id = int(selected_item[0])

        budget = self.budget_lookup.get(budget_id)

        if not budget:
            return

        BudgetForm(
            self,
            budget_month=budget["budget_month"],
            budget=budget,
            on_success=self.refresh_budgets
        )

    # ---------------------------------------------------------
    # DELETE BUDGET
    # ---------------------------------------------------------

    def delete_selected_budget(self):
        """Delete the selected monthly budget."""

        selected_item = self.budget_table.selection()

        if not selected_item:
            messagebox.showwarning(
                "No Selection",
                "Please select a budget first.",
                parent=self
            )
            return

        budget_id = int(selected_item[0])

        budget = self.budget_lookup.get(budget_id)

        if not budget:
            return

        confirmed = messagebox.askyesno(
            "Confirm Budget Deletion",
            (
                f"Are you sure you want to delete the "
                f"'{budget['category_name']}' budget for "
                f"{budget['budget_month']}?\n\n"
                "This will delete the budget only. "
                "Your transactions will remain unchanged."
            ),
            parent=self
        )

        if not confirmed:
            return

        try:
            delete_budget(budget_id)

            messagebox.showinfo(
                "Budget Deleted",
                "The budget was deleted successfully.",
                parent=self
            )

            self.refresh_budgets()

        except Exception as error:
            messagebox.showerror(
                "Deletion Error",
                f"Unable to delete budget.\n\n{error}",
                parent=self
            )


# ============================================================
# BUDGET FORM
# ============================================================

class BudgetForm(ctk.CTkToplevel):
    """Dialog for creating or editing a monthly budget."""

    def __init__(
        self,
        parent,
        budget_month,
        budget=None,
        on_success=None
    ):
        super().__init__(parent)

        self.parent = parent
        self.budget_month = budget_month
        self.budget = budget
        self.on_success = on_success

        self.is_editing = budget is not None

        self.category_lookup = {}

        # Window settings.
        self.title(
            "Edit Budget" if self.is_editing
            else "Add Budget"
        )

        self.geometry("470x430")
        self.resizable(False, False)

        self.configure(
            fg_color=COLORS["background"]
        )

        self.transient(parent)
        self.grab_set()

        self.create_form()

        # Center the window.
        self.update_idletasks()

        x = (
            self.winfo_screenwidth() // 2
            - self.winfo_width() // 2
        )

        y = (
            self.winfo_screenheight() // 2
            - self.winfo_height() // 2
        )

        self.geometry(f"+{x}+{y}")

    # ---------------------------------------------------------
    # FORM UI
    # ---------------------------------------------------------

    def create_form(self):
        """Create the budget input form."""

        container = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12
        )

        container.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # Heading.
        ctk.CTkLabel(
            container,
            text=(
                "Edit Monthly Budget" if self.is_editing
                else "Create Monthly Budget"
            ),
            font=(FONT_FAMILY, 20, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(
            anchor="w",
            padx=22,
            pady=(22, 5)
        )

        # Selected month.
        ctk.CTkLabel(
            container,
            text=f"Budget Month: {self.budget_month}",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["text_secondary"]
        ).pack(
            anchor="w",
            padx=22,
            pady=(5, 18)
        )

        # Category label.
        ctk.CTkLabel(
            container,
            text="Expense Category",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 6)
        )

        if self.is_editing:

            # Existing budgets keep their original category.
            category_text = self.budget["category_name"]

            if not self.budget["category_active"]:
                category_text += " (Inactive)"

            self.category_selector = ctk.CTkLabel(
                container,
                text=category_text,
                height=38,
                anchor="w",
                fg_color=COLORS["background"],
                corner_radius=8,
                text_color=COLORS["text_primary"],
                font=(FONT_FAMILY, FONT_SIZE_NORMAL)
            )

            self.category_selector.pack(
                fill="x",
                padx=22
            )

        else:

            # Load active expense categories.
            categories = get_all_categories(
                category_type="expense"
            )

            self.category_lookup = {
                category["name"]: category["id"]
                for category in categories
            }

            category_names = list(self.category_lookup.keys())

            if category_names:

                self.category_selector = ctk.CTkOptionMenu(
                    container,
                    values=category_names,
                    height=38,
                    font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                    fg_color=COLORS["primary"],
                    button_color=COLORS["primary_hover"],
                    button_hover_color=COLORS["sidebar_active"]
                )

                self.category_selector.set(
                    category_names[0]
                )

            else:

                self.category_selector = ctk.CTkLabel(
                    container,
                    text="No active expense categories available",
                    height=38,
                    anchor="w",
                    fg_color=COLORS["background"],
                    corner_radius=8,
                    text_color=COLORS["text_secondary"],
                    font=(FONT_FAMILY, FONT_SIZE_NORMAL)
                )

            self.category_selector.pack(
                fill="x",
                padx=22
            )

        # Amount label.
        ctk.CTkLabel(
            container,
            text="Monthly Budget Amount (LKR)",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(
            anchor="w",
            padx=22,
            pady=(20, 6)
        )

        # Amount input.
        self.amount_entry = ctk.CTkEntry(
            container,
            height=40,
            placeholder_text="Enter budget amount",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=8
        )

        self.amount_entry.pack(
            fill="x",
            padx=22
        )

        # Populate amount when editing.
        if self.is_editing:

            self.amount_entry.insert(
                0,
                str(self.budget["budget_amount"])
            )

        # Buttons.
        buttons_frame = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        buttons_frame.pack(
            fill="x",
            padx=22,
            pady=(28, 20)
        )

        ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            height=36,
            fg_color=COLORS["sidebar_hover"],
            hover_color=COLORS["sidebar_active"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        ).pack(side="right")

        ctk.CTkButton(
            buttons_frame,
            text="Save Budget",
            command=self.save_budget,
            width=130,
            height=36,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
        ).pack(
            side="right",
            padx=(0, 10)
        )

        self.amount_entry.focus()

    # ---------------------------------------------------------
    # SAVE BUDGET
    # ---------------------------------------------------------

    def save_budget(self):
        """Create a new budget or update an existing one."""

        amount = self.amount_entry.get().strip()

        if not amount:
            messagebox.showwarning(
                "Missing Amount",
                "Please enter a budget amount.",
                parent=self
            )
            self.amount_entry.focus()
            return

        try:

            if self.is_editing:

                update_budget(
                    budget_id=self.budget["id"],
                    amount=amount
                )

                success_message = "Budget updated successfully."

            else:

                if not self.category_lookup:
                    raise ValueError(
                        "Please create an active expense category "
                        "before creating a budget."
                    )

                selected_category = self.category_selector.get()

                category_id = self.category_lookup.get(
                    selected_category
                )

                if category_id is None:
                    raise ValueError(
                        "Please select a valid expense category."
                    )

                create_budget(
                    category_id=category_id,
                    budget_month=self.budget_month,
                    amount=amount
                )

                success_message = "Budget created successfully."

            messagebox.showinfo(
                "Success",
                success_message,
                parent=self
            )

            # Refresh the budget page.
            if self.on_success:
                self.on_success()

            self.destroy()

        except ValueError as error:

            messagebox.showwarning(
                "Invalid Budget",
                str(error),
                parent=self
            )

        except Exception as error:

            messagebox.showerror(
                "Budget Error",
                f"Unable to save budget.\n\n{error}",
                parent=self
            )
