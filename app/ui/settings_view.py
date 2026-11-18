
# ============================================================
# CodeCraft Finance Manager
# Settings View
# ============================================================

import customtkinter as ctk

from tkinter import messagebox

from config import (
    APP_NAME,
    APP_VERSION,
    COLORS,
    FONT_FAMILY,
)

from app.services.settings_service import (
    load_settings,
    save_settings,
    reset_settings,
    AVAILABLE_CURRENCIES,
    AVAILABLE_APPEARANCES,
)


class SettingsView(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(
            master,
            fg_color="transparent"
        )

        # Load the currently saved settings.
        self.current_settings = load_settings()

        # Create variables for the settings controls.
        self.currency_variable = ctk.StringVar(
            value=self.current_settings["currency"]
        )

        self.appearance_variable = ctk.StringVar(
            value=self.current_settings["appearance"]
        )

        # Build the settings interface.
        self.create_interface()

    # ========================================================
    # MAIN INTERFACE
    # ========================================================

    def create_interface(self):

        # Main heading.
        heading = ctk.CTkLabel(
            self,
            text="Application Settings",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLORS["text_primary"]
        )

        heading.pack(
            anchor="w",
            pady=(0, 6)
        )

        description = ctk.CTkLabel(
            self,
            text="Manage your application preferences.",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["text_secondary"]
        )

        description.pack(
            anchor="w",
            pady=(0, 24)
        )

        # Create the appearance settings section.
        self.create_appearance_section()

        # Create the currency settings section.
        self.create_currency_section()

        # Create the action buttons.
        self.create_action_buttons()

    # ========================================================
    # APPEARANCE SETTINGS
    # ========================================================

    def create_appearance_section(self):

        section = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        section.pack(
            fill="x",
            pady=(0, 18)
        )

        section.grid_columnconfigure(
            0,
            weight=1
        )

        # Section heading.
        title = ctk.CTkLabel(
            section,
            text="Appearance",
            font=(FONT_FAMILY, 17, "bold"),
            text_color=COLORS["text_primary"]
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(20, 6)
        )

        description = ctk.CTkLabel(
            section,
            text="Choose how CodeCraft Finance Manager looks.",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text_secondary"]
        )

        description.grid(
            row=1,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 16)
        )

        # Appearance selector.
        appearance_label = ctk.CTkLabel(
            section,
            text="Appearance Mode",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text_primary"]
        )

        appearance_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 8)
        )

        self.appearance_menu = ctk.CTkOptionMenu(
            section,
            variable=self.appearance_variable,
            values=AVAILABLE_APPEARANCES,
            width=220,
            height=36
        )

        self.appearance_menu.grid(
            row=3,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 22)
        )

    # ========================================================
    # CURRENCY SETTINGS
    # ========================================================

    def create_currency_section(self):

        section = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        section.pack(
            fill="x",
            pady=(0, 18)
        )

        section.grid_columnconfigure(
            0,
            weight=1
        )

        # Section heading.
        title = ctk.CTkLabel(
            section,
            text="Currency Display",
            font=(FONT_FAMILY, 17, "bold"),
            text_color=COLORS["text_primary"]
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(20, 6)
        )

        description = ctk.CTkLabel(
            section,
            text="Choose the currency label used by the application.",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text_secondary"]
        )

        description.grid(
            row=1,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 16)
        )

        # Currency selector.
        currency_label = ctk.CTkLabel(
            section,
            text="Currency Preference",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["text_primary"]
        )

        currency_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 8)
        )

        self.currency_menu = ctk.CTkOptionMenu(
            section,
            variable=self.currency_variable,
            values=list(AVAILABLE_CURRENCIES.keys()),
            width=220,
            height=36
        )

        self.currency_menu.grid(
            row=3,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 14)
        )

        # Important financial warning.
        warning = ctk.CTkLabel(
            section,
            text=(
                "Important: Your financial records are stored in LKR. "
                "Changing this preference does not convert amounts "
                "or apply exchange rates."
            ),
            font=(FONT_FAMILY, 12),
            text_color=COLORS["warning"],
            wraplength=650,
            justify="left"
        )

        warning.grid(
            row=4,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 22)
        )

    # ========================================================
    # ACTION BUTTONS
    # ========================================================

    def create_action_buttons(self):

        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            pady=(4, 0)
        )

        # Save button.
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Settings",
            width=150,
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.save_user_settings
        )

        save_button.pack(
            side="left",
            padx=(0, 10)
        )

        # Reset button.
        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset to Default",
            width=150,
            height=38,
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"],
            command=self.reset_user_settings
        )

        reset_button.pack(
            side="left"
        )

    # ========================================================
    # SAVE SETTINGS
    # ========================================================

    def save_user_settings(self):

        try:

            # Save the selected preferences.
            saved_settings = save_settings(
                currency=self.currency_variable.get(),
                appearance=self.appearance_variable.get()
            )

            # Apply the selected appearance immediately.
            ctk.set_appearance_mode(
                saved_settings["appearance"]
            )

            # Update the local settings.
            self.current_settings = saved_settings

            messagebox.showinfo(
                "Settings Saved",
                "Your application settings have been saved successfully."
            )

        except (ValueError, OSError) as error:

            messagebox.showerror(
                "Settings Error",
                f"Unable to save settings:\n\n{error}"
            )

    # ========================================================
    # RESET SETTINGS
    # ========================================================

    def reset_user_settings(self):

        confirmation = messagebox.askyesno(
            "Reset Settings",
            (
                "Are you sure you want to reset all application "
                "preferences to their default values?"
            )
        )

        if not confirmation:
            return

        try:

            # Restore the default settings.
            default_settings = reset_settings()

            # Update the controls.
            self.currency_variable.set(
                default_settings["currency"]
            )

            self.appearance_variable.set(
                default_settings["appearance"]
            )

            # Apply the default appearance.
            ctk.set_appearance_mode(
                default_settings["appearance"]
            )

            # Update the local settings.
            self.current_settings = default_settings

            messagebox.showinfo(
                "Settings Reset",
                "Application settings have been restored to their defaults."
            )

        except OSError as error:

            messagebox.showerror(
                "Reset Error",
                f"Unable to reset settings:\n\n{error}"
            )
