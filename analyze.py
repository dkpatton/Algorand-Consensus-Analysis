""" 
This script analyzes the node.log file and outputs a json file with the number of votes each account has cast.
"""

import os
import json

ALGORAND_DATA = "/var/lib/algorand"
LOG_FILE = ALGORAND_DATA + "/node.log"
LOG_LIST = []


with open("addresses/algo_inc_and_found_accounts.json", "r", encoding="utf-8") as f:
    accounts = json.load(f)

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
    if "Context" in jsonln.keys() and "Type" in jsonln.keys() and "Sender" in jsonln.keys() and "Round" in jsonln.keys():
        if jsonln["Context"] == "Agreement" and jsonln["Type"] == "VoteAccepted":
            if jsonln["Round"] < first_block:
                first_block = jsonln["Round"]
            if jsonln["Round"] > last_block:
                last_block = jsonln["Round"]
            if jsonln["Sender"] not in votes.keys():
                votes[jsonln["Sender"]] = 0
            votes[jsonln["Sender"]] += 1


# Export Votes
with open("data/votes.json", "w", encoding="utf-8") as f:
    json.dump(votes, f, indent=4)


