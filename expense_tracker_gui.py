# expense_tracker_gui.py
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# -------------------- Assuming modules exist in a subdirectory 'modules' -------------------- #
from modules import budget, charts, data_handler

# -------------------- Setup -------------------- #
if not os.path.exists("visuals"):
    os.makedirs("visuals")

monthly_income = 0
total_fixed = 0
fixed_df, total_fixed = data_handler.load_fixed_expenses()
daily_df = data_handler.load_daily_spending()

if not daily_df.empty:
    daily_df['amount'] = pd.to_numeric(daily_df['amount'], errors='coerce').fillna(0)

# -------------------- Functions -------------------- #
def update_ui():
    """Refreshes the UI elements with current data."""
    global monthly_income, total_fixed, daily_df
    
    fixed_df, total_fixed = data_handler.load_fixed_expenses()
    daily_df = data_handler.load_daily_spending()
    if not daily_df.empty:
        daily_df['amount'] = pd.to_numeric(daily_df['amount'], errors='coerce').fillna(0)
    
    try:
        monthly_income = float(entry_income.get()) if entry_income.get() else 0
    except ValueError:
        monthly_income = 0

    if monthly_income > 0:
        daily_allowance, remaining_budget, daily_remaining_allowance = budget.calculate_daily_allowance(
            monthly_income, total_fixed, daily_df
        )
        lbl_daily_allowance.config(text=f"Daily Allowance: ₹{daily_allowance:.2f} 💸")
        lbl_remaining_budget.config(text=f"Remaining Monthly Budget: ₹{remaining_budget:.2f} 💰")
        
        # Update progress bar
        progress_value = (daily_allowance - daily_remaining_allowance) / daily_allowance * 100 if daily_allowance > 0 else 0
        progress_bar['value'] = progress_value
        progress_text.set(f"{progress_value:.0f}% used today")

        # Dynamic color for remaining budget
        if remaining_budget < 0:
            lbl_remaining_budget.config(style="Red.TLabel")
        else:
            lbl_remaining_budget.config(style="Green.TLabel")
    else:
        # Reset labels if no income is set
        lbl_daily_allowance.config(text="Daily Allowance: ₹0.00 💸")
        lbl_remaining_budget.config(text="Remaining Monthly Budget: ₹0.00 💰")
        lbl_remaining_budget.config(style="Green.TLabel")
        progress_bar['value'] = 0
        progress_text.set("0% used today")

    lbl_total_fixed.config(text=f"Total Fixed Expenses: ₹{total_fixed:.2f} 🧾")
    
    # Update charts
    plot_daily_spending()
    plot_category_expenses()


def add_budget():
    """Set monthly income and add fixed expenses."""
    global monthly_income, total_fixed, fixed_df
    try:
        income_str = entry_income.get().strip()
        if income_str:
            monthly_income = float(income_str)
        
        name = entry_fixed_name.get().strip()
        amt_str = entry_fixed_amount.get().strip()
        if name and amt_str:
            amt = float(amt_str)
            record = {'category': name, 'amount': amt}
            data_handler.save_fixed_expenses(record)
            messagebox.showinfo("Fixed Expense Added", f"✨ {name} - ₹{amt} added.")
            entry_fixed_name.delete(0, tk.END)
            entry_fixed_amount.delete(0, tk.END)
        
        update_ui()
    except ValueError:
        messagebox.showerror("Error", "🚫 Enter valid numbers for income and fixed expenses.")


