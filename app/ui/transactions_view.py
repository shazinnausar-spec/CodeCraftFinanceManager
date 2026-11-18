
# ============================================================
# CodeCraft Finance Manager
# Transactions Management Interface
# ============================================================

import customtkinter as ctk

from tkinter import ttk, messagebox
from decimal import Decimal

from app.ui import main_window
from config import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE_SMALL,
    FONT_SIZE_NORMAL,
    FONT_SIZE_LARGE,
)

from app.services.transaction_service import (
    create_transaction,
    get_all_transactions,
    get_transaction,
    update_transaction,
    delete_transaction,
)

from app.services.category_service import (
    get_all_categories,
)

from app.services.money_service import (
    format_currency,
)


class TransactionsView(ctk.CTkFrame):
    """Transactions management page."""

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.current_type = "All"
        self.current_search = ""

        self.create_header()
        self.create_summary_cards()
        self.create_toolbar()
        self.create_transaction_table()
        self.refresh_transactions()

    def create_header(self):
        """Create the page heading."""

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 20)
        )

        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Transactions",
            font=(FONT_FAMILY, 27, "bold"),
            text_color=COLORS["text_primary"]
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkLabel(
            header,
            text="Manage your income and expenses",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["text_secondary"]
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(5, 0)
        )

        self.add_button = ctk.CTkButton(
            header,
            text="+  Add Transaction",
            width=170,
            height=40,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.open_add_transaction
        )

        self.add_button.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="e"
        )

    def create_summary_cards(self):
        """Create transaction summary cards."""

        cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        cards_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 20)
        )

        for column in range(3):
            cards_frame.grid_columnconfigure(
                column,
                weight=1
            )

        self.summary_values = {}

        card_data = [
            ("income", "Total Income", COLORS["income"]),
            ("expenses", "Total Expenses", COLORS["expense"]),
            ("balance", "Net Balance", COLORS["primary"]),
        ]

        for column, (key, title, accent) in enumerate(card_data):

            card = ctk.CTkFrame(
                cards_frame,
                fg_color=COLORS["surface"],
                corner_radius=12,
                border_width=1,
                border_color=COLORS["border"]
            )

            card.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=(0 if column == 0 else 7, 7 if column < 2 else 0)
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=(FONT_FAMILY, FONT_SIZE_SMALL),
                text_color=COLORS["text_secondary"]
            ).pack(
                anchor="w",
                padx=18,
                pady=(17, 5)
            )

            value_label = ctk.CTkLabel(
                card,
                text="Rs. 0.00",
                font=(FONT_FAMILY, 22, "bold"),
                text_color=accent
            )

            value_label.pack(
                anchor="w",
                padx=18,
                pady=(0, 17)
            )

            self.summary_values[key] = value_label

    def create_toolbar(self):
        """Create search and filtering controls."""

        toolbar = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )

        toolbar.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 15)
        )

        toolbar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="Search transactions...",
            height=38,
            width=260,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )

        self.search_entry.grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=12
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.on_search
        )

        self.type_filter = ctk.CTkOptionMenu(
            toolbar,
            values=["All", "Income", "Expense"],
            width=125,
            height=38,
            command=self.on_type_filter
        )

        self.type_filter.set("All")

        self.type_filter.grid(
            row=0,
            column=1,
            padx=10,
            pady=12
        )

        ctk.CTkButton(
            toolbar,
            text="Refresh",
            width=90,
            height=38,
            fg_color=COLORS["sidebar"],
            hover_color=COLORS["sidebar_hover"],
            command=self.refresh_transactions
        ).grid(
            row=0,
            column=2,
            padx=(5, 15),
            pady=12
        )

    def create_transaction_table(self):
        """Create the transaction data table."""

        table_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        table_frame.grid(
            row=3,
            column=0,
            sticky="nsew"
        )

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()

        style.configure(
            "Finance.Treeview",
            font=(FONT_FAMILY, 10),
            rowheight=38,
            background="#FFFFFF",
            foreground=COLORS["text_primary"],
            fieldbackground="#FFFFFF"
        )

        style.configure(
            "Finance.Treeview.Heading",
            font=(FONT_FAMILY, 10, "bold"),
            background="#F1F5F9",
            foreground=COLORS["text_primary"],
            padding=10
        )

        style.map(
            "Finance.Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", COLORS["text_primary"])]
        )

        columns = (
            "date",
            "title",
            "category",
            "type",
            "payment",
            "amount"
        )

        self.transaction_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Finance.Treeview"
        )

        headings = {
            "date": "DATE",
            "title": "TRANSACTION",
            "category": "CATEGORY",
            "type": "TYPE",
            "payment": "PAYMENT METHOD",
            "amount": "AMOUNT",
        }

        widths = {
            "date": 105,
            "title": 190,
            "category": 135,
            "type": 90,
            "payment": 130,
            "amount": 120,
        }

        for column in columns:

            self.transaction_table.heading(
                column,
                text=headings[column]
            )

            self.transaction_table.column(
                column,
                width=widths[column],
                minwidth=75,
                anchor="e" if column == "amount" else "w"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.transaction_table.yview
        )

        self.transaction_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.transaction_table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(12, 0),
            pady=12
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(0, 12),
            pady=12
        )

        self.transaction_table.tag_configure(
            "income",
            foreground=COLORS["income"]
        )

        self.transaction_table.tag_configure(
            "expense",
            foreground=COLORS["expense"]
        )

        # Double-click a transaction to edit it.
        self.transaction_table.bind(
            "<Double-1>",
            self.on_transaction_double_click
        )

        # Add edit and delete buttons below the table.
        actions_frame = ctk.CTkFrame(
            table_frame,
            fg_color="transparent"
        )

        actions_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="e",
            padx=12,
            pady=(0, 12)
        )

        ctk.CTkButton(
            actions_frame,
            text="Edit Selected",
            width=120,
            height=35,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.edit_selected_transaction
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ctk.CTkButton(
            actions_frame,
            text="Delete Selected",
            width=130,
            height=35,
            fg_color=COLORS["expense"],
            hover_color="#B91C1C",
            command=self.delete_selected_transaction
        ).pack(side="left")

    def on_search(self, event=None):
        """Update transactions when the search changes."""

        self.current_search = self.search_entry.get().strip()
        self.refresh_transactions()

    def on_type_filter(self, selected_value):
        """Update the selected transaction type."""

        self.current_type = selected_value
        self.refresh_transactions()

    def refresh_transactions(self):
        """Load and display saved transactions."""

        transaction_type = None

        if self.current_type == "Income":
            transaction_type = "income"

        elif self.current_type == "Expense":
            transaction_type = "expense"

        try:

            transactions = get_all_transactions(
                transaction_type=transaction_type,
                search=self.current_search or None
            )

            for item in self.transaction_table.get_children():
                self.transaction_table.delete(item)

            for transaction in transactions:

                amount = format_currency(
                    transaction["amount"]
                )

                transaction_type = transaction["transaction_type"]

                self.transaction_table.insert(
                    "",
                    "end",
                    iid=str(transaction["id"]),
                    values=(
                        transaction["transaction_date"],
                        transaction["title"],
                        transaction["category_name"],
                        transaction_type.capitalize(),
                        transaction["payment_method"],
                        amount
                    ),
                    tags=(transaction_type,)
                )

            self.update_summary_cards(transactions)

        except Exception as error:

            messagebox.showerror(
                "Transactions Error",
                f"Unable to load transactions:\n{error}"
            )

    def update_summary_cards(self, transactions):
        """Calculate totals from the displayed transactions."""

        income = sum(
            (
                transaction["amount"]
                for transaction in transactions
                if transaction["transaction_type"] == "income"
            ),
            start=Decimal("0.00")
        )

        expenses = sum(
            (
                transaction["amount"]
                for transaction in transactions
                if transaction["transaction_type"] == "expense"
            ),
            start=Decimal("0.00")
        )

        balance = income - expenses

        self.summary_values["income"].configure(
            text=format_currency(income)
        )

        self.summary_values["expenses"].configure(
            text=format_currency(expenses)
        )

        self.summary_values["balance"].configure(
            text=format_currency(balance)
        )

    def open_add_transaction(self):
        """Open the new transaction form."""

        TransactionForm(
            self,
            title="Add Transaction",
            on_save=self.refresh_transactions
        )

    def edit_selected_transaction(self):
        """Edit the selected transaction."""

        selected = self.transaction_table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a transaction to edit."
            )
            return

        transaction_id = int(selected[0])

        transaction = get_transaction(transaction_id)

        if transaction is None:
            messagebox.showerror(
                "Not Found",
                "This transaction no longer exists."
            )
            self.refresh_transactions()
            return

        TransactionForm(
            self,
            title="Edit Transaction",
            transaction=transaction,
            on_save=self.refresh_transactions
        )

    def on_transaction_double_click(self, event):
        """Open the selected transaction for editing."""

        row_id = self.transaction_table.identify_row(
            event.y
        )

        if not row_id:
            return

        self.transaction_table.selection_set(row_id)
        self.edit_selected_transaction()

    def delete_selected_transaction(self):
        """Delete the selected transaction after confirmation."""

        selected = self.transaction_table.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a transaction to delete."
            )
            return

        transaction_id = int(selected[0])

        transaction = get_transaction(transaction_id)

        if transaction is None:
            messagebox.showerror(
                "Not Found",
                "This transaction no longer exists."
            )
            self.refresh_transactions()
            return

        confirmed = messagebox.askyesno(
            "Confirm Deletion",
            (
                f"Are you sure you want to delete "
                f"'{transaction['title']}'?\n\n"
                "This action cannot be undone."
            )
        )

        if not confirmed:
            return

        try:

            delete_transaction(transaction_id)

            messagebox.showinfo(
                "Deleted",
                "Transaction deleted successfully."
            )

            self.refresh_transactions()

        except Exception as error:

            messagebox.showerror(
                "Deletion Error",
                str(error)
            )


