"""
Reports in this module will make a decentralization report 
for the Algorand network.
"""
import os
import json
import time
import datetime
import tabulate
import requests
import pandas as pd
import matplotlib.pyplot as plt


TOTAL_SUPPLY = 10000000000000000
REPORT_TERMS = {"AF": "The Algorand Foundation, the organization charged with\
                distributing the remaining Algos to the community.",
                "AI": "Algorand Inc., the organization that created the Algorand\
                protocol and is responsible for its development.",
                "AC": "Algorand Community, the community of Algorand users and\
                developers.",
                "&": "Symbol used in this report to denote the ALGO cryptocurrency."}

cb_algo_price_url = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=ALGO",
                                 timeout=60).json()["data"]
with open("README.md", "r", encoding="utf-8") as f:
    header = f.readline()
    file_name = header.split("Decentralization Report, ")[1].strip().split("T")[0]
    with open("archive/" + file_name + ".md", "w", encoding="utf-8") as f2:
        f2.write(header + f.read())


# Load metadata
with open("data/meta_data.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

iso_date = datetime.datetime.fromtimestamp(time.time()).isoformat()
with open("data/all_accounts.json", "r", encoding="utf-8") as f:
    accounts = json.load(f)

# Create a dataframe for the report
df = pd.DataFrame(columns=["Account", "Owner", "Balance", "Votes"])

# Add all accounts to the dataframe
for account in accounts:
    df["Account"] = accounts.keys()
    df["Owner"] = [accounts[account]["owner"] for account in accounts]
    df["Balance"] = [accounts[account]["balance"] for account in accounts]
    df["Votes"] = [accounts[account]["votes"] for account in accounts]

# Format the data
df["Balance"] = df["Balance"].astype(int)
df["Votes"] = df["Votes"].astype(int)
df = df.drop(df[df["Balance"] == 0].index)
df = df.drop(df[df["Votes"] == 0].index)

balance_participating_in_consensus = df["Balance"].sum()

# Make copies for the report
df_report1 = df.copy()
df_appendix = df.copy()

# By owner, Average of Balance and Votes, Number of accounts
df_report1["Balance"] = df_report1["Balance"] / 1000000
# Create comma separated values for balance
df_report1 = df_report1.groupby("Owner").agg({"Balance": ["mean"],
                                                "Votes": ["mean", "count", "std"]})
df_report1.columns = ["Balance Mean",
                      "Votes Mean", "Node Count", "Votes Std"]
df_report1["Balance Mean"] = df_report1["Balance Mean"].map("{:,.2f}".format)
# Add total percentage of votes column to report
df_report1["Votes %"] = (df_report1["Node Count"] / df_report1["Node Count"].sum()) * 100

# Generate histograph of votes
df["Votes"].plot.hist(bins=100, alpha=0.5)
plt.title("Algorand Votes Distribution")
plt.xlabel("Votes")
plt.ylabel("Frequency")
no_legend = plt.savefig("images/votes_distribution.png")

# For info block in report
firstRound = metadata["firstBlock"]
lastRound = metadata["lastBlock"]

# Max appendix column
df_appendix = df.set_index("Owner")
appendix = df_appendix.to_markdown()
markdown = "# Algorand Decentralization Report, " + iso_date + "\n\n"
markdown += "Data in this report have been generated using a node log. " + \
            "The block range for this report is from block " + str(firstRound) + \
            " to block " + str(lastRound) +" (" + str(lastRound-firstRound) +" total)." +\
            " Owner is being identified through " + \
            "the foundation and inc websites. I'll be running this periodically.\n\n"
markdown += "Previous report: [{link_name}]({link_to_archive})\n\n".format(
    link_to_archive="archive/" + header + ".md", link_name=header)
markdown += "## Summary Table\n"
markdown += df_report1.to_markdown()
markdown += "\n## Number of Votes Distribution\n"
markdown += "![Votes Distribution](images/votes_distribution.png)\n\n"
markdown += "\n\n"
markdown += "## Raw Table\n"
markdown += appendix

with open("README.md", "w") as f:
    f.write(markdown)
