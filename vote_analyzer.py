""" Vote ANalyzer
    Reads addresses.json and votes.json and makes a data file for reporting."""
import os
import json
from collections import defaultdict
from algosdk.v2client import algod
from config.algod import API_CONFIG
import pandas as pd

# Initial Variables
ALGOD_ADDRESS = API_CONFIG["algod_address"]
ALGOD_TOKEN = API_CONFIG["algod_api_key"]
HEADERS = {"X-API-Key": ALGOD_TOKEN}
ALGOD_CLIENT = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, HEADERS)

# Open the addresses, including resolved addresses
with open('data/addresses.json', 'r') as json_file:
    addresses = json.load(json_file)

# Open votes list and blocks voted on data
with open('data/votes.json', 'r') as json_file:
    votes = json.load(json_file)

# Initialize a DataFrame to store the votes
votes_df = pd.DataFrame()

# Iterate over each block range in the votes data
for block_range, block_data in votes.items():
    # Iterate over each address in the block range data
    for address, address_data in block_data.items():
        # Get the association and description for the address
        association = addresses.get(address, {}).get("association", "unknown")
        description = addresses.get(address, {}).get("description", "")

        # If there is a description, append it to the association
        if description:
            association += f": {description}"

        # Update the DataFrame with the votes, blocks, and number of distinct addresses that voted
        votes_df.loc[block_range, f"{association} (votes)"] = address_data.get("votes", 0)
        votes_df.loc[block_range, f"{association} (blocks)"] = address_data.get("blocks", 0)
        votes_df.loc[block_range, f"{association} (addresses)"] = len(address_data.get("addresses", set()))
        

# Fill NaN values with 0
votes_df.fillna(0, inplace=True)

# Convert vote and block counts to integers
for column in votes_df.columns:
    votes_df[column] = votes_df[column].astype(int)

# write the dataframe to README.md
votes_df.to_markdown("README.md", index=True)


