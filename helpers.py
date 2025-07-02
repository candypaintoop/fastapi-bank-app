# helpers.py

import csv
import os
from datetime import datetime
from fastapi import HTTPException

def ensure_csv_exists(filename):
    if not os.path.exists(filename):
        with open(filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Action", "Amount", "Balance"])

def log_transaction(filename, action, amount, balance):
    with open(filename, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            action,
            amount,
            balance
        ])

def read_transactions(filename):
    with open(filename, mode='r') as f:
        return list(csv.DictReader(f))

def write_transactions(filename, transactions):
    with open(filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Action", "Amount", "Balance"])
        writer.writeheader()
        writer.writerows(transactions)

def search_transactions(filename, keyword=None, date_from=None, date_to=None):
    results = []
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="Transaction file not found.")

    from datetime import datetime

    try:
        if date_from:
            date_from = datetime.strptime(date_from, "%Y-%m-%d")
        if date_to:
            date_to = datetime.strptime(date_to, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    with open(filename, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_date = datetime.strptime(row['Date'], "%Y-%m-%d %H:%M:%S")
            if keyword and keyword.lower() not in row["Action"].lower():
                continue
            if date_from and row_date < date_from:
                continue
            if date_to and row_date > date_to:
                continue
            results.append(row)

    return results
