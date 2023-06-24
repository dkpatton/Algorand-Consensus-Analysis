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
min_block = 9999999999999999
max_block = 0
tmp_votes = defaultdict(lambda: {"votes": 0, "blocks": set()})
tmp_votes = defaultdict(lambda: {"votes": 0, "blocks": set()})
# Data folder should be environment variable ALGORAND_DATA per https://developer.algorand.org/docs/run-a-node/setup/install/
# If environment variable is not set, then set manually to /var/lib/algorand
DATA_FOLDER = os.getenv("ALGORAND_DATA", "SET YOUR NODE DATA FOLDER HERE")

with open("data/start_block.txt", "r", encoding="utf-8") as start_block:
    # These are the lines from the node log file that we want to keep
    start_block = int(start_block.read())

# Step 1 is to pull up the lists of associations and their addresses
with open("known_addresses/af_vault_addresses.json", "r", encoding="utf-8") as af_vault_addresses:
    # These are addresses with app ID 879935316 (algo fi vault)
    algofi_vault_addresses = json.load(af_vault_addresses)

with open("known_addresses/community_confirmed.json", "r", encoding="utf-8") as community_confirmed:
    # These are addresses that are community/ecosystem addresses, that we have confirmed
    community_confirmed_addresses = json.load(community_confirmed)

with open("known_addresses/community_unconfirmed.json", "r", encoding="utf-8") as community_unconfirmed:
    # These are addresses that are community/ecosystem addresses, that we have not confirmed
    community_unconfirmed_addresses = json.load(community_unconfirmed)

with open("known_addresses/fdn_and_corp_addresses.json", "r", encoding="utf-8") as fdn_and_corp_addresses:
    # These are addresses that are foundation and corporate addresses
    fdn_and_corp_addresses = json.load(fdn_and_corp_addresses)

# Step 2 is to get the node file from the data folder and load the rows into a list
# Copy and overwrite the file into the data directory
# Each line is JSON and should be kept if the type is VoteAccepted
# Skip lines that are not valid json

os.system(f"cp {DATA_FOLDER}/node.log data/node.log")

with open("data/node.log", "r", encoding="utf-8") as node_log:
    # These are the lines from the node log file that we want to keep
    node_log_lines = []

    # These are the lines from the node log file that we want to keep
    for line in node_log:
        # Parse each line as a JSON object
        try:
            log_entry = json.loads(line)
        except json.decoder.JSONDecodeError:
            continue

        # Check if the log entry contains "Round" and is a vote
        if log_entry.get("Type") == "VoteAccepted" and "Round" in log_entry:
            if log_entry.get("Round") > max_block:
                max_block = log_entry.get("Round")
            if log_entry.get("Round") < min_block:
                min_block = log_entry.get("Round")
            node_log_lines.append(log_entry)

# Step 3 is to iterate through the list of lines and tabulate the votes
# Here is the data structure. There has to be a smaller footprint way to do this.
# Only counting after the last block in the last file (start_block)
# {
#   "address_as_string": {
#       block_number_as_int: 1, # Usually an address votes once
#       block_number_as_int: 2} # Sometimes an address votes twice       
# }
# Here is the data format of the node logs we want to parse
# {'Context': 'Agreement', 'Hash': 'VEJNUTIGLVCKSON6BXHVSCGGBRWZAOXVROVNVLEB43Y2VV4BFFZQ', 'ObjectPeriod': 0, 'ObjectRound': 30003770, 'ObjectStep': 1, 'Period': 0, 'Round': 30003770, 'Sender': '45FNTGDM3MOTKOYNYMLZO2U2AEET4UHIMAYICA5AOV6XE7CFG7RTZHMA7A', 'Step': 1, 'Type': 'VoteAccepted', 'Weight': 1, 'WeightTotal': 106, 'file': 'trace.go', 'function': 'github.com/algorand/go-algorand/agreement.(*tracer).logVoteTrackerResult', 'level': 'info', 'line': 482, 'msg': 'vote accepted for {{} 0 XBYLS2E6YI6XXL5BWCAMOA4GTWHXWENZMX5UHXMRNWWUQ7BXCY5WC5TEPA VEJNUTIGLVCKSON6BXHVSCGGBRWZAOXVROVNVLEB43Y2VV4BFFZQ IA5OKKFFALTJMHB3SQC7OLI3DBBLADY3BSIV6YPTEHX5ZG5IWDZQ} at (30003770, 0, 1)', 'time': '2023-06-24T02:06:18.165459-07:00'}
#

with open("data/votes.json", "r", encoding="utf-8") as votes:
    # This is the running dictionary from all previous runs, which we will add to next
    votes = json.load(votes)

for line in node_log_lines:
    # Check if entry is after the last block in the last file
    if line.get("Round") > start_block:
        start_block = line.get("Round")
        # Check if the address is in the dictionary
        if line.get("Sender") not in votes:
            # Add the address to the dictionary
            votes[line.get("Sender")] = {}
        # Check if the block number is in the dictionary
        if line.get("Round") not in votes[line.get("Sender")]:
            # Add the block number to the dictionary
            votes[line.get("Sender")][line.get("Round")] = 1
        else:
            # Increment the block number
            votes[line.get("Sender")][line.get("Round")] += 1

# Write out the start block to a file
with open("data/start_block.txt", "w", encoding="utf-8") as start_block_file:
    start_block_file.write(str(start_block))

# Write out the votes to a file
with open("data/votes.json", "w", encoding="utf-8") as vote_record:
    json.dump(votes, vote_record, indent=4)

# Create merged dictionary of all seen addresses algofi_vault_addresses, community_confirmed_addresses, community_unconfirmed_addresses, fdn_and_corp_addresses
address_dir = {}
address_dir.update(algofi_vault_addresses)
address_dir.update(community_confirmed_addresses)
address_dir.update(community_unconfirmed_addresses)
address_dir.update(fdn_and_corp_addresses)

# Step 4 is to iterate through the list of lines and tabulate the votes
# While doing so add any unknown addresses to community_unconfirmed.json
for address in votes:
    if address not in address_dir:
        community_unconfirmed_addresses[address] = {"association": "Community",
                                                    "description": "Unconfirmed"}

with open("known_addresses/community_unconfirmed.json", "w", encoding="utf-8") as community_unconfirmed:
    json.dump(community_unconfirmed_addresses, community_unconfirmed, indent=4)

# Step 5 is to iterate through the list of lines and tabulate the votes by association
# We are tabulating in sequences of 1000 blocks. E.g. blocks 29014001 to 29015000 is one sequence.
# Here is the data structure. There has to be a smaller footprint way to do this.
# { 29014 : {  [this is 29014000 to 29014999]
#       "Community": 102,
#       "Algorand Foundation": 192,
#       "Algorand, Inc.": 0},
#   29015 : {   [this is 29015000 to 29015999]
#       "Community": 102,
#       "Algorand Foundation": 192,
#       "Algorand, Inc.": 0}
# }
data = {}
for address in votes:
    for block in votes[address]:
        block_sequence = int(block) // 1000
        if block_sequence not in data:
            data[block_sequence] = {}
        association = address_dir.get(address, {}).get("association", "unknown")
        if association not in data[block_sequence]:
            data[block_sequence][association] = 0
        data[block_sequence][association] += 1

# Step 6 is to write out the data to a file
with open("data/association_votes.json", "w", encoding="utf-8") as association_votes:
    json.dump(data, association_votes, indent=4)

        