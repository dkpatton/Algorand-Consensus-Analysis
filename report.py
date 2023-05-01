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

# Make two copies, one for the report and one for the appendix
df_report = df.copy()
df_appendix = df.copy()

# Generate statistics for the report
df_report = df_report.drop("Account", axis=1)
df_report = df_report.groupby("Owner").sum()
df_report["Balance"] = df_report["Balance"].astype(int)
df_report["Votes"] = df_report["Votes"].astype(int)
df_report["% of Supply"] = df_report["Balance"] / TOTAL_SUPPLY
df_report["% of Supply"] = df_report["% of Supply"].map(lambda x: "{:.2%}".format(x))
df_report["% of Votes"] = df_report["Votes"] / df_report["Votes"].sum()
df_report["% of Votes"] = df_report["% of Votes"].map(lambda x: "{:.2%}".format(x))
df_report = df_report.reset_index()
df_report = df_report.sort_values(by=["Balance"], ascending=False)
df_report = df_report.reset_index(drop=True)

report = df_report.to_markdown()

# Max appendix column
df_appendix = df.set_index("Owner")
appendix = df_appendix.to_markdown()

markdown = report + "\n\n" + appendix
with open("decentralization_report.md", "w") as f:
    f.write(markdown)