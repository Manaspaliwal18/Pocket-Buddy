import os
import json
import pandas as pd
from services.insight_service import get_summary


def _load_context(data_dir: str) -> dict:
    """Load financial data as structured context."""
    file_path = os.path.join(data_dir, "daily_spending.csv")

    if not os.path.exists(file_path):
        return {}

    summary = get_summary(file_path)
    return summary


def chat(messages: list[dict], data_dir: str) -> str:
    """
    Rule-based smart chatbot (no API needed)
    """

    if not messages:
        return "Please ask something about your finances."

    user_query = messages[-1]["content"].lower()

    summary = _load_context(data_dir)

    if not summary:
        return "No financial data available."

    total = summary.get("total_spent", 0)
    top_category = summary.get("top_category", "")
    breakdown = summary.get("category_breakdown", {})
    avg = summary.get("avg_daily", 0)

    # 🔥 Smart responses
    if "top" in user_query or "category" in user_query:
        return f"You are spending the most on {top_category}. Try reducing it to save money."

    elif "total" in user_query or "spend" in user_query:
        return f"Your total spending is ₹{total}. Consider tracking unnecessary expenses."

    elif "average" in user_query:
        return f"Your average spending per transaction is ₹{avg}."

    elif "save" in user_query or "reduce" in user_query:
        return f"To save money, reduce spending in {top_category} and focus on essential expenses."

    elif "breakdown" in user_query:
        text = "Here is your category-wise spending:\n"
        for k, v in breakdown.items():
            text += f"- {k}: ₹{v}\n"
        return text

    elif "overspend" in user_query:
        if total > 8000:
            return "Your spending is quite high this month. Try cutting down on non-essential categories."
        else:
            return "Your spending is under control. Keep it up!"

    else:
        return f"Based on your data, your highest spending is in {top_category}. Try optimizing it to improve savings."