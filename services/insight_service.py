from datetime import datetime
import calendar
import pandas as pd
 
 
def calculate_daily_allowance(monthly_income, total_fixed, daily_df):
    """Calculates the remaining daily allowance based on the budget."""
    today = datetime.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = today.day
 
    remaining_budget = monthly_income - total_fixed
 
    if not daily_df.empty:
        total_spent = daily_df["amount"].sum()
        remaining_budget -= total_spent
 
    days_left = days_in_month - days_passed + 1
    daily_allowance = remaining_budget / days_left if days_left > 0 else remaining_budget
 
    today_date = str(today.date())
    today_spending = daily_df[daily_df["date"] == today_date]["amount"].sum()
    daily_remaining_allowance = daily_allowance - today_spending
 
    return daily_allowance, remaining_budget, daily_remaining_allowance
 
 
def get_additional_insights(df: pd.DataFrame) -> list[dict]:
    """Returns structured insight objects with type and message."""
    insights = []
 
    if df.empty:
        return insights
 
    category_spend = df.groupby("category")["amount"].sum()
    top_category = category_spend.idxmax()
    top_amount = int(category_spend.max())
 
    # Warning: top spending category
    insights.append({
        "type": "warn",
        "message": (
            f"You are spending most on <strong>{top_category}</strong> "
            f"(₹{top_amount:,}). Review if this aligns with your budget."
        ),
    })
 
    # Alert: unusually high individual expenses
    avg_spend = df["amount"].mean()
    high_spends = df[df["amount"] > avg_spend * 2]
    if not high_spends.empty:
        insights.append({
            "type": "alert",
            "message": (
                f"You have <strong>{len(high_spends)}</strong> unusually high "
                "expense(s) — more than 2× your average. Consider reviewing them."
            ),
        })
 
    # Warning: overall high spending
    total = df["amount"].sum()
    if total > 8000:
        insights.append({
            "type": "warn",
            "message": (
                "Your total spending is relatively high. "
                "Try reducing non-essential expenses to boost savings."
            ),
        })
 
    # Positive: low transaction count (disciplined spending)
    if len(df) < 20:
        insights.append({
            "type": "good",
            "message": (
                f"Great discipline! Only <strong>{len(df)}</strong> transactions "
                "recorded — you're keeping a tight rein on spending."
            ),
        })
 
    # Tip: daily reduction math
    days_remaining = (
        calendar.monthrange(datetime.today().year, datetime.today().month)[1]
        - datetime.today().day
    )
    if days_remaining > 0:
        savings_per_day = 100
        projected_savings = savings_per_day * days_remaining
        insights.append({
            "type": "tip",
            "message": (
                f"Cutting just <strong>₹100/day</strong> for the remaining "
                f"{days_remaining} days saves you ₹{projected_savings:,} this month."
            ),
        })
 
    return insights
 
 
def get_summary(file_path: str) -> dict:
    """Reads the daily spending CSV and returns a summary dict for the dashboard."""
    df = pd.read_csv(file_path)
    df = df.dropna(subset=["amount", "category"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
 
    total_spent = int(df["amount"].sum())
    category_spend = df.groupby("category")["amount"].sum()
    top_category = category_spend.idxmax() if not category_spend.empty else "N/A"
    avg_daily = int(df["amount"].mean()) if not df.empty else 0
    num_transactions = len(df)
    insights = get_additional_insights(df)
 
    return {
        "total_spent": f"{total_spent:,}",
        "top_category": top_category,
        "category_breakdown": {k: int(v) for k, v in category_spend.to_dict().items()},
        "avg_daily": f"{avg_daily:,}",
        "num_transactions": num_transactions,
        "insights": insights,
    }