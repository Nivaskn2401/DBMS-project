# Libra Library Management System (Mac)

A local library-management app built with Streamlit and SQLite.

## Features
- Dashboard with catalogue, members, availability, active loans and overdue loans.
- Books: add, search, edit, delete and export to CSV.
- Members: register, search, edit, delete and export to CSV.
- Issue and return books while updating available stock.
- Transaction history with search and CSV export.
- Confirmation required for destructive deletes; related loan history is also deleted to keep referential integrity valid.
- Existing SQLite database is bundled with the project.

## Run on macOS
1. Extract the ZIP.
2. Double-click `Start_Libra.command`.
3. If blocked, right-click `Start_Libra.command` and select **Open**.
4. First run needs internet to install dependencies.
5. Open `http://localhost:8501` if the browser does not open automatically.
6. Keep Terminal open while using the app; press Control+C there to stop it.

## Data and safety
Data is stored in `library_db.sqlite3` in this folder. Back it up periodically. Deleting a book or member permanently deletes its related issue/return history, after a confirmation checkbox.
