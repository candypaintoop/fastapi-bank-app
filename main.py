#main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import csv
import os

app = FastAPI()

# ------------ Core Classes ------------

class BankAccount:
    def __init__(self, account_holder, initial_balance=0):
        self.account_holder = account_holder
        self.balance = initial_balance
        self.log_file = f"{account_holder}_transactions.csv"

        # Create CSV with headers only if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Action", "Amount", "Balance"])

    def log_transaction(self, action, amount):
        with open(self.log_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                action,
                amount,
                self.balance
            ])

    def deposit(self, amount):
        self.balance += amount
        self.log_transaction("Deposit", amount)
        return f"Added ${amount}. New balance: ${self.balance}"

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Not enough money in account!")
        self.balance -= amount
        self.log_transaction("Withdraw", amount)
        return f"Withdrew ${amount}. New balance: ${self.balance}"

    def get_balance(self):
        return self.balance

    @property
    def is_overdrawn(self):
        return self.balance < 0


class SavingsAccount(BankAccount):
    def add_interest(self):
        interest = self.balance * 0.05
        self.balance += interest
        self.log_transaction("Interest", interest)
        return f"Added ${interest:.2f} interest! New balance: ${self.balance}"

# ------------ Use a global account for now ------------

account = SavingsAccount("Sahiti", 1000)

# ------------ Pydantic Model ------------

class Transaction(BaseModel):
    amount: float


def search_transactions(owner, keyword=None, date_from=None, date_to=None):
        results=[]
        file_path = f"{owner}_transactions.csv"

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Transaction file not found.")
        
        from datetime import datetime
        
        try:
            if date_from:
                date_from = datetime.strptime(date_from, "%Y-%m-%d")
            if date_to:
                date_to=datetime.strptime(date_to, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid data format. Use YYYY-MM-DD.")
        print("parsing date_from:", date_from)
        
        with open(file_path,mode='r')as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_date = datetime.strptime(row['Date'],"%Y-%m-%d %H:%M:%S" )

                if keyword and keyword.lower() not in row["Action"].lower():
                    continue
                if date_from and row_date< date_from:
                    continue
                if date_to and row_date< date_to:
                    continue

                
                results.append(row)
        
        return results

# ------------ API Routes ------------

@app.get("/balance")
def get_balance():
    return {
        "account_holder": account.account_holder,
        "balance": account.get_balance(),
        "is_overdrawn": account.is_overdrawn
    }

@app.post("/deposit")
def deposit_money(txn: Transaction):
    return {"message": account.deposit(txn.amount)}

@app.post("/withdraw")
def withdraw_money(txn: Transaction):
    try:
        return {"message": account.withdraw(txn.amount)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/interest")
def apply_interest():
    return {"message": account.add_interest()}

@app.get("/transactions")
def get_transactions():
    try:
        with open(account.log_file, mode='r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Transaction file not found.")
    
@app.get("/search")
def search(keyword: str=None, date_from: str=None, date_to:str=None):
    return search_transactions("Sahiti",keyword,date_from,date_to)

@app.get("/debug-all")
def debug_all():
    with open(account.log_file, mode='r') as f:
        return list(csv.DictReader(f))

