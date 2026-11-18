
# CodeCraft Finance Manager

A modern Windows desktop personal finance management application built with Python, CustomTkinter, and SQLite.

**Developed by Shazin Nausar**

## Overview

CodeCraft Finance Manager helps users manage personal income and expenses, monitor monthly budgets, analyse financial activity, and securely back up their financial records.

The application provides a clean desktop interface with financial summaries, charts, transaction management, and reporting tools.

## Features

- **Dashboard:** View income, expenses, balance, transaction statistics, and recent activity.
- **Transaction Management:** Add, edit, delete, search, and filter financial transactions.
- **Category Management:** Organise income and expense categories.
- **Budget Management:** Set monthly expense budgets and monitor spending.
- **Financial Reports:** Analyse financial activity using date ranges, charts, and summaries.
- **CSV Export:** Export report transactions to CSV.
- **Backup & Restore:** Create database backups and restore previous records.
- **Application Settings:** Configure appearance and currency display preferences.
- **About:** View application and developer information.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| CustomTkinter | Desktop user interface |
| SQLite | Local database |
| Matplotlib | Financial charts |
| Pillow | Image processing |
| Pytest | Automated testing |
| PyInstaller | Windows executable packaging |

## Requirements

- Windows 10 or Windows 11
- Python 3.14
- Required packages listed in `requirements.txt`

## Installation

1. Clone the repository:

   ```bash
   git clone YOUR_GITHUB_REPOSITORY_URL
   ```

2. Navigate to the project directory:

   ```bash
   cd CodeCraftFinanceManager
   ```

3. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

4. Activate the virtual environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Start the application:

   ```bash
   python main.py
   ```

## Running Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the complete test suite:

```bash
python -m pytest -v
```

## Data Storage

The application uses a local SQLite database to store financial records.

Database and application settings are maintained locally. Users can create database backups and restore previously saved data through the application.

Financial amounts are stored using integer minor units to avoid floating-point precision problems.

## Currency

The application stores financial records in Sri Lankan Rupees (LKR).

Users can choose between the `LKR` and `Rs.` display formats. Changing the display preference does not convert financial amounts.

## Project Structure

```text
CodeCraftFinanceManager/
│
├── app/
│   ├── assets/
│   │   ├── icons/
│   │   └── images/
│   ├── database/
│   ├── models/
│   ├── services/
│   ├── ui/
│   │   ├── components/
│   │   ├── dialogs/
│   │   └── pages/
│   └── utils/
│
├── backups/
├── data/
├── screenshots/
├── tests/
│
├── config.py
├── main.py
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Testing

The project includes automated tests covering:

- Database operations
- Financial calculations
- Transaction and category services
- Dashboard calculations
- Budget management
- Financial reports
- Application settings
- Database backup and restoration

**Current test status: 96 tests passing.**

## Screenshots

Application screenshots will be added here.

## Developer

**Shazin Nausar**

GitHub: https://github.com/shazinnausar-spec

LinkedIn: https://linkedin.com/in/mohammed-shajin-nausar

## License

This project is currently provided for portfolio and demonstration purposes. A formal license has not yet been selected.
