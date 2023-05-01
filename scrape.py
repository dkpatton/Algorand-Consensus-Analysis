"""
Scrape the foundation and inc addresses, check the balances, and save to a json file.
"""
import json
import time
import requests
from algosdk.v2client import algod
from bs4 import BeautifulSoup
from config.algod import API_CONFIG

algod_address = API_CONFIG["algod_address"]
algod_token = API_CONFIG["algod_api_key"]
headers = {"X-API-Key": algod_token}
algod_client = algod.AlgodClient(algod_token, algod_address, headers)

ALGO_INC_URL = "https://algorand.com/resources/blog/algorand_wallets"
ALGO_FND_URL = "https://algorand.foundation/the-foundation"

# Scrape addresses from the preformatted html tags
algorand_inc_addresses = []
html_page = requests.get(ALGO_INC_URL, timeout=30)
soup = BeautifulSoup(html_page.content, "html.parser")
for pre in soup.find_all("pre"):
    for address in pre.text.split("\n"):
        if address.endswith(" | Participating"):
            algorand_inc_addresses.append(address.split(" | ")[0])

# Scraping out of this page is a bit more difficult
algorand_foundation_addresses = []
html_page = requests.get(ALGO_FND_URL, timeout=30)
soup = BeautifulSoup(html_page.content, 'html.parser')
for p in soup.find_all("p"):
    # split all p tags by <br> tags
    addresses = str(p).split("<br/>")
    VALID = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    special_removals = ["<strong>BitGo:</strong>", "<strong>Fireblocks:</strong>"]
    for address in addresses:
        address = address.replace("<p>", "").replace("</p>", "")
        for removal in special_removals:
            address = address.replace(removal, "")
        address = address.strip().split(" ")[0]
        # if address has trailing space, split and take first part
        for letter in address:
            if letter not in VALID:
                address = address.split(letter)[0]
        if len(address) == 58:
            algorand_foundation_addresses.append(address)

# Save to txt files
with open("addresses/algorand_inc_addresses.txt", "w", encdoing="utf-8") as f:
    for address in algorand_inc_addresses:
        f.write(address + "\n")

with open("addresses/algorand_foundation_addresses.txt", "w", encoding="utf-8") as f:
    for address in algorand_foundation_addresses:
        f.write(address + "\n")

# The addresses of and balances for the Algorand Foundation and Algorand Inc.
algo_inc_and_found_accounts = {}
for address in algorand_inc_addresses:
    account = algod_client.account_info(address)
    time.sleep(5)
    algo_inc_and_found_accounts[address] = {"owner": "Algorand Inc.", "balance": str(account["amount"])}

for address in algorand_foundation_addresses:
    account = algod_client.account_info(address)
    time.sleep(5)
    algo_inc_and_found_accounts[address] = {"owner": "Algorand Foundation", "balance": str(account["amount"])}

with open("addresses/algo_inc_and_found_accounts.json", "w") as f:
    f.write(json.dumps(algo_inc_and_found_accounts, indent=4))

