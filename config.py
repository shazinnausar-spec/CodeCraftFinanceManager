
# Application information
APP_NAME = "CodeCraft Finance Manager"
APP_VERSION = "1.0.0"
APP_AUTHOR = "CodeCraft Studio"

# Default application window dimensions
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

# Minimum window dimensions
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 650

# Default financial settings
DEFAULT_CURRENCY = "LKR"
DEFAULT_CURRENCY_SYMBOL = "LKR"

# Application appearance
APPEARANCE_MODE = "light"
COLOR_THEME = "blue"

# Application color palette
COLORS = {
    # Main application colors
    "sidebar": "#14243A",
    "sidebar_hover": "#203650",
    "sidebar_active": "#263F5C",

    # Workspace colors
    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "surface_hover": "#F8FAFD",

    # Accent colors
    "primary": "#3478F6",
    "primary_hover": "#2865D8",
    "secondary": "#17A6C5",
    "accent": "#06B6D4",

    # Financial colors
    "income": "#16A36A",
    "expense": "#E05252",
    "warning": "#E6A23C",

    # Text colors
    "text_primary": "#1D2939",
    "text_secondary": "#667085",
    "text_light": "#FFFFFF",

    # Borders and separators
    "border": "#E5EAF1",
    "divider": "#DCE3EC",
}

# Font settings
FONT_FAMILY = "Segoe UI"

FONT_SIZE_SMALL = 11
FONT_SIZE_NORMAL = 13
FONT_SIZE_MEDIUM = 15
FONT_SIZE_LARGE = 20
FONT_SIZE_TITLE = 26
FONT_SIZE_HEADING = 30

from pathlib import Path

# Get the main project directory.
BASE_DIR = Path(__file__).resolve().parent

# Store the development database inside the data folder.
DATA_DIR = BASE_DIR / "data"

# Full path to the SQLite database.
DATABASE_PATH = DATA_DIR / "finance.db"
