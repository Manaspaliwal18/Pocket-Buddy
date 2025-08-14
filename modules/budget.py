# modules/budget.py
from datetime import datetime
import calendar

def calculate_daily_allowance(monthly_income, total_fixed, daily_df):
    """Calculates the remaining daily allowance based on the budget."""
    today = datetime.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    days_passed = today.day
    
    remaining_budget = monthly_income - total_fixed
    
    if not daily_df.empty:
        total_spent = daily_df['amount'].sum()
        remaining_budget -= total_spent
    
    # Avoid division by zero if it's the last day of the month
    days_left = days_in_month - days_passed + 1
    daily_allowance = remaining_budget / days_left if days_left > 0 else remaining_budget
    
    today_date = str(today.date())
    today_spending = daily_df[daily_df['date'] == today_date]['amount'].sum()
    daily_remaining_allowance = daily_allowance - today_spending
    
    return daily_allowance, remaining_budget, daily_remaining_allowance