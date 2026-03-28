# modules/data_handler.py
import pandas as pd
import os

FIXED_EXPENSES_FILE = "visuals/fixed_expenses.csv"
DAILY_SPENDING_FILE = "visuals/daily_spending.csv"
CATEGORIES_FILE = "visuals/categories.csv"

def save_fixed_expenses(record):
    """Appends a new fixed expense to the CSV file."""
    try:
        df = load_fixed_expenses()[0]
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=['category', 'amount'])
    
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(FIXED_EXPENSES_FILE, index=False)

def load_fixed_expenses():
    """Loads all fixed expenses from the CSV file."""
    try:
        df = pd.read_csv(FIXED_EXPENSES_FILE)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        total_fixed = df['amount'].sum()
        return df, total_fixed
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['category', 'amount']), 0

def save_daily_record(record):
    """Appends a new daily spending record to the CSV file."""
    try:
        df = load_daily_spending()
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = pd.DataFrame(columns=['date', 'amount', 'category'])
    
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv(DAILY_SPENDING_FILE, index=False)

def load_daily_spending():
    """Loads all daily spending records from the CSV file."""
    try:
        df = pd.read_csv(DAILY_SPENDING_FILE)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=['date', 'amount', 'category'])

def load_categories():
    """Loads expense categories from a CSV file or returns a default list."""
    try:
        df = pd.read_csv(CATEGORIES_FILE)
        return df['category'].tolist()
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Default categories if file doesn't exist
        return ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping']

def save_categories(categories_list):
    """Saves the current list of categories to a CSV file."""
    df = pd.DataFrame(categories_list, columns=['category'])
    df.to_csv(CATEGORIES_FILE, index=False)