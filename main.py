#main.py

# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from helpers import ensure_csv_exists, log_transaction, read_transactions, write_transactions, search_transactions

class BankAccount:
    def __init__(self, account_holder, initial_balance=0):
        self.account_holder = account_holder
        self.balance = initial_balance
        self.log_file = f"{account_holder}_transactions.csv"

        ensure_csv_exists(self.log_file)

    def deposit(self, amount):
        self.balance += amount
        log_transaction(self.log_file, "Deposit", amount, self.balance)
        return f"Added ${amount}. New balance: ${self.balance}"

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds!")
        self.balance -= amount
        log_transaction(self.log_file, "Withdraw", amount, self.balance)
        return f"Withdrew ${amount}. New balance: ${self.balance}"

    def add_interest(self):
        interest = self.balance * 0.05
        self.balance += interest
        log_transaction(self.log_file, "Interest", interest, self.balance)
        return f"Added ${interest:.2f} interest! New balance: ${self.balance}"

    def get_balance(self):
        return self.balance

    @property
    def is_overdrawn(self):
        return self.balance < 0

app = FastAPI()
account = BankAccount("Sahiti", 1000)

class Transaction(BaseModel):
    amount: float

class UpdateTransaction(BaseModel):
    index: int
    action: str
    amount: float

class DeleteTransaction(BaseModel):
    index: int

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
    return read_transactions(account.log_file)

@app.get("/search")
def search(keyword: str = None, date_from: str = None, date_to: str = None):
    return search_transactions(account.log_file, keyword, date_from, date_to)

@app.put("/update")
def update_transaction(update: UpdateTransaction):
    transactions = read_transactions(account.log_file)
    if update.index < 0 or update.index >= len(transactions):
        raise HTTPException(status_code=404, detail="Transaction index out of range.")

    transactions[update.index]["Action"] = update.action
    transactions[update.index]["Amount"] = str(update.amount)
    # Optionally, recalculate balance logic here if needed.
    write_transactions(account.log_file, transactions)
    return {"message": f"Transaction at index {update.index} updated."}

@app.delete("/delete")
def delete_transaction(delete: DeleteTransaction):
    transactions = read_transactions(account.log_file)
    if delete.index < 0 or delete.index >= len(transactions):
        raise HTTPException(status_code=404, detail="Transaction index out of range.")

    transactions.pop(delete.index)
    write_transactions(account.log_file, transactions)
    return {"message": f"Transaction at index {delete.index} deleted."}