class TransactionForm(ctk.CTkToplevel):
    """Add or edit a transaction."""

    def __init__(
        self,
        parent,
        title,
        transaction=None,
        on_save=None
    ):
        super().__init__(parent)

        self.transaction = transaction
        self.on_save = on_save

        self.title(title)
        self.geometry("520x780")
        self.resizable(False, False)

        self.configure(
            fg_color=COLORS["background"]
        )

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)

        # Form heading.
        ctk.CTkLabel(
            self,
            text=title,
            font=(FONT_FAMILY, 23, "bold"),
            text_color=COLORS["text_primary"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=30,
            pady=(25, 20)
        )

        # Transaction type.
        self.create_label("Transaction Type", 1)

        self.type_option = ctk.CTkOptionMenu(
            self,
            values=["Income", "Expense"],
            width=460,
            height=38,
            command=self.on_type_changed
        )

        self.type_option.grid(
            row=2,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew"
        )

        # Transaction title.
        self.create_label("Transaction Title", 3)

        self.title_entry = self.create_entry(
            "e.g. Monthly Salary",
            4
        )

        # Amount.
        self.create_label("Amount (LKR)", 5)

        self.amount_entry = self.create_entry(
            "e.g. 50000.00",
            6
        )

        # Category.
        self.create_label("Category", 7)

        # Category selector and category management button.
        category_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        category_frame.grid(
            row=8,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew"
        )

        category_frame.grid_columnconfigure(0, weight=1)

        self.category_option = ctk.CTkOptionMenu(
            category_frame,
            values=["No categories available"],
            height=38,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )

        self.category_option.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        self.manage_categories_button = ctk.CTkButton(
            category_frame,
            text="Manage",
            width=85,
            height=38,
            fg_color=COLORS["sidebar"],
            hover_color=COLORS["sidebar_hover"],
            command=self.open_category_management
        )

        self.manage_categories_button.grid(
            row=0,
            column=1
        )

        # Transaction date.
        self.create_label("Transaction Date (YYYY-MM-DD)", 9)

        self.date_entry = self.create_entry(
            "2026-11-16",
            10
        )

        # Payment method.
        self.create_label("Payment Method", 11)

        self.payment_option = ctk.CTkOptionMenu(
            self,
            values=[
                "Cash",
                "Bank Transfer",
                "Debit Card",
                "Credit Card",
                "Mobile Payment",
                "Other"
            ],
            width=460,
            height=38
        )

        self.payment_option.grid(
            row=12,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew"
        )

        # Notes.
        self.create_label("Notes (Optional)", 13)

        self.notes_entry = ctk.CTkTextbox(
            self,
            width=460,
            height=75,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=8,
            fg_color=COLORS["surface"],
            text_color=COLORS["text_primary"]
        )

        self.notes_entry.grid(
            row=14,
            column=0,
            padx=30,
            pady=(0, 15),
            sticky="ew"
        )

        # Form buttons.
        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        button_frame.grid(
            row=15,
            column=0,
            padx=30,
            pady=(0, 25),
            sticky="ew"
        )

        button_frame.grid_columnconfigure(
            (0, 1),
            weight=1
        )

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            height=40,
            fg_color="#64748B",
            hover_color="#475569",
            command=self.destroy
        ).grid(
            row=0,
            column=0,
            padx=(0, 8),
            sticky="ew"
        )

        ctk.CTkButton(
            button_frame,
            text="Save Transaction",
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.save_transaction
        ).grid(
            row=0,
            column=1,
            padx=(8, 0),
            sticky="ew"
        )

        # Populate the form when editing.
        if transaction is not None:
            self.populate_form()

        else:
            self.type_option.set("Income")
            self.date_entry.insert(
                0,
                __import__("datetime").date.today().isoformat()
            )

        self.load_categories()

        self.after(100, self.focus_force)

    def create_label(self, text, row):
        """Create a form field label."""

        ctk.CTkLabel(
            self,
            text=text,
            font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            text_color=COLORS["text_primary"]
        ).grid(
            row=row,
            column=0,
            sticky="w",
            padx=30,
            pady=(0, 5)
        )

    def create_entry(self, placeholder, row):
        """Create a form text entry."""

        entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            width=460,
            height=38,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )

        entry.grid(
            row=row,
            column=0,
            padx=30,
            pady=(0, 12),
            sticky="ew"
        )

        return entry

    def populate_form(self):
        """Fill the form with existing transaction data."""

        transaction = self.transaction

        self.type_option.set(
            transaction["transaction_type"].capitalize()
        )

        self.title_entry.insert(
            0,
            transaction["title"]
        )

        self.amount_entry.insert(
            0,
            str(transaction["amount"])
        )

        self.date_entry.insert(
            0,
            transaction["transaction_date"]
        )

        self.payment_option.set(
            transaction["payment_method"]
        )

        self.notes_entry.insert(
            "1.0",
            transaction["notes"] or ""
        )

    def on_type_changed(self, selected_value):
        """Reload categories when transaction type changes."""

        self.load_categories()

    def load_categories(self):
        """Load active categories matching the transaction type."""

        category_type = self.type_option.get().lower()

        # Load active categories, plus inactive ones when editing.
        categories = get_all_categories(
            category_type=category_type,
            include_inactive=self.transaction is not None
        )

        # Store category records using their displayed names.
        self.category_choices = {}

        category_names = []
        selected_category_name = None

        current_category_id = None

        if self.transaction is not None:
            current_category_id = self.transaction["category_id"]

        for category in categories:

            is_active = bool(category["is_active"])

            # Normal active categories can be selected.
            if is_active:

                display_name = category["name"]

                self.category_choices[display_name] = category
                category_names.append(display_name)

                if category["id"] == current_category_id:
                    selected_category_name = display_name

            # Preserve the original inactive category when editing.
            elif category["id"] == current_category_id:

                display_name = (
                    f'{category["name"]} (Inactive - choose another)'
                )

                self.category_choices[display_name] = category
                category_names.append(display_name)

                selected_category_name = display_name

        self.categories = categories

        # Handle an empty category list.
        if not category_names:

            self.category_option.configure(
                values=["No active categories available"]
            )

            self.category_option.set(
                "No active categories available"
        )

            return

        self.category_option.configure(
            values=category_names
        )

        # Preserve the existing category when possible.
        if selected_category_name is not None:

            self.category_option.set(
                selected_category_name
            )

        else:

            self.category_option.set(
                category_names[0]
            )

    def open_category_management(self):
        # Get the main application window before closing this form.
        main_window = self.master.winfo_toplevel()

        # Close the transaction form.
        self.destroy()

        # Navigate to the Categories page.
        main_window.show_page("Categories")

    def save_transaction(self):
        """Validate and save the transaction."""

        try:

            transaction_type = self.type_option.get().lower()

            title = self.title_entry.get().strip()

            amount = self.amount_entry.get().strip()

            category_name = self.category_option.get()

            transaction_date = self.date_entry.get().strip()

            payment_method = self.payment_option.get()

            notes = self.notes_entry.get(
                "1.0",
                "end-1c"
            ).strip()

            # Find the selected category.
            selected_category = self.category_choices.get(
                category_name
            )

            if selected_category is None:
                raise ValueError(
                    "Please create or select an active category."
                )

            # Do not allow inactive categories for new or updated transactions.
            if not bool(selected_category["is_active"]):
                raise ValueError(
                    "This category is inactive.\n\n"
                    "Please select an active category or create a new one."
                )

            # Confirm that the category matches the transaction type.
            if selected_category["category_type"] != transaction_type:
                raise ValueError(
                    "The selected category does not match "
                    "the transaction type."
                )

            # Create a new transaction.
            if self.transaction is None:

                create_transaction(
                    title=title,
                    amount=amount,
                    transaction_type=transaction_type,
                    category_id=selected_category["id"],
                    transaction_date=transaction_date,
                    payment_method=payment_method,
                    notes=notes
                )

            # Update an existing transaction.
            else:

                update_transaction(
                    transaction_id=self.transaction["id"],
                    title=title,
                    amount=amount,
                    transaction_type=transaction_type,
                    category_id=selected_category["id"],
                    transaction_date=transaction_date,
                    payment_method=payment_method,
                    notes=notes
                )

            messagebox.showinfo(
                "Success",
                "Transaction saved successfully.",
                parent=self
            )

            if self.on_save:
                self.on_save()

            self.destroy()

        except ValueError as error:

            messagebox.showwarning(
                "Invalid Transaction",
                str(error),
                parent=self
            )

        except Exception as error:

            messagebox.showerror(
                "Error",
                f"Unable to save transaction:\n{error}",
                parent=self
            )