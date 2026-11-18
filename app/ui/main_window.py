
# ============================================================
# CodeCraft Finance Manager
# Main Application Window
# ============================================================

import customtkinter as ctk

from config import (
    APP_NAME,
    APP_VERSION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    COLORS,
    FONT_FAMILY,
    FONT_SIZE_SMALL,
    FONT_SIZE_NORMAL,
    FONT_SIZE_LARGE,
)

from app.ui.dashboard_view import DashboardView
from app.ui.transactions_view import TransactionsView
from app.ui.categories_view import CategoriesView
from app.ui.budgets_view import BudgetsView
from app.ui.reports_view import ReportsView
from app.ui.backup_view import BackupView
from app.ui.settings_view import SettingsView
from app.ui.about_view import AboutView


class MainWindow(ctk.CTk):
    """Main application window for CodeCraft Finance Manager."""

    def __init__(self):
        super().__init__()

        # Configure the application window.
        self.title(f"{APP_NAME} | v{APP_VERSION}")

        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        self.minsize(
            MIN_WINDOW_WIDTH,
            MIN_WINDOW_HEIGHT
        )

        self.configure(
            fg_color=COLORS["background"]
        )

        # Store navigation information.
        self.navigation_buttons = {}
        self.current_page = None
        self.current_page_name = None

        # Configure the main grid.
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Build the application interface.
        self.create_sidebar()
        self.create_workspace()

        # Display the dashboard initially.
        self.show_page("Dashboard")

    def create_sidebar(self):
        """Create the dark navigation sidebar."""

        self.sidebar = ctk.CTkFrame(
            self,
            width=245,
            corner_radius=0,
            fg_color=COLORS["sidebar"]
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Brand section.
        brand_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        brand_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=22,
            pady=(28, 35)
        )

        ctk.CTkLabel(
            brand_frame,
            text="◈  CODECRAFT",
            font=(
                FONT_FAMILY,
                19,
                "bold"
            ),
            text_color="#FFFFFF"
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_frame,
            text="FINANCE MANAGER",
            font=(
                FONT_FAMILY,
                FONT_SIZE_SMALL,
                "bold"
            ),
            text_color="#8EA9C5"
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # Navigation heading.
        ctk.CTkLabel(
            self.sidebar,
            text="WORKSPACE",
            font=(
                FONT_FAMILY,
                FONT_SIZE_SMALL,
                "bold"
            ),
            text_color="#7890AA"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=24,
            pady=(0, 12)
        )

        # Navigation items.
        navigation_items = [
            ("▦", "Dashboard"),
            ("↔", "Transactions"),
            ("◈", "Categories"),
            ("◷", "Budgets"),
            ("▤", "Reports"),
            ("↻", "Backup & Restore"),
            ("⚙", "Settings"),
            ("ⓘ", "About"),
        ]

        navigation_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        navigation_frame.grid(
            row=2,
            column=0,
            sticky="new",
            padx=12
        )

        # Create clickable navigation buttons.
        for icon, title in navigation_items:

            button = ctk.CTkButton(
                navigation_frame,
                text=f"{icon}    {title}",
                height=43,
                corner_radius=8,
                anchor="w",
                font=(
                    FONT_FAMILY,
                    FONT_SIZE_NORMAL
                ),
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color="#B8C8D9",
                command=lambda page=title: self.show_page(page)
            )

            button.pack(
                fill="x",
                pady=3
            )

            self.navigation_buttons[title] = button

        # Sidebar footer.
        footer = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )

        footer.grid(
            row=3,
            column=0,
            sticky="sew",
            padx=22,
            pady=22
        )

        ctk.CTkLabel(
            footer,
            text="CODECRAFT STUDIO",
            font=(
                FONT_FAMILY,
                10,
                "bold"
            ),
            text_color="#7890AA"
        ).pack(anchor="w")

        ctk.CTkLabel(
            footer,
            text="Personal Finance Workspace",
            font=(
                FONT_FAMILY,
                11
            ),
            text_color="#A8B8C9"
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

    def create_workspace(self):
        """Create the main workspace."""

        self.workspace = ctk.CTkFrame(
            self,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        self.workspace.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.workspace.grid_columnconfigure(0, weight=1)
        self.workspace.grid_rowconfigure(1, weight=1)

        # Build the workspace header.
        self.create_header()

        # Create the page container.
        self.page_container = ctk.CTkFrame(
            self.workspace,
            fg_color="transparent",
            corner_radius=0
        )

        self.page_container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=22
        )

        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

    def create_header(self):
        """Create the top workspace header."""

        header = ctk.CTkFrame(
            self.workspace,
            height=76,
            fg_color=COLORS["surface"],
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border"]
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(
            header,
            text="Personal Finance",
            font=(
                FONT_FAMILY,
                FONT_SIZE_LARGE,
                "bold"
            ),
            text_color=COLORS["text_primary"]
        )

        self.header_title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=30,
            pady=18
        )

        ctk.CTkLabel(
            header,
            text="CODECRAFT FINANCE MANAGER",
            font=(
                FONT_FAMILY,
                FONT_SIZE_SMALL,
                "bold"
            ),
            text_color=COLORS["text_secondary"]
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=30
        )

    def show_page(self, page_name):
        """Display the selected application page."""

        # Only allow navigation to implemented pages.
        available_pages = [
            "Dashboard",
            "Transactions",
            "Categories",
            "Budgets",
            "Reports",
            "Backup & Restore",
            "Settings",
            "About",
        ]

        if page_name not in available_pages:
            return

        # Remove the currently displayed page.
        if self.current_page is not None:
            self.current_page.destroy()

        # -----------------------------------------------------
        # DASHBOARD
        # -----------------------------------------------------

        if page_name == "Dashboard":

            self.current_page = ctk.CTkScrollableFrame(
                self.page_container,
                fg_color="transparent",
                corner_radius=0
            )

            self.current_page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.current_page.grid_columnconfigure(
                0,
                weight=1
            )

            dashboard = DashboardView(
                self.current_page
            )

            dashboard.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.header_title.configure(
                text="Personal Finance"
            )

        # -----------------------------------------------------
        # TRANSACTIONS
        # -----------------------------------------------------

        elif page_name == "Transactions":

            self.current_page = TransactionsView(
                self.page_container
            )

            self.current_page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.header_title.configure(
                text="Transaction Management"
            )

        # -----------------------------------------------------
        # CATEGORIES
        # -----------------------------------------------------

        elif page_name == "Categories":

            self.current_page = CategoriesView(
                self.page_container
            )

            self.current_page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.header_title.configure(
                text="Category Management"
            )

        # -----------------------------------------------------
        # BUDGETS
        # -----------------------------------------------------

        elif page_name == "Budgets":

            self.current_page = BudgetsView(
                self.page_container
            )

            self.current_page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.header_title.configure(
                text="Budget Management"
            )

        # -----------------------------------------------------
        # REPORTS
        # -----------------------------------------------------

        elif page_name == "Reports":

            self.current_page = ReportsView(
                self.page_container
            )

            self.current_page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.header_title.configure(
                text="Financial Reports"
            )

        # -----------------------------------------------------
        # BACKUP & RESTORE
        # -----------------------------------------------------

        elif page_name == "Backup & Restore":

            self.current_page = ctk.CTkScrollableFrame(
                self.page_container,
                fg_color="transparent",
                corner_radius=0
            )

            self.current_page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.current_page.grid_columnconfigure(
                0,
                weight=1
            )

            backup_view = BackupView(
                self.current_page
            )

            backup_view.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.header_title.configure(
                text="Database Backup & Restore"
            )

                    # -----------------------------------------------------
        # SETTINGS
        # -----------------------------------------------------

        elif page_name == "Settings":

            self.current_page = ctk.CTkScrollableFrame(
                self.page_container,
                fg_color="transparent",
                corner_radius=0
            )

            self.current_page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.current_page.grid_columnconfigure(
                0,
                weight=1
            )

            settings_view = SettingsView(
                self.current_page
            )

            settings_view.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.header_title.configure(
                text="Application Settings"
            )

        # -----------------------------------------------------
        # ABOUT
        # -----------------------------------------------------

        elif page_name == "About":

            self.current_page = ctk.CTkScrollableFrame(
                self.page_container,
                fg_color="transparent",
                corner_radius=0
            )

            self.current_page.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.current_page.grid_columnconfigure(
                0,
                weight=1
            )

            about_view = AboutView(
                self.current_page
            )

            about_view.grid(
                row=0,
                column=0,
                sticky="nsew"
            )

            self.header_title.configure(
                text="About CodeCraft Finance Manager"
            )

        self.current_page_name = page_name

        # Update sidebar active states.
        for title, button in self.navigation_buttons.items():

            if title == page_name:

                button.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color="#FFFFFF",
                    font=(
                        FONT_FAMILY,
                        FONT_SIZE_NORMAL,
                        "bold"
                    )
                )

            else:

                button.configure(
                    fg_color="transparent",
                    text_color="#B8C8D9",
                    font=(
                        FONT_FAMILY,
                        FONT_SIZE_NORMAL
                    )
                )
        
                
