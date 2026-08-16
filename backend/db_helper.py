# backend/db_helper.py
import sqlite3
import os
from contextlib import contextmanager
from backend.logging_setup import setup_logger

logger = setup_logger('db_helper')

# --- MySQL DB Config ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "expense_manager"
}

# SQLite database file path as fallback
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "expense_manager.db")


def init_sqlite_db():
    """Ensure SQLite table exists if SQLite is used."""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                notes TEXT
            );
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.exception("Failed to initialize SQLite database: %s", e)


# Initialize SQLite on import
init_sqlite_db()


@contextmanager
def get_db_cursor(commit=False):
    conn = None
    use_sqlite = False
    
    # Try MySQL connection first if mysql.connector is installed
    try:
        import mysql.connector
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        placeholder = "%s"
    except Exception as mysql_err:
        # Fall back to SQLite
        use_sqlite = True
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        placeholder = "?"

    try:
        yield cursor, placeholder
        if commit:
            conn.commit()
    except Exception as e:
        logger.exception("Database error: %s", e)
        raise
    finally:
        if conn:
            conn.close()


def fetch_expenses_for_date(expense_date):
    """
    expense_date: 'YYYY-MM-DD'
    returns: list of dicts: [{'id':..., 'expense_date':..., 'amount':..., 'category':..., 'notes':...}, ...]
    """
    try:
        with get_db_cursor() as (cursor, ph):
            cursor.execute(
                f"SELECT id, expense_date, amount, category, notes FROM expenses WHERE expense_date = {ph} ORDER BY id;",
                (str(expense_date),)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.exception("fetch_expenses_for_date failed: %s", e)
        return None


def delete_expenses_for_date(expense_date):
    try:
        with get_db_cursor(commit=True) as (cursor, ph):
            cursor.execute(f"DELETE FROM expenses WHERE expense_date = {ph};", (str(expense_date),))
            return True
    except Exception as e:
        logger.exception("delete_expenses_for_date failed: %s", e)
        return False


def add_expenses_for_date(expense_date, expenses):
    """
    expenses: list of dicts with keys: amount, category, notes
    """
    if not isinstance(expenses, list):
        logger.error("add_expenses_for_date: expenses is not a list")
        return False

    try:
        with get_db_cursor(commit=True) as (cursor, ph):
            sql = f"INSERT INTO expenses (expense_date, amount, category, notes) VALUES ({ph}, {ph}, {ph}, {ph})"
            values = []
            for e in expenses:
                amount = float(e.get("amount", 0))
                category = str(e.get("category", ""))
                notes = str(e.get("notes", ""))
                values.append((str(expense_date), amount, category, notes))
            if values:
                cursor.executemany(sql, values)
            return True
    except Exception as e:
        logger.exception("add_expenses_for_date failed: %s", e)
        return False


def fetch_expense_summary(start_date, end_date):
    """
    Returns list of dicts: [{'category': 'Shopping', 'total': 123.45}, ...]
    """
    try:
        with get_db_cursor() as (cursor, ph):
            cursor.execute(
                f'''SELECT category, SUM(amount) as total
                   FROM expenses
                   WHERE expense_date BETWEEN {ph} AND {ph}
                   GROUP BY category;''',
                (str(start_date), str(end_date))
            )
            data = cursor.fetchall()
            return [dict(row) for row in data]
    except Exception as e:
        logger.exception("fetch_expense_summary failed: %s", e)
        return None


if __name__ == "__main__":
    print("Testing fetch:", fetch_expenses_for_date("2024-08-01"))
    print("Testing summary:", fetch_expense_summary("2024-08-01", "2024-08-05"))