def add_daily():
    """Add today's spending with category and alert if overspent."""
    global monthly_income, total_fixed
    if monthly_income <= 0:
        messagebox.showwarning("Warning", "⚠️ Set monthly income first!")
        return
    try:
        amt = float(entry_amount.get())
        cat = entry_category.get().strip()
        if not cat:
            messagebox.showerror("Error", "🚫 Enter a category for your expense.")
            return
        
        # Check for overspending before saving
        daily_df = data_handler.load_daily_spending()
        daily_df['amount'] = pd.to_numeric(daily_df['amount'], errors='coerce').fillna(0)
        daily_allowance, _, _ = budget.calculate_daily_allowance(monthly_income, total_fixed, daily_df)
        
        today_date = str(datetime.today().date())
        current_today_spending = daily_df[daily_df['date'] == today_date]['amount'].sum()
        
        if (current_today_spending + amt) > daily_allowance:
            messagebox.showwarning("Daily Budget Status", "🚨 Whoa, this will put you over your daily budget!")
        else:
            messagebox.showinfo("Daily Budget Status", "✅ You're doing great! Keep it up.")
            
        record = {'date': datetime.today().date(), 'amount': amt, 'category': cat}
        data_handler.save_daily_record(record)
        
        entry_amount.delete(0, tk.END)
        entry_category.delete(0, tk.END)
        update_ui()
    except ValueError:
        messagebox.showerror("Error", "🚫 Enter a valid number for amount.")


def check_expected():
    """Check expected spending for upcoming days."""
    global monthly_income, total_fixed
    if monthly_income <= 0:
        messagebox.showwarning("Warning", "⚠️ Set monthly income first!")
        return
    try:
        days = int(entry_days.get())
        expected_total = float(entry_expected.get())
        daily_df = data_handler.load_daily_spending()
        daily_df['amount'] = pd.to_numeric(daily_df['amount'], errors='coerce').fillna(0)
        remaining_budget = monthly_income - total_fixed - daily_df['amount'].sum()
        
        if expected_total / days > remaining_budget / days:
            messagebox.showwarning("Warning", "⚠️ Your expected spending may cause overspending!")
        else:
            messagebox.showinfo("On Track", "✅ Your expected spending is within budget.")
        
        entry_days.delete(0, tk.END)
        entry_expected.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Error", "🚫 Enter valid numbers.")


def plot_daily_spending():
    """Generates and embeds the daily spending chart."""
    global daily_df, monthly_income, total_fixed
    if monthly_income > 0:
        daily_allowance, _, _ = budget.calculate_daily_allowance(
            monthly_income, total_fixed, daily_df
        )
        charts.plot_daily_spending(daily_df, daily_allowance, daily_fig, daily_ax)
        daily_canvas.draw_idle()
    else:
        # Clear the chart if no income is set
        daily_ax.clear()
        daily_ax.text(0.5, 0.5, "Set your monthly income to see the chart!", ha='center', va='center', fontsize=12)
        daily_ax.set_xticks([])
        daily_ax.set_yticks([])
        daily_canvas.draw_idle()


def plot_category_expenses():
    """Generates and embeds the category expenses chart."""
    global daily_df
    charts.plot_category_expenses(daily_df, category_fig, category_ax)
    category_canvas.draw_idle()


# -------------------- GUI Setup -------------------- #
root = tk.Tk()
root.title("💰 Student Expense Tracker 💰")
root.geometry("1100x700")
root.configure(bg="#E8F0F5")

# --- Add Application Logo to Title Bar ---
try:
    logo_path = os.path.join("visuals", "logo.png")
    if os.path.exists(logo_path):
        logo_icon = tk.PhotoImage(file=logo_path)
        root.iconphoto(False, logo_icon)
except Exception as e:
    print(f"Failed to load application icon: {e}")

# --- Styles ---
s = ttk.Style()
s.theme_use('clam')
s.configure('TFrame', background='#E8F0F5', borderwidth=0, relief='flat')
s.configure('TLabel', background='#E8F0F5', font=('Arial', 12), foreground='#212529')
s.configure('Red.TLabel', foreground="#C0392B")
s.configure('Green.TLabel', foreground="#27AE60")
s.configure('Buddy.TLabel', foreground='#2980B9', background='#E8F0F5')
s.configure('TButton', font=('Arial', 14, 'bold'), borderwidth=0, relief='flat', foreground='white', padding=12)
s.map('TButton',
      background=[('active', '#1ABC9C'), ('!disabled', '#2ECC71')],
      foreground=[('active', 'white'), ('!disabled', 'white')])

