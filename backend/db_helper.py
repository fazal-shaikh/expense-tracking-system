# backend/db_helper.py
import mysql.connector
from contextlib import contextmanager
from backend.logging_setup import setup_logger

logger = setup_logger('db_helper')

# --- Update these to your DB credentials if different ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "expense_manager"
}
# --------------------------------------------------------

@contextmanager
def get_db_cursor(commit=False):
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        yield cursor
        if commit:
            conn.commit()
    except mysql.connector.Error as e:
        logger.exception("Database error: %s", e)
        raise
    finally:
        if conn:
            conn.close()


def fetch_expenses_for_date(expense_date):
    """
    expense_date: 'YYYY-MM-DD' or a date object (mysql-connector will accept str)
    returns: list of dicts: [{'id':..., 'expense_date':..., 'amount':..., 'category':..., 'notes':...}, ...]
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT id, expense_date, amount, category, notes FROM expenses WHERE expense_date = %s ORDER BY id;",
                (expense_date,)
            )
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        logger.exception("fetch_expenses_for_date failed: %s", e)
        return None


def delete_expenses_for_date(expense_date):
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM expenses WHERE expense_date = %s;", (expense_date,))
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
        with get_db_cursor(commit=True) as cursor:
            sql = "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)"
            values = []
            for e in expenses:
                # sanitize fallback
                amount = e.get("amount", 0)
                category = e.get("category", "")
                notes = e.get("notes", "")
                values.append((expense_date, amount, category, notes))
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
        with get_db_cursor() as cursor:
            cursor.execute(
                '''SELECT category, SUM(amount) as total
                   FROM expenses
                   WHERE expense_date BETWEEN %s AND %s
                   GROUP BY category;''',
                (start_date, end_date)
            )
            data = cursor.fetchall()
            return data
    except Exception as e:
        logger.exception("fetch_expense_summary failed: %s", e)
        return None


if __name__ == "__main__":
    # tiny manual test (only runs locally if you execute this file)
    print(fetch_expenses_for_date("2024-08-01"))
    print(fetch_expense_summary("2024-08-01", "2024-08-05"))
