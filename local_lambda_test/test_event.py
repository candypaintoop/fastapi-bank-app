import json
from lambda_function import lambda_handler

# Load your simulated event from event.json
with open("event.json", "r") as f:
    event = json.load(f)

response = lambda_handler(event, None)
print(response)