"""
Quick smoke-test for insight_service.get_summary().
Run from the project root:
    python test_insights.py
"""
import sys
import os
 
# Make sure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
from services.insight_service import get_summary
 
FILE_PATH = os.path.join("data", "daily_spending.csv")
 
if not os.path.exists(FILE_PATH):
    print(f"[ERROR] Data file not found: {FILE_PATH}")
    print("Create data/daily_spending.csv with columns: date, amount, category")
    sys.exit(1)
 
result = get_summary(FILE_PATH)
print("=== Summary ===")
for key, value in result.items():
    if key == "insights":
        print(f"insights ({len(value)}):")
        for ins in value:
            print(f"  [{ins['type'].upper()}] {ins['message']}")
    else:
        print(f"  {key}: {value}")