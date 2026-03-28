# modules/charts.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Use a generic sans-serif font family that is universally supported
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']

def plot_daily_spending(daily_df, daily_allowance, fig, ax):
    """Plots daily spending against the daily allowance."""
    if daily_df.empty:
        ax.clear()
        ax.text(0.5, 0.5, "No daily spending data yet!", ha='center', va='center', fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        return
        
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    daily_spending_by_day = daily_df.groupby(daily_df['date'].dt.date)['amount'].sum()
    
    ax.clear()
    bars = ax.bar(daily_spending_by_day.index, daily_spending_by_day.values, color='#3498DB')
    
    # Add daily allowance line
    ax.axhline(y=daily_allowance, color='#E74C3C', linestyle='--', label='Daily Allowance')
    
    # Highlight bars over the allowance
    for bar in bars:
        if bar.get_height() > daily_allowance:
            bar.set_color('#E74C3C')
    
    ax.set_title("Daily Spending vs. Allowance", fontweight="bold", fontsize=14)
    ax.set_ylabel("Amount (₹)")
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    fig.tight_layout()

def plot_category_expenses(daily_df, fig, ax):
    """Plots spending by category."""
    if daily_df.empty:
        ax.clear()
        ax.text(0.5, 0.5, "No category spending data yet!", ha='center', va='center', fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        return

    category_spending = daily_df.groupby('category')['amount'].sum().sort_values(ascending=False)
    
    ax.clear()
    # Use a professional color palette
    colors = ['#3498DB', '#1ABC9C', '#9B59B6', '#F1C40F', '#E67E22']
    bars = ax.bar(category_spending.index, category_spending.values, color=colors[:len(category_spending)])
    
    ax.set_title("Spending by Category", fontweight="bold", fontsize=14)
    ax.set_ylabel("Total Amount (₹)")
    ax.tick_params(axis='x', rotation=45, labelsize=8)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    fig.tight_layout()

