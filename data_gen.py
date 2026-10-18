"""Synthetic ticket generator. Templates + noise so the task is non-trivial
(shared vocabulary between categories, typos, vague tickets, mixed priority cues)."""
import random
import pandas as pd

from knowledge import CATEGORIES

USERS = ["Sam", "Priya", "Tom", "Aisha", "Mark", "Lena", "Dave", "Chloe", "Ravi", "Emma"]
SITES = ["Newcastle office", "Leeds site", "head office", "warehouse", "Gateshead depot", "London branch"]
APPS = ["Outlook", "Teams", "SharePoint", "OneDrive", "Excel", "the CRM", "the finance system"]

T = {
 "Account Access": [
  ("{u} cannot log in, says password is incorrect", "P3"),
  ("Account locked out after several attempts, user at {s}", "P3"),
  ("MFA prompt not arriving on new phone, locked out of everything", "P3"),
  ("password expired and self service reset is failing for {u}", "P3"),
  ("CEO locked out of account before board meeting in 30 minutes", "P2"),
  ("whole finance team getting 'account disabled' sign-in errors since 9am", "P1"),
  ("how do I change my password?", "P4"),
 ],
 "Phishing / Email Security": [
  ("received a strange email asking me to verify my bank details", "P3"),
  ("suspicious email with attachment from unknown sender, did not open it", "P3"),
  ("I clicked a link in an email and entered my password, now worried", "P2"),
  ("multiple staff at {s} received same fake invoice email with link", "P2"),
  ("phishing campaign: users reporting emails impersonating our MD, several clicked", "P1"),
  ("is this email legitimate? looks odd, question only", "P4"),
 ],
 "Endpoint Security Alert": [
  ("EDR alert: malware detected on {u}'s laptop, quarantined automatically", "P3"),
  ("antivirus flagged a potentially unwanted program on a workstation", "P4"),
  ("EDR high severity: suspicious PowerShell executing encoded commands on server", "P2"),
  ("files renamed with .locked extension and ransom note on file server", "P1"),
  ("ransomware behaviour detected on multiple endpoints at {s}", "P1"),
  ("endpoint agent shows as out of date on {u}'s device", "P4"),
 ],
 "Network / Firewall": [
  ("internet down at {s}, nobody can get online", "P1"),
  ("VPN tunnel to {s} keeps dropping every few minutes", "P2"),
  ("slow network for users at {s}, pages take ages to load", "P3"),
  ("firewall rule request: allow supplier IP to access web server", "P4"),
  ("wifi not working in meeting room two only", "P3"),
  ("firewall cluster failed over, primary unresponsive, site traffic unstable", "P2"),
 ],
 "Cloud (Azure / AWS)": [
  ("Azure VM not responding, production web app is down", "P1"),
  ("AWS S3 bucket permissions error for the reporting service", "P3"),
  ("Azure app service is very slow since last deployment", "P2"),
  ("storage account nearing quota, alert triggered", "P3"),
  ("cannot reach the cloud database from the app, timeouts started this morning", "P2"),
  ("request to resize a test VM in Azure", "P4"),
 ],
 "Backup & Recovery": [
  ("nightly backup failed again with error repository full", "P2"),
  ("please restore a deleted folder from last Tuesday for {u}", "P3"),
  ("backup agent offline on file server, last success 3 days ago", "P2"),
  ("need to restore whole VM from yesterday's snapshot, server corrupted", "P1"),
  ("backup report shows a warning on one job but completed", "P4"),
 ],
 "Microsoft 365 / Software": [
  ("{a} keeps crashing when opening attachments", "P3"),
  ("cannot send emails from Outlook, stuck in outbox", "P3"),
  ("Teams meetings audio keeps cutting out for all staff at {s}", "P2"),
  ("SharePoint site access denied for {u}", "P3"),
  ("mailbox full, need quota increase", "P4"),
  ("email not working for entire company, no one can send or receive", "P1"),
 ],
 "Hardware / Device": [
  ("laptop will not turn on, battery light flashing", "P3"),
  ("monitor flickering on {u}'s desk", "P4"),
  ("printer at {s} jammed and showing error code", "P4"),
  ("laptop screen cracked, user is travelling and needs it for client demo", "P2"),
  ("hard drive making clicking noise on a director's desktop", "P3"),
 ],
 "Data & BI (Qlik / Alteryx)": [
  ("Qlik dashboard not refreshing, data is from last week", "P3"),
  ("Alteryx workflow failed overnight with a connection error", "P3"),
  ("sales report shows wrong totals after the latest data load", "P2"),
  ("month-end Qlik reload failed and finance needs numbers today", "P2"),
  ("request for a new column in the stock dashboard", "P4"),
 ],
 "Access / Change Request": [
  ("new starter {u} joining Monday, needs laptop, email and CRM access", "P4"),
  ("leaver today: please disable account and forward mailbox to manager", "P3"),
  ("add {u} to the finance shared folder group", "P4"),
  ("urgent: terminated employee still has access to systems, disable now", "P2"),
  ("need licence for Visio for {u}", "P4"),
 ],
}

PREFIX = ["", "", "", "Hi, ", "Hello team, ", "URGENT: ", "Please help - ", "Quick one: ", "FYI "]
SUFFIX = ["", "", "", " Thanks.", " Can someone look asap?", " Started today.", " Happening for a while now.", " Not sure what changed."]
NOISE = [("password", "pasword"), ("email", "emial"), ("cannot", "cant"), ("laptop", "lap top"),
         ("firewall", "fire wall"), ("backup", "back up")]

def _noise(text, rng):
    if rng.random() < 0.15:
        a, b = rng.choice(NOISE)
        text = text.replace(a, b)
    return text

def generate(n=1500, seed=42):
    rng = random.Random(seed)
    rows = []
    for i in range(n):
        cat = rng.choice(CATEGORIES)
        tpl, pr = rng.choice(T[cat])
        text = tpl.format(u=rng.choice(USERS), s=rng.choice(SITES), a=rng.choice(APPS))
        text = rng.choice(PREFIX) + text + rng.choice(SUFFIX)
        text = _noise(text, rng)
        # label noise: occasionally the human-assigned priority is one level off
        if rng.random() < 0.07:
            idx = int(pr[1]) - 1
            idx = min(3, max(0, idx + rng.choice([-1, 1])))
            pr = f"P{idx+1}"
        # category ambiguity: occasionally the ticket is vague and mislabelled
        if rng.random() < 0.04:
            cat = rng.choice(CATEGORIES)
        rows.append({"ticket_id": f"T{100000+i}", "text": text, "category": cat, "priority": pr})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = generate()
    df.to_csv("synthetic_tickets.csv", index=False)
    print(df.head(10).to_string())
    print(df.category.value_counts())
    print(df.priority.value_counts())
