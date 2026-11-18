
# ============================================================
# CodeCraft Finance Manager
# Backup and Restore Interface
# ============================================================

import customtkinter as ctk

from datetime import datetime
from pathlib import Path

from tkinter import filedialog, messagebox

from config import (
    BASE_DIR,
    DATABASE_PATH,
    COLORS,
    FONT_FAMILY,
    FONT_SIZE_SMALL,
    FONT_SIZE_NORMAL,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_LARGE,
)

from app.services.backup_service import (
    create_database_backup,
    restore_database_backup,
)


# Default backup directory.
BACKUP_DIR = BASE_DIR / "backups"


class BackupView(ctk.CTkFrame):
    """Database backup and restore management page."""

    def __init__(self, parent):

        super().__init__(
            parent,
            fg_color="transparent"
        )

        self.grid_columnconfigure(0, weight=1)

        self.create_interface()
        self.refresh_backup_list()

    def create_interface(self):
        """Build the backup and restore interface."""

        # Page introduction.
        ctk.CTkLabel(
            self,
            text="Database Backup & Restore",
            font=(
                FONT_FAMILY,
                FONT_SIZE_LARGE,
                "bold"
            ),
            text_color=COLORS["text_primary"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 8)
        )

        ctk.CTkLabel(
            self,
            text=(
                "Protect your financial records by creating "
                "database backups and restoring previous copies."
            ),
            font=(
                FONT_FAMILY,
                FONT_SIZE_NORMAL
            ),
            text_color=COLORS["text_secondary"],
            wraplength=850,
            justify="left"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 22)
        )

        # -----------------------------------------------------
        # CREATE BACKUP SECTION
        # -----------------------------------------------------

        backup_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        backup_card.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        backup_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            backup_card,
            text="Create a Backup",
            font=(
                FONT_FAMILY,
                FONT_SIZE_MEDIUM,
                "bold"
            ),
            text_color=COLORS["text_primary"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(20, 8)
        )

        ctk.CTkLabel(
            backup_card,
            text=(
                "Save your current categories, transactions, "
                "and budgets into a separate database file."
            ),
            font=(
                FONT_FAMILY,
                FONT_SIZE_NORMAL
            ),
            text_color=COLORS["text_secondary"],
            wraplength=800,
            justify="left"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 16)
        )

        ctk.CTkButton(
            backup_card,
            text="Create Database Backup",
            width=220,
            height=40,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(
                FONT_FAMILY,
                FONT_SIZE_NORMAL,
                "bold"
            ),
            command=self.create_backup
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 22)
        )

        # -----------------------------------------------------
        # RESTORE BACKUP SECTION
        # -----------------------------------------------------

        restore_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        restore_card.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 18)
        )

        restore_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            restore_card,
            text="Restore a Backup",
            font=(
                FONT_FAMILY,
                FONT_SIZE_MEDIUM,
                "bold"
            ),
            text_color=COLORS["text_primary"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(20, 8)
        )

        ctk.CTkLabel(
            restore_card,
            text=(
                "Replace your current financial database with "
                "a previously created backup."
            ),
            font=(
                FONT_FAMILY,
                FONT_SIZE_NORMAL
            ),
            text_color=COLORS["text_secondary"],
            wraplength=800,
            justify="left"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 8)
        )

        ctk.CTkLabel(
            restore_card,
            text=(
                "Important: Restoring replaces the current "
                "financial records. A safety backup will be "
                "created automatically before restoration."
            ),
            font=(
                FONT_FAMILY,
                FONT_SIZE_SMALL
            ),
            text_color=COLORS["expense"],
            wraplength=800,
            justify="left"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 16)
        )

        ctk.CTkButton(
            restore_card,
            text="Select Backup to Restore",
            width=220,
            height=40,
            corner_radius=8,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary_hover"],
            font=(
                FONT_FAMILY,
                FONT_SIZE_NORMAL,
                "bold"
            ),
            command=self.restore_backup
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=22,
            pady=(0, 22)
        )

        # -----------------------------------------------------
        # EXISTING BACKUPS SECTION
        # -----------------------------------------------------

        history_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        history_card.grid(
            row=4,
            column=0,
            sticky="ew"
        )

        history_card.grid_columnconfigure(0, weight=1)

        history_header = ctk.CTkFrame(
            history_card,
            fg_color="transparent"
        )

        history_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=22,
            pady=(18, 10)
        )

        history_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            history_header,
            text="Available Backups",
            font=(
                FONT_FAMILY,
                FONT_SIZE_MEDIUM,
                "bold"
            ),
            text_color=COLORS["text_primary"]
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkButton(
            history_header,
            text="Refresh",
            width=90,
            height=30,
            corner_radius=7,
            fg_color=COLORS["surface"],
            hover_color=COLORS["surface_hover"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"],
            command=self.refresh_backup_list
        ).grid(
            row=0,
            column=1,
            sticky="e"
        )

        self.backup_list_frame = ctk.CTkFrame(
            history_card,
            fg_color="transparent"
        )

        self.backup_list_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=22,
            pady=(0, 20)
        )

        # -----------------------------------------------------
        # DATABASE INFORMATION
        # -----------------------------------------------------

        ctk.CTkLabel(
            self,
            text=f"Application database: {DATABASE_PATH}",
            font=(
                FONT_FAMILY,
                FONT_SIZE_SMALL
            ),
            text_color=COLORS["text_secondary"],
            wraplength=850,
            justify="left"
        ).grid(
            row=5,
            column=0,
            sticky="w",
            pady=(18, 0)
        )

    def create_backup(self):
        """Ask the user for a location and create a backup."""

        if not DATABASE_PATH.exists():

            messagebox.showerror(
                "Backup Failed",
                "The application database could not be found.",
                parent=self
            )

            return

        BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        suggested_name = (
            f"finance_backup_{timestamp}.db"
        )

        selected_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Finance Database Backup",
            initialdir=str(BACKUP_DIR),
            initialfile=suggested_name,
            defaultextension=".db",
            filetypes=[
                ("SQLite Database", "*.db"),
                ("SQLite Database", "*.sqlite3"),
                ("All Files", "*.*"),
            ]
        )

        if not selected_path:
            return

        try:

            backup_path = create_database_backup(
                selected_path
            )

            self.refresh_backup_list()

            messagebox.showinfo(
                "Backup Successful",
                (
                    "Your database backup was created successfully.\n\n"
                    f"Location:\n{backup_path}"
                ),
                parent=self
            )

        except Exception as error:

            messagebox.showerror(
                "Backup Failed",
                str(error),
                parent=self
            )

    def restore_backup(self):
        """Restore a selected database backup safely."""

        selected_path = filedialog.askopenfilename(
            parent=self,
            title="Select Finance Database Backup",
            initialdir=str(BACKUP_DIR),
            filetypes=[
                ("SQLite Database", "*.db *.sqlite3"),
                ("All Files", "*.*"),
            ]
        )

        if not selected_path:
            return

        backup_path = Path(selected_path).resolve()

        # Ask for confirmation before replacing data.
        confirmed = messagebox.askyesno(
            "Confirm Database Restoration",
            (
                "WARNING: Restoring this backup will replace "
                "your current financial records.\n\n"
                "The application will first create a safety "
                "backup of your current database.\n\n"
                "Do you want to continue?"
            ),
            icon="warning",
            parent=self
        )

        if not confirmed:
            return

        try:

            # Make sure the backup directory exists.
            BACKUP_DIR.mkdir(
                parents=True,
                exist_ok=True
            )

            # Create a safety backup before restoration.
            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            safety_backup_path = (
                BACKUP_DIR
                / f"pre_restore_{timestamp}.db"
            )

            create_database_backup(
                safety_backup_path
            )

            # Restore the selected database.
            restore_database_backup(
                backup_path
            )

            self.refresh_backup_list()

            messagebox.showinfo(
                "Restoration Successful",
                (
                    "Your database has been restored successfully.\n\n"
                    "The application will now close. "
                    "Please reopen it to reload the restored data.\n\n"
                    f"Safety backup:\n{safety_backup_path}"
                ),
                parent=self
            )

            # Close the application so no page continues
            # displaying data from before restoration.
            self.winfo_toplevel().destroy()

        except Exception as error:

            messagebox.showerror(
                "Restoration Failed",
                (
                    "The database could not be restored.\n\n"
                    f"Details: {error}"
                ),
                parent=self
            )

    def refresh_backup_list(self):
        """Display backups saved in the default backup folder."""

        if not hasattr(self, "backup_list_frame"):
            return

        for widget in self.backup_list_frame.winfo_children():
            widget.destroy()

        BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        backup_files = sorted(
            [
                path
                for path in BACKUP_DIR.iterdir()
                if path.is_file()
                and path.suffix.lower() in (".db", ".sqlite3")
            ],
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        if not backup_files:

            ctk.CTkLabel(
                self.backup_list_frame,
                text="No backups found yet.",
                font=(
                    FONT_FAMILY,
                    FONT_SIZE_NORMAL
                ),
                text_color=COLORS["text_secondary"]
            ).pack(
                anchor="w",
                pady=12
            )

            return

        for backup_file in backup_files:

            backup_row = ctk.CTkFrame(
                self.backup_list_frame,
                fg_color=COLORS["background"],
                corner_radius=8
            )

            backup_row.pack(
                fill="x",
                pady=4
            )

            backup_row.grid_columnconfigure(
                0,
                weight=1
            )

            ctk.CTkLabel(
                backup_row,
                text=backup_file.name,
                font=(
                    FONT_FAMILY,
                    FONT_SIZE_NORMAL,
                    "bold"
                ),
                text_color=COLORS["text_primary"]
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=12,
                pady=(9, 2)
            )

            modified_time = datetime.fromtimestamp(
                backup_file.stat().st_mtime
            ).strftime("%d %b %Y, %I:%M %p")

            file_size = backup_file.stat().st_size / 1024

            ctk.CTkLabel(
                backup_row,
                text=(
                    f"{modified_time}  |  "
                    f"{file_size:.1f} KB"
                ),
                font=(
                    FONT_FAMILY,
                    FONT_SIZE_SMALL
                ),
                text_color=COLORS["text_secondary"]
            ).grid(
                row=1,
                column=0,
                sticky="w",
                padx=12,
                pady=(0, 9)
            )
