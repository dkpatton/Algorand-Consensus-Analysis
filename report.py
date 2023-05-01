"""
Reports in this module will make a decentralization report 
for the Algorand network.
"""
import os
import json
import time
import datetime
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

# Sum all AF balances
uncirculated_supply = df[df["Owner"] == "Algorand Foundation"]["Balance"].sum()

# Remove all zero balances or zero votes
df = df[df["Balance"] != "0"]
df = df[df["Votes"] != "0"]

# Convert all balances and votes to integers
df["Balance"] = df["Balance"].astype(int)
df["Votes"] = df["Votes"].astype(int)

# Make an HTML table of all the data in the dataframe
appendix = df.to_html(index=False)

# Total Consensus Statistics
total_votes = df["Votes"].sum()
total_participating_supply = df["Balance"].sum()

# Select all non-AF accounts from the dataframe
df = df[df["Owner"] != "Algorand Foundation"]

# Circulating Supply Consensus Statistics
sum_non_af_balance = sum(df["Balance"])
percent_non_af_balance = sum_non_af_balance / TOTAL_SUPPLY
sum_non_af_votes = sum(df["Votes"])
percent_non_af_votes = sum_non_af_votes / total_votes
n_non_af_accounts = len(df)
mean_non_af_balance = df["Balance"].mean()
mean_non_af_votes = df["Votes"].mean()
median_non_af_balance = df["Balance"].median()
median_non_af_votes = df["Votes"].median()
std_non_af_balance = df["Balance"].std()
std_non_af_votes = df["Votes"].std()

# Select all non-AI accounts from the dataframe
df = df[df["Owner"] != "Algorand Inc."]

# Community Consensus Statistics
sum_community_balance = sum(df["Balance"])
percent_community_balance = sum_community_balance / TOTAL_SUPPLY
sum_community_votes = sum(df["Votes"])
percent_community_votes = sum_community_votes / total_votes
n_community_accounts = len(df)
mean_community_balance = df["Balance"].mean()
mean_community_votes = df["Votes"].mean()
median_community_balance = df["Balance"].median()
median_community_votes = df["Votes"].median()
std_community_balance = df["Balance"].std()
std_community_votes = df["Votes"].std()

# REPORT VARIABLES
log_ts = time.ctime(os.path.getmtime("data/node.log"))
af_bal_ts = time.ctime(os.path.getmtime("data/af_ai_accounts.json"))
ai_bal_ts = time.ctime(os.path.getmtime("data/af_ai_accounts.json"))
ac_bal_ts = time.ctime(os.path.getmtime("data/all_accounts.json"))
iso_date = datetime.datetime.now().isoformat()

html = "<html><body>{header}{intro}{circulating_supply_stats}{community_stats}{appendix}{timestamps}</body></html>"
header = "<h1> Algorand Decentralization Report, {iso_date}</h1>".format(iso_date=iso_date)
intro = [
    "This report was generated based on real traffic logged on the Algorand network.",
    "The total number of Algos in circulation is {total_supply}.".format(total_supply=TOTAL_SUPPLY/1000000) +
    "There were {total_votes} votes cast within the range covered by this report.".format(total_votes=total_votes)]

# Make an HTML table for the circulating supply statistics section
circulating_supply_stats = [
    "<h2>Circulating Supply Consensus Statistics</h2>",
    "<table>",
    "<tr><th>Statistic</th><th>Value</th></tr>",
    "<tr><td>Number of accounts</td><td>{n_non_af_accounts}</td></tr>".format(n_non_af_accounts=n_non_af_accounts),
    "<tr><td>Sum of balances</td><td>{sum_non_af_balance}</td></tr>".format(sum_non_af_balance=sum_non_af_balance),
    "<tr><td>Percent of total supply</td><td>{percent_non_af_balance:.2%}</td></tr>".format(percent_non_af_balance=percent_non_af_balance),
    "<tr><td>Mean balance</td><td>{mean_non_af_balance}</td></tr>".format(mean_non_af_balance=mean_non_af_balance),
    "<tr><td>Median balance</td><td>{median_non_af_balance}</td></tr>".format(median_non_af_balance=median_non_af_balance),
    "<tr><td>Standard deviation of balances</td><td>{std_non_af_balance}</td></tr>".format(std_non_af_balance=std_non_af_balance),
    "<tr><td>Sum of votes</td><td>{sum_non_af_votes}</td></tr>".format(sum_non_af_votes=sum_non_af_votes),
    "<tr><td>Percent of total votes</td><td>{percent_non_af_votes:.2%}</td></tr>".format(percent_non_af_votes=percent_non_af_votes),
    "<tr><td>Mean votes</td><td>{mean_non_af_votes}</td></tr>".format(mean_non_af_votes=mean_non_af_votes),
    "<tr><td>Median votes</td><td>{median_non_af_votes}</td></tr>".format(median_non_af_votes=median_non_af_votes),
    "<tr><td>Standard deviation of votes</td><td>{std_non_af_votes}</td></tr>".format(std_non_af_votes=std_non_af_votes),
    "</table>"]

# Make an HTML table for the community statistics section
community_stats = [
    "<h2>Community Consensus Statistics</h2>",
    "<table>",
    "<tr><th>Statistic</th><th>Value</th></tr>",
    "<tr><td>Number of accounts</td><td>{n_community_accounts}</td></tr>".format(n_community_accounts=n_community_accounts),
    "<tr><td>Sum of balances</td><td>{sum_community_balance}</td></tr>".format(sum_community_balance=sum_community_balance),
    "<tr><td>Percent of total supply</td><td>{percent_community_balance:.2%}</td></tr>".format(percent_community_balance=percent_community_balance),
    "<tr><td>Mean balance</td><td>{mean_community_balance}</td></tr>".format(mean_community_balance=mean_community_balance),
    "<tr><td>Median balance</td><td>{median_community_balance}</td></tr>".format(median_community_balance=median_community_balance),
    "<tr><td>Standard deviation of balances</td><td>{std_community_balance}</td></tr>".format(std_community_balance=std_community_balance),
    "<tr><td>Sum of votes</td><td>{sum_community_votes}</td></tr>".format(sum_community_votes=sum_community_votes),
    "<tr><td>Percent of total votes</td><td>{percent_community_votes:.2%}</td></tr>".format(percent_community_votes=percent_community_votes),
    "<tr><td>Mean votes</td><td>{mean_community_votes}</td></tr>".format(mean_community_votes=mean_community_votes),
    "<tr><td>Median votes</td><td>{median_community_votes}</td></tr>".format(median_community_votes=median_community_votes),
    "<tr><td>Standard deviation of votes</td><td>{std_community_votes}</td></tr>".format(std_community_votes=std_community_votes),
    "</table>"]

timestamps_footer = [
    "<p>Timestamps for the data used in this report:</p>",
    "<ul>",
    "<li>node.log: {log_ts}</li>".format(log_ts=log_ts),
    "<li>af_ai_accounts.json: {af_bal_ts}</li>".format(af_bal_ts=af_bal_ts),
    "<li>ai_bal_ts: {ai_bal_ts}</li>".format(ai_bal_ts=ai_bal_ts),
    "<li>all_accounts.json: {ac_bal_ts}</li>".format(ac_bal_ts=ac_bal_ts),
    "</ul>"]

html = html.format(
    header=header,
    intro=intro,
    circulating_supply_stats=circulating_supply_stats,
    community_stats=community_stats,
    appendix=appendix,
    timestamps=timestamps_footer)

with open("decentralization_report.html", "w") as f:
    f.write(html)
