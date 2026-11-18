
import customtkinter as ctk
from tkinter import ttk, messagebox

from app.services.category_service import (
    create_category,
    get_all_categories,
    update_category,
    deactivate_category,
)

from config import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE_NORMAL,
    FONT_SIZE_SMALL,
    FONT_SIZE_MEDIUM,
)


class CategoriesView(ctk.CTkFrame):
    """Page for managing income and expense categories."""

    def __init__(self, master):
        super().__init__(
            master,
            fg_color=COLORS["background"]
        )

        # Store the currently selected category type.
        self.current_category_type = "income"

        # Store category records for later actions.
        self.category_lookup = {}

        # Configure the page layout.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.create_header()
        self.create_category_controls()
        self.create_category_table()

        # Load income categories when the page opens.
        self.refresh_categories()

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------

    def create_header(self):
        """Create the page title and description."""

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

        title = ctk.CTkLabel(
            header_frame,
            text="Category Management",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Create and manage your income and expense categories.",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack(anchor="w", pady=(5, 0))

    # ---------------------------------------------------------
    # CATEGORY CONTROLS
    # ---------------------------------------------------------

    def create_category_controls(self):
        """Create category type selector and action buttons."""

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

        # Category type selector.
        self.category_selector = ctk.CTkSegmentedButton(
            controls_frame,
            values=["Income", "Expense"],
            command=self.on_category_type_changed,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"]
        )
        self.category_selector.set("Income")
        self.category_selector.grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=18
        )

        # Add category button.
        self.add_button = ctk.CTkButton(
            controls_frame,
            text="+ Add Category",
            command=self.open_add_category_form,
            width=145,
            height=36,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
        )
        self.add_button.grid(
            row=0,
            column=1,
            padx=(10, 18),
            pady=18
        )

        # Refresh button.
        self.refresh_button = ctk.CTkButton(
            controls_frame,
            text="Refresh",
            command=self.refresh_categories,
            width=90,
            height=36,
            corner_radius=8,
            fg_color=COLORS["sidebar_hover"],
            hover_color=COLORS["sidebar_active"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        self.refresh_button.grid(
            row=0,
            column=2,
            padx=(0, 18),
            pady=18
        )

    # ---------------------------------------------------------
    # CATEGORY TABLE
    # ---------------------------------------------------------

    def create_category_table(self):
        """Create the table displaying available categories."""

        table_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        table_container.grid(
            row=2,
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
            text="Income Categories",
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

        # Configure the table appearance.
        style = ttk.Style()

        style.configure(
            "Categories.Treeview",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            rowheight=38,
            background=COLORS["surface"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["surface"]
        )

        style.configure(
            "Categories.Treeview.Heading",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            background=COLORS["background"],
            foreground=COLORS["text_primary"],
            padding=10
        )

        style.map(
            "Categories.Treeview",
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
        self.category_table = ttk.Treeview(
            tree_frame,
            columns=("name", "status"),
            show="headings",
            style="Categories.Treeview",
            selectmode="browse"
        )

        self.category_table.heading(
            "name",
            text="Category Name"
        )

        self.category_table.heading(
            "status",
            text="Status"
        )

        self.category_table.column(
            "name",
            width=400,
            anchor="w"
        )

        self.category_table.column(
            "status",
            width=150,
            anchor="center"
        )

        self.category_table.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        # Vertical scrollbar.
        scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="vertical",
            command=self.category_table.yview
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.category_table.configure(
            yscrollcommand=scrollbar.set
        )

        # Category row colors.
        self.category_table.tag_configure(
            "active",
            foreground=COLORS["income"]
        )

        self.category_table.tag_configure(
            "inactive",
            foreground=COLORS["text_secondary"]
        )

        # Double-click to edit a category.
        self.category_table.bind(
            "<Double-1>",
            self.edit_selected_category
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

        self.edit_button = ctk.CTkButton(
            actions_frame,
            text="Rename Selected",
            command=self.edit_selected_category,
            width=145,
            height=34,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(FONT_FAMILY, FONT_SIZE_SMALL)
        )
        self.edit_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.deactivate_button = ctk.CTkButton(
            actions_frame,
            text="Deactivate Selected",
            command=self.deactivate_selected_category,
            width=155,
            height=34,
            corner_radius=8,
            fg_color=COLORS["expense"],
            hover_color="#B91C1C",
            font=(FONT_FAMILY, FONT_SIZE_SMALL)
        )
        self.deactivate_button.pack(side="left")

    # ---------------------------------------------------------
    # CATEGORY TYPE
    # ---------------------------------------------------------

    def on_category_type_changed(self, selected_type):
        """Change between income and expense categories."""

        if selected_type == "Income":
            self.current_category_type = "income"
        else:
            self.current_category_type = "expense"

        self.refresh_categories()

    # ---------------------------------------------------------
    # LOAD CATEGORIES
    # ---------------------------------------------------------

    def refresh_categories(self):
        """Load categories from the database."""

        # Update the heading.
        if self.current_category_type == "income":
            self.table_title.configure(
                text="Income Categories"
            )
        else:
            self.table_title.configure(
                text="Expense Categories"
            )

        # Clear existing rows.
        for item in self.category_table.get_children():
            self.category_table.delete(item)

        self.category_lookup.clear()

        try:
            categories = get_all_categories(
                category_type=self.current_category_type,
                include_inactive=True
            )

            # Add categories to the table.
            for category in categories:

                category_id = category["id"]
                category_name = category["name"]
                is_active = bool(category["is_active"])

                status = "Active" if is_active else "Inactive"

                tag = "active" if is_active else "inactive"

                self.category_table.insert(
                    "",
                    "end",
                    iid=str(category_id),
                    values=(category_name, status),
                    tags=(tag,)
                )

                self.category_lookup[category_id] = category

        except Exception as error:
            messagebox.showerror(
                "Category Error",
                f"Unable to load categories.\n\n{error}",
                parent=self
            )

    # ---------------------------------------------------------
    # ADD CATEGORY
    # ---------------------------------------------------------

    def open_add_category_form(self):
        """Open the form for creating a new category."""

        CategoryForm(
            self,
            category_type=self.current_category_type,
            on_success=self.refresh_categories
        )

    # ---------------------------------------------------------
    # EDIT CATEGORY
    # ---------------------------------------------------------

    def edit_selected_category(self, event=None):
        """Rename the selected category."""

        selected_item = self.category_table.selection()

        if not selected_item:
            if event is None:
                messagebox.showwarning(
                    "No Selection",
                    "Please select a category first.",
                    parent=self
                )
            return

        category_id = int(selected_item[0])

        category = self.category_lookup.get(category_id)

        if not category:
            return

        if not bool(category["is_active"]):
            messagebox.showwarning(
                "Inactive Category",
                "Inactive categories cannot be renamed.",
                parent=self
            )
            return

        CategoryForm(
            self,
            category_type=self.current_category_type,
            category=category,
            on_success=self.refresh_categories
        )

    # ---------------------------------------------------------
    # DEACTIVATE CATEGORY
    # ---------------------------------------------------------

    def deactivate_selected_category(self):
        """Deactivate a category without deleting its history."""

        selected_item = self.category_table.selection()

        if not selected_item:
            messagebox.showwarning(
                "No Selection",
                "Please select a category first.",
                parent=self
            )
            return

        category_id = int(selected_item[0])

        category = self.category_lookup.get(category_id)

        if not category:
            return

        if not bool(category["is_active"]):
            messagebox.showinfo(
                "Already Inactive",
                "This category is already inactive.",
                parent=self
            )
            return

        category_name = category["name"]

        confirmed = messagebox.askyesno(
            "Confirm Deactivation",
            (
                f"Are you sure you want to deactivate "
                f"'{category_name}'?\n\n"
                "This category will no longer be available "
                "when creating new transactions.\n\n"
                "Existing transactions will remain unchanged."
            ),
            parent=self
        )

        if not confirmed:
            return

        try:
            deactivate_category(category_id)

            messagebox.showinfo(
                "Category Deactivated",
                f"'{category_name}' has been deactivated.",
                parent=self
            )

            self.refresh_categories()

        except Exception as error:
            messagebox.showerror(
                "Deactivation Error",
                f"Unable to deactivate category.\n\n{error}",
                parent=self
            )


# =============================================================
# CATEGORY FORM
# =============================================================

class CategoryForm(ctk.CTkToplevel):
    """Dialog for adding or renaming a category."""

    def __init__(
        self,
        parent,
        category_type,
        category=None,
        on_success=None
    ):
        super().__init__(parent)

        self.parent = parent
        self.category_type = category_type
        self.category = category
        self.on_success = on_success

        self.is_editing = category is not None

        # Window settings.
        self.title(
            "Rename Category" if self.is_editing
            else "Add Category"
        )

        self.geometry("430x300")
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
        """Create the category input form."""

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
        heading = ctk.CTkLabel(
            container,
            text=(
                "Rename Category" if self.is_editing
                else "Create New Category"
            ),
            font=(FONT_FAMILY, 20, "bold"),
            text_color=COLORS["text_primary"]
        )
        heading.pack(
            anchor="w",
            padx=22,
            pady=(22, 5)
        )

        # Category type.
        type_label = ctk.CTkLabel(
            container,
            text=f"Category Type: {self.category_type.title()}",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["text_secondary"]
        )
        type_label.pack(
            anchor="w",
            padx=22,
            pady=(8, 15)
        )

        # Category name label.
        name_label = ctk.CTkLabel(
            container,
            text="Category Name",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            text_color=COLORS["text_primary"]
        )
        name_label.pack(
            anchor="w",
            padx=22,
            pady=(0, 6)
        )

        # Category name input.
        self.name_entry = ctk.CTkEntry(
            container,
            height=40,
            placeholder_text="Enter category name",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=8
        )
        self.name_entry.pack(
            fill="x",
            padx=22
        )

        # Populate existing category name when editing.
        if self.is_editing:
            self.name_entry.insert(
                0,
                self.category["name"]
            )

        # Buttons.
        buttons_frame = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )
        buttons_frame.pack(
            fill="x",
            padx=22,
            pady=(25, 20)
        )

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            height=36,
            fg_color=COLORS["sidebar_hover"],
            hover_color=COLORS["sidebar_active"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        cancel_button.pack(side="right")

        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save Changes" if self.is_editing else "Create Category",
            command=self.save_category,
            width=145,
            height=36,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
        )
        save_button.pack(
            side="right",
            padx=(0, 10)
        )

        self.name_entry.focus()

    # ---------------------------------------------------------
    # SAVE CATEGORY
    # ---------------------------------------------------------

    def save_category(self):
        """Create a category or update its name."""

        category_name = self.name_entry.get().strip()

        if not category_name:
            messagebox.showwarning(
                "Missing Category Name",
                "Please enter a category name.",
                parent=self
            )
            self.name_entry.focus()
            return

        try:
            if self.is_editing:

                update_category(
                    category_id=self.category["id"],
                    name=category_name
                )

                success_message = "Category renamed successfully."

            else:

                create_category(
                    name=category_name,
                    category_type=self.category_type
                )

                success_message = "Category created successfully."

            messagebox.showinfo(
                "Success",
                success_message,
                parent=self
            )

            # Refresh the parent page.
            if self.on_success:
                self.on_success()

            self.destroy()

        except ValueError as error:
            messagebox.showwarning(
                "Invalid Category",
                str(error),
                parent=self
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"Unable to save category.\n\n{error}",
                parent=self
            )