# --- New styles for card backgrounds ---
s.configure('Card.TFrame', background='#F8F9FA', borderwidth=0, relief='flat', padding=10)
s.map('Card.TFrame', background=[('active', '#F8F9FA')])
s.configure('InputCard.TFrame', background='#FFFFFF', borderwidth=1, relief='solid', bordercolor="#E5E9EC", padding=15)
s.configure('InputLabel.TLabel', background='#FFFFFF', font=('Arial', 12), foreground="#002953")

# --- Progressbar styling fix ---
s.configure('TProgressbar', troughcolor='#CFD8DC', background='#3498DB')

# --- Main Layout ---
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# Container for logo and titles
header_frame = ttk.Frame(main_frame, style='TFrame')
header_frame.pack(fill=tk.X, pady=(0, 20), anchor=tk.W)

# Add Logo to the top-left of the application
logo_path_inline = os.path.join("visuals", "logo.png")
if os.path.exists(logo_path_inline):
    try:
        logo_image = tk.PhotoImage(file=logo_path_inline)
        resized_logo_image = logo_image.subsample(4, 4)
        logo_label = ttk.Label(header_frame, image=resized_logo_image, background='#E8F0F5')
        logo_label.image = resized_logo_image 
        logo_label.pack(side=tk.LEFT, anchor="w", padx=(0, 10))
    except Exception as e:
        print(f"Failed to load inline logo image: {e}")

# Main Title and Subtitle Section
title_container_frame = ttk.Frame(header_frame, style='TFrame')
title_container_frame.pack(side=tk.LEFT, fill=tk.Y)

title_label_container = ttk.Frame(title_container_frame, style='TFrame')
title_label_container.pack(pady=(10, 0), anchor=tk.W)

title_label_pocket = ttk.Label(title_label_container, text="Pocket", font=("Arial", 28, "bold"), foreground="#2C3E50")
title_label_pocket.pack(side=tk.LEFT)
title_label_buddy = ttk.Label(title_label_container, text="Buddy", font=("Arial", 28, "bold"), style="Buddy.TLabel")
title_label_buddy.pack(side=tk.LEFT)

subtitle_label = ttk.Label(title_container_frame, text="Track your money like a boss! 😎", font=("Arial", 16), foreground="#7F8C8D")
subtitle_label.pack(anchor=tk.W)

# Stats Card
stats_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=20)
stats_frame.pack(fill=tk.X, pady=(0, 20))
s.configure('Card.TFrame', background="#F8F9FA", borderwidth=1, relief='solid', bordercolor="#003355")
s.map('Card.TFrame', background=[('active', '#F8F9FA')])

# Add a progress bar and labels to the stats frame
lbl_daily_allowance = ttk.Label(stats_frame, text="Daily Allowance: ₹0.00 💸", font=("Arial", 16, "bold"), foreground="#34495E", background='#F8F9FA')
lbl_daily_allowance.pack(pady=(0, 5), anchor=tk.W)
lbl_remaining_budget = ttk.Label(stats_frame, text="Remaining Monthly Budget: ₹0.00 💰", font=("Arial", 16, "bold"), style="Green.TLabel", background='#F8F9FA')
lbl_remaining_budget.pack(pady=(0, 10), anchor=tk.W)

# Create a progress bar with a label
progress_frame = ttk.Frame(stats_frame, style='TFrame')
progress_frame.pack(fill=tk.X, pady=(5, 0))
progress_text = tk.StringVar(value="0% used today")
progress_label = ttk.Label(progress_frame, textvariable=progress_text, font=("Arial", 12), background='#F8F9FA')
progress_label.pack(side=tk.LEFT, padx=(0, 10))
progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)


# Main content frame for inputs and charts
content_frame = ttk.Frame(main_frame, style='TFrame')
content_frame.pack(fill=tk.BOTH, expand=True)

# Left panel for input forms
left_panel = ttk.Frame(content_frame, style='TFrame', padding=10)
left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

