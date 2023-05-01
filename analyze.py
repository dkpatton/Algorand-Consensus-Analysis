""" 
This script analyzes the node.log file and outputs a json file with the number of votes each account has cast.
"""

import os
import time
import json
from algosdk.v2client import algod
from config.algod import API_CONFIG

ALGOD_ADDRESS = API_CONFIG["algod_address"]
ALGOD_TOKEN = API_CONFIG["algod_api_key"]
HEADERS = {"X-API-Key": ALGOD_TOKEN}
ALGOD_CLIENT = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, HEADERS)

ALGORAND_DATA = "/var/lib/algorand"
LOG_FILE = ALGORAND_DATA + "/node.log"
LOG_LIST = []


with open("data/af_ai_accounts.json", "r", encoding="utf-8") as f:
    accounts = json.load(f)

all_accounts = accounts

# Copy node log to folder for analysis
if not(os.path.exists("data/node.log")):
    os.system("cp /var/lib/algorand/node.log node.log")

with open("data/node.log", "r", encoding="utf-8") as f:
    for line in f:
        LOG_LIST.append(line)

# open the schema file
with open("data/schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)
votes = {}
first_block = 1000000000000000
last_block = 0
for line in LOG_LIST:
    # If sender not in keys, add to keys
    # Requirements for a vote: Agreement, Vote, and Sender
    jsonln = json.loads(line)
    if ("Context" in jsonln.keys() and "Type" in jsonln.keys() and \
        "Sender" in jsonln.keys() and "Round" in jsonln.keys()):
        if jsonln["Context"] == "Agreement" and jsonln["Type"] == "VoteAccepted":
            if jsonln["Sender"] not in all_accounts.keys():
                address = jsonln["Sender"]
                account = ALGOD_CLIENT.account_info(address)
                time.sleep(1)
                all_accounts[jsonln["Sender"]] = {"balance": str(account["amount"]),
                                                  "owner": "Community"}
            if jsonln["Round"] < first_block:
                first_block = jsonln["Round"]
            if jsonln["Round"] > last_block:
                last_block = jsonln["Round"]
            if jsonln["Sender"] not in votes.keys():
                votes[jsonln["Sender"]] = 0
            votes[jsonln["Sender"]] += 1

with open("data/votes.json", "w", encoding="utf-8") as f:
    json.dump(votes, f, indent=4)

# Map vote values into all_accounts
for account in all_accounts:
    if account in votes.keys():
        all_accounts[account]["votes"] = votes[account]
    else:
        all_accounts[account]["votes"] = 0

with open("data/all_accounts.json", "w", encoding="utf-8") as f:
    json.dump(all_accounts, f, indent=4)