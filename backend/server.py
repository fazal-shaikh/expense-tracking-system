from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from typing import List
from pydantic import BaseModel

from backend import db_helper
from backend.logging_setup import setup_logger

logger = setup_logger("server")

app = FastAPI(title="Expense Tracker API")

# Allow local development origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8501", "http://localhost:3000", "http://127.0.0.1", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Expense(BaseModel):
    amount: float
    category: str
    notes: str = ""


class DateRange(BaseModel):
    start_date: date
    end_date: date


@app.get("/expenses/{expense_date}")
def get_expenses(expense_date: date):
    """
    GET /expenses/2024-08-01
    """
    try:
        rows = db_helper.fetch_expenses_for_date(str(expense_date))
        if rows is None:
            raise HTTPException(status_code=500, detail="Failed to fetch expenses from DB")
        return rows
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("get_expenses error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/expenses/{expense_date}")
def update_expenses(expense_date: date, expenses: List[Expense]):
    """
    Replace expenses for the date.
    The frontend sends a list of Expense objects.
    """
    try:
        # delete old entries for date
        ok = db_helper.delete_expenses_for_date(str(expense_date))
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to delete existing expenses")

        # insert new entries
        payloads = [e.dict() for e in expenses]
        ok2 = db_helper.add_expenses_for_date(str(expense_date), payloads)
        if not ok2:
            raise HTTPException(status_code=500, detail="Failed to insert new expenses")
        return {"message": "Expenses updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("update_expenses error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/analytics/summary")
def analytics_summary(date_range: DateRange):
    """
    POST /analytics/summary with JSON body: {"start_date": "2024-08-01", "end_date": "2024-08-05"}
    returns: { "Shopping": {"total": 100, "percentage": 50.0}, ... }
    """
    try:
        data = db_helper.fetch_expense_summary(str(date_range.start_date), str(date_range.end_date))
        if data is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve expense summary from the database.")

        total = sum([row['total'] for row in data]) if data else 0

        breakdown = {}
        for row in data:
            percentage = (row['total'] / total) * 100 if total != 0 else 0
            breakdown[row['category']] = {"total": float(row['total']), "percentage": float(percentage)}

        return breakdown
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("analytics_summary error: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")