# --- Monthly Budget Card ---
frame_budget = ttk.LabelFrame(left_panel, text="✨ Monthly Budget", padding=20, style='InputCard.TFrame')
frame_budget.pack(pady=10, fill=tk.X)
ttk.Label(frame_budget, text="Monthly Income (₹):", font=("Arial", 12, "bold"), style='InputLabel.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_income = ttk.Entry(frame_budget)
entry_income.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
ttk.Label(frame_budget, text="Fixed Expense Name:", font=("Arial", 12, "bold"), style='InputLabel.TLabel').grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_fixed_name = ttk.Entry(frame_budget)
entry_fixed_name.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
ttk.Label(frame_budget, text="Fixed Expense Amount (₹):", font=("Arial", 12, "bold"), style='InputLabel.TLabel').grid(row=2, column=0, sticky="w", padx=5, pady=5)
entry_fixed_amount = ttk.Entry(frame_budget)
entry_fixed_amount.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
btn_add_budget = ttk.Button(frame_budget, text="➕ Add / Set Budget", command=add_budget)
btn_add_budget.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
lbl_total_fixed = ttk.Label(frame_budget, text=f"Total Fixed Expenses: ₹{total_fixed:.2f} 🧾", font=("Arial", 12, "bold"), style='InputLabel.TLabel')
lbl_total_fixed.grid(row=4, column=0, columnspan=2, pady=(0, 5))

# --- Daily Spending Card ---
frame_expense = ttk.LabelFrame(left_panel, text="🗓️ Daily Spending", padding=20, style='InputCard.TFrame')
frame_expense.pack(pady=10, fill=tk.X)
ttk.Label(frame_expense, text="Amount spent today (₹):", font=("Arial", 12, "bold"), style='InputLabel.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_amount = ttk.Entry(frame_expense)
entry_amount.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
ttk.Label(frame_expense, text="Category:", font=("Arial", 12, "bold"), style='InputLabel.TLabel').grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_category = ttk.Entry(frame_expense)
entry_category.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
btn_add_daily = ttk.Button(frame_expense, text="💸 Add Today's Spending", command=add_daily)
btn_add_daily.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

# --- Expected Spending Card ---
frame_expected = ttk.LabelFrame(left_panel, text="🔮 Expected Spending", padding=20, style='InputCard.TFrame')
frame_expected.pack(pady=10, fill=tk.X)
ttk.Label(frame_expected, text="Days ahead:", font=("Arial", 12, "bold"), style='InputLabel.TLabel').grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_days = ttk.Entry(frame_expected)
entry_days.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
ttk.Label(frame_expected, text="Total Expected Spending (₹):", font=("Arial", 12, "bold"), style='InputLabel.TLabel').grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_expected = ttk.Entry(frame_expected)
entry_expected.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
btn_check_expected = ttk.Button(frame_expected, text="✅ Check Expected Spending", command=check_expected)
btn_check_expected.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

# Right panel for charts
right_panel = ttk.Frame(content_frame, style='TFrame', padding=10)
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

# --- Daily Spending Chart ---
daily_chart_frame = ttk.LabelFrame(right_panel, text="📊 Daily Spending Chart", padding=10)
daily_chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
daily_fig, daily_ax = plt.subplots(figsize=(5, 3), facecolor="#E8F0F5")
daily_canvas = FigureCanvasTkAgg(daily_fig, master=daily_chart_frame)
daily_canvas_widget = daily_canvas.get_tk_widget()
daily_canvas_widget.pack(fill=tk.BOTH, expand=True)

# --- Category Chart ---
category_chart_frame = ttk.LabelFrame(right_panel, text="📈 Category Breakdown", padding=10)
category_chart_frame.pack(fill=tk.BOTH, expand=True)
category_fig, category_ax = plt.subplots(figsize=(5, 3), facecolor="#E8F0F5")
category_canvas = FigureCanvasTkAgg(category_fig, master=category_chart_frame)
category_canvas_widget = category_canvas.get_tk_widget()
category_canvas_widget.pack(fill=tk.BOTH, expand=True)

# Initial UI Update
update_ui()

root.mainloop()