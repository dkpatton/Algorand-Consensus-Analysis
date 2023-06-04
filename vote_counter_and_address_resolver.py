"""
Data Collection Module:
This module is responsible for analyzing the node's log file and tabulating agreement messages for every 1000 blocks.
"""

import os
import json
from collections import defaultdict
from algosdk.v2client import algod
from config.algod import API_CONFIG

ALGOD_ADDRESS = API_CONFIG["algod_address"]
ALGOD_TOKEN = API_CONFIG["algod_api_key"]
HEADERS = {"X-API-Key": ALGOD_TOKEN}
ALGOD_CLIENT = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, HEADERS)

# Initial Variables
min_block = 0
max_block = 999
tmp_votes = defaultdict(lambda: {"votes": 0, "blocks": set()})
tmp_votes = defaultdict(lambda: {"votes": 0, "blocks": set()})

# Make a dictionary of known addresses and their association (file name) and add a "description" field
known_addresses = {}
for file_name in os.listdir("known_addresses"):
    with open(f"known_addresses/{file_name}", "r") as address_file:
        for line in address_file.readlines()[1:]:
            address = line.strip()
            known_addresses[address] = {"association": file_name.split(".")[0], "description": ""}

# Create a variable to store accounts that are not known to add to the known addresses at the end
unknown_addresses = []


# Check if "data/votes.json" exists
if os.path.isfile('data/votes.json'):
    with open('data/votes.json', 'r') as json_file:
        data = json.load(json_file)
else:
    data = {}

# Open "data/node.log"
with open("data/node.log", "r", encoding="utf-8") as log_file:
    for line in log_file:
        # Parse each line as a JSON object
        log_entry = json.loads(line)

        # Check if the log entry contains "Round" and is a vote
        if log_entry.get("Type") == "VoteAccepted" and "Round" in log_entry:
            block_number = log_entry["Round"]
            sender_address = log_entry.get("Sender")


            # If the sender address is not None, increment vote count and add block number to the set of blocks
            if sender_address is not None:
                tmp_votes[sender_address]["votes"] += 1
                tmp_votes[sender_address]["blocks"].add(block_number)

            # Check if sender in known addresses, and if not add to unknown addresses
            if sender_address not in known_addresses:
                unknown_addresses.append(sender_address)

            # Check if we have processed blocks in the range
            if min_block <= block_number <= max_block:
                continue
            
            # Calculate the block range
            block_range = f"{min_block}-{max_block}"
            # Store the temporary votes in the data dictionary
            data[block_range] = {k: {"votes": v["votes"], "blocks": len(v["blocks"])} for k, v in tmp_votes.items()}

            # Reset the temporary votes
            tmp_votes = defaultdict(lambda: {"votes": 0, "blocks": set()})

            # Update the block range
            min_block = block_number // 1000 * 1000
            max_block = min_block + 999

# Check if there are any remaining votes
if tmp_votes:
    # Calculate the block range
    block_range = f"{min_block}-{block_number}"
    # Store the temporary votes in the data dictionary
    data[block_range] = {k: {"votes": v["votes"], "blocks": len(v["blocks"])} for k, v in tmp_votes.items()}

# Save the data to a JSON file
with open('data/votes.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Add all unkown addresses to known addresses variable with association "unknown"
for address in unknown_addresses:
    known_addresses[address] = {"association": "unknown", "description": ""}

# Save the unkown addresses as a text file in known_addresses
with open("known_addresses/unknown.txt", "w", encoding="utf-8") as f:
    for address in unknown_addresses:
        f.write(address + "\n")


# For every unknown address, check with if the application ID is 879935316 is configured
# If so, add add the "AlgoFi Vault" description to that address in known addresses
#remove duplicates in unknown addresses
unknown_addresses = list(set(unknown_addresses))
still_unknown_addresses = []
for address in unknown_addresses:
    account_info = ALGOD_CLIENT.account_info(address)
    # # get all values for 'id' in 'apps-local-state'
    app_ids = [app["id"] for app in account_info["apps-local-state"]]
    if 879935316 in app_ids:
        known_addresses[address]= {
            "association": "Community",
            "description": "AlgoFi Vault"
        }
    else:
        known_addresses[address]= {
            "association": "Unknown",
            "description": ""
        }
        still_unknown_addresses.append(address)
    
# Save the unkown addresses as a text file in known_addresses
with open("known_addresses/unknown.txt", "w", encoding="utf-8") as f:
    for address in still_unknown_addresses:
        f.write(address + "\n")

# Save the known addresses to a JSON file
with open('data/addresses.json', 'w') as json_file:
    json.dump(known_addresses, json_file, indent=4)
