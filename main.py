
# ============================================================
# CodeCraft Finance Manager
# Application Entry Point
# ============================================================

import customtkinter as ctk

from config import COLOR_THEME

from app.database.connection import initialize_database
from app.services.settings_service import load_settings
from app.ui.main_window import MainWindow


def main():

    # Initialize the SQLite database.
    initialize_database()

    # Load the user's saved application settings.
    settings = load_settings()

    # Apply the saved appearance preference.
    ctk.set_appearance_mode(settings["appearance"])

    # Configure the default CustomTkinter color theme.
    ctk.set_default_color_theme(COLOR_THEME)

    # Create the main application window.
    app = MainWindow()

    # Start the application event loop.
    app.mainloop()


if __name__ == "__main__":
    main()
