import os
import shutil

BUCKET_DIR = "bank_data"
CSV_FILE = "Sahiti_transactions.csv"

def lambda_handler(event, context):
    action = event.get("action")
    amount = event.get("amount", 0)

    if action == "deposit":
        save_to_s3(CSV_FILE)
        return {"statusCode": 200, "body": f"Deposited ₹{amount}"}

    elif action == "withdraw":
        save_to_s3(CSV_FILE)
        return {"statusCode": 200, "body": f"Withdrew ₹{amount}"}

    elif action == "download":
        content = download_from_s3(CSV_FILE)
        return {"statusCode": 200, "body": content}

    else:
        return {"statusCode": 400, "body": "Invalid action"}

def save_to_s3(filename):
    os.makedirs(BUCKET_DIR, exist_ok=True)
    shutil.copy(filename, os.path.join(BUCKET_DIR, filename))

def download_from_s3(filename):
    path = os.path.join(BUCKET_DIR, filename)
    with open(path, 'r') as f:
        return f.read()
import json
from lambda_function import lambda_handler

# Load your simulated event from event.json
with open("event.json", "r") as f:
    event = json.load(f)

response = lambda_handler(event, None)
print(response)


