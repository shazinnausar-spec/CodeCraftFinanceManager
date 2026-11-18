
# ============================================================
# CodeCraft Finance Manager
# About View
# ============================================================

import customtkinter as ctk

from config import (
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR,
    COLORS,
    FONT_FAMILY,
)


class AboutView(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="transparent"
        )

        # Build the About page.
        self.create_interface()

    # ========================================================
    # MAIN INTERFACE
    # ========================================================

    def create_interface(self):

        # Page heading.
        heading = ctk.CTkLabel(
            self,
            text="About",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLORS["text_primary"]
        )

        heading.pack(
            anchor="w",
            pady=(0, 6)
        )

        description = ctk.CTkLabel(
            self,
            text="Application information and development details.",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_secondary"]
        )

        description.pack(
            anchor="w",
            pady=(0, 24)
        )

        # Main application information card.
        self.create_application_card()

        # Technology information card.
        self.create_technology_card()

        # Developer information card.
        self.create_developer_card()

    # ========================================================
    # APPLICATION INFORMATION
    # ========================================================

    def create_application_card(self):

        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        card.pack(
            fill="x",
            pady=(0, 18)
        )

        # Application name.
        app_name = ctk.CTkLabel(
            card,
            text=APP_NAME,
            font=(FONT_FAMILY, 25, "bold"),
            text_color=COLORS["primary"]
        )

        app_name.pack(
            anchor="w",
            padx=24,
            pady=(24, 8)
        )

        # Application description.
        app_description = ctk.CTkLabel(
            card,
            text=(
                "A desktop personal finance management application "
                "designed to help users organize transactions, "
                "monitor spending, manage budgets and understand "
                "their financial activity."
            ),
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_secondary"],
            wraplength=700,
            justify="left"
        )

        app_description.pack(
            anchor="w",
            padx=24,
            pady=(0, 16)
        )

        # Version information.
        version = ctk.CTkLabel(
            card,
            text=f"Version {APP_VERSION}",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text_primary"]
        )

        version.pack(
            anchor="w",
            padx=24,
            pady=(0, 24)
        )

    # ========================================================
    # TECHNOLOGY INFORMATION
    # ========================================================

    def create_technology_card(self):

        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        card.pack(
            fill="x",
            pady=(0, 18)
        )

        heading = ctk.CTkLabel(
            card,
            text="Technology Stack",
            font=(FONT_FAMILY, 17, "bold"),
            text_color=COLORS["text_primary"]
        )

        heading.pack(
            anchor="w",
            padx=24,
            pady=(20, 14)
        )

        technologies = [
            ("Programming Language", "Python"),
            ("Graphical Interface", "CustomTkinter"),
            ("Database", "SQLite"),
            ("Data Visualization", "Matplotlib"),
            ("Image Processing", "Pillow"),
            ("Testing Framework", "Pytest"),
        ]

        for label_text, value_text in technologies:

            row = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                padx=24,
                pady=5
            )

            row.grid_columnconfigure(
                0,
                weight=1
            )

            label = ctk.CTkLabel(
                row,
                text=label_text,
                font=(FONT_FAMILY, 12),
                text_color=COLORS["text_secondary"]
            )

            label.grid(
                row=0,
                column=0,
                sticky="w"
            )

            value = ctk.CTkLabel(
                row,
                text=value_text,
                font=(FONT_FAMILY, 12, "bold"),
                text_color=COLORS["text_primary"]
            )

            value.grid(
                row=0,
                column=1,
                sticky="e"
            )

        # Bottom spacing.
        ctk.CTkLabel(
            card,
            text=""
        ).pack(pady=5)

    # ========================================================
    # DEVELOPER INFORMATION
    # ========================================================

    def create_developer_card(self):

        card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        card.pack(
            fill="x"
        )

        heading = ctk.CTkLabel(
            card,
            text="Development",
            font=(FONT_FAMILY, 17, "bold"),
            text_color=COLORS["text_primary"]
        )

        heading.pack(
            anchor="w",
            padx=24,
            pady=(20, 10)
        )

        developer = ctk.CTkLabel(
            card,
            text=f"Developed by {APP_AUTHOR}",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text_primary"]
        )

        developer.pack(
            anchor="w",
            padx=24,
            pady=(0, 8)
        )

        copyright_label = ctk.CTkLabel(
            card,
            text=f"{APP_NAME} | {APP_VERSION}",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text_secondary"]
        )

        copyright_label.pack(
            anchor="w",
            padx=24,
            pady=(0, 22)
        )
