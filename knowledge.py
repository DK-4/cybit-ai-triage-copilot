"""Runbook knowledge base + ticket taxonomy for the Cybit triage copilot PoC.
All content is synthetic and written for this demo (no real Cybit data)."""

RUNBOOKS = {
    "RB-001": {
        "category": "Account Access",
        "title": "Password reset & account lockout",
        "steps": [
            "Verify the caller's identity using the approved challenge questions or manager approval.",
            "Check Entra ID / Active Directory sign-in logs for lockout source and failed attempts.",
            "Unlock the account and trigger a self-service password reset or set a temporary password.",
            "If lockouts repeat, look for stale credentials on mobile devices or mapped drives.",
            "Confirm MFA registration is intact; re-register the method if the phone changed.",
        ],
    },
    "RB-002": {
        "category": "Phishing / Email Security",
        "title": "Suspected phishing email",
        "steps": [
            "Ask the user NOT to click links or open attachments; capture the original message (.eml).",
            "Search mail trace for the same sender/subject and quarantine all copies tenant-wide.",
            "If the user clicked or entered credentials: force password reset, revoke sessions, review sign-in logs.",
            "Block sender domain / URLs at the mail gateway and web filter.",
            "Notify the customer security contact and log the incident for the monthly report.",
        ],
    },
    "RB-003": {
        "category": "Endpoint Security Alert",
        "title": "EDR malware / ransomware alert",
        "steps": [
            "Review the alert severity and process tree in the EDR console.",
            "If ransomware behaviour or lateral movement is suspected: isolate the host immediately.",
            "Collect triage artefacts (running processes, persistence, recent files) before remediation.",
            "Run a full scan, remove the threat, and check other hosts for the same hash.",
            "Escalate to the security team lead and notify the customer per the incident SLA.",
        ],
    },
    "RB-004": {
        "category": "Network / Firewall",
        "title": "Network or firewall outage",
        "steps": [
            "Confirm scope: one user, one site, or whole customer. Check the NOC monitoring dashboard.",
            "Test ISP link, WAN interface state and VPN tunnel status on the firewall (e.g. Check Point).",
            "Review recent firewall policy or firmware changes; roll back if the timing matches.",
            "Fail over to the secondary link if available and raise a carrier ticket.",
            "Keep the customer updated every 30 minutes for P1 incidents.",
        ],
    },
    "RB-005": {
        "category": "Cloud (Azure / AWS)",
        "title": "Cloud resource or service degradation",
        "steps": [
            "Check the provider service health page and Azure/AWS monitoring alerts for the subscription.",
            "Identify affected resources (VMs, app services, storage) and recent deployment or scaling changes.",
            "Review cost/quota limits and networking rules (NSG / security groups).",
            "Restart or redeploy the affected resource; restore from last known good config if needed.",
            "Document root cause and add monitoring if the failure was silent.",
        ],
    },
    "RB-006": {
        "category": "Backup & Recovery",
        "title": "Backup job failure or restore request",
        "steps": [
            "Open the backup console and read the job error; check repository free space and agent status.",
            "Re-run the failed job manually once the cause is fixed.",
            "For restore requests: confirm the exact file/VM, restore point and destination with the requester.",
            "Verify the restored data with the owner and record it in the change log.",
            "If two consecutive backups fail, escalate to P2 and inform the customer.",
        ],
    },
    "RB-007": {
        "category": "Microsoft 365 / Software",
        "title": "Outlook, Teams, SharePoint or application issue",
        "steps": [
            "Check Microsoft 365 service health and confirm whether the issue is tenant-wide.",
            "Reproduce on web client; if the web works, rebuild the Outlook profile or clear the Teams cache.",
            "Check licence assignment and mailbox/storage quotas.",
            "Review SharePoint permissions for access complaints.",
            "Escalate to Microsoft support with the request ID if a service-side fault is confirmed.",
        ],
    },
    "RB-008": {
        "category": "Hardware / Device",
        "title": "Laptop, desktop or peripheral fault",
        "steps": [
            "Run built-in diagnostics and check warranty status of the device.",
            "Try basic isolation: different power source, dock, cable or peripheral.",
            "Back up user data if the disk shows SMART errors.",
            "Raise a vendor repair call or arrange a loan device for the user.",
            "Update the asset register once resolved.",
        ],
    },
    "RB-009": {
        "category": "Data & BI (Qlik / Alteryx)",
        "title": "Dashboard, data refresh or workflow failure",
        "steps": [
            "Check the reload / scheduler log for the failing task (Qlik reload or Alteryx workflow).",
            "Validate source connectivity and credentials (database, API, gateway).",
            "Look for schema changes upstream that break field mappings.",
            "Re-run for a small date range to isolate bad records, then run the full load.",
            "Notify the report owner when data is current again.",
        ],
    },
    "RB-010": {
        "category": "Access / Change Request",
        "title": "New starter, leaver or access change",
        "steps": [
            "Confirm the request is approved by the customer's authorised contact.",
            "Create/disable the account and update group memberships and licences.",
            "For leavers: disable sign-in, revoke sessions, convert mailbox, recover devices.",
            "Provision hardware and MFA enrolment for new starters.",
            "Close the ticket with a summary of changes made.",
        ],
    },
}

CATEGORIES = sorted({r["category"] for r in RUNBOOKS.values()})
CATEGORY_TO_RUNBOOK = {r["category"]: rid for rid, r in RUNBOOKS.items()}
PRIORITIES = ["P1", "P2", "P3", "P4"]
PRIORITY_MEANING = {
    "P1": "Critical - business down or active security incident (respond < 15 min)",
    "P2": "High - major degradation or many users affected (respond < 1 h)",
    "P3": "Normal - single user or workaround exists (respond < 4 h)",
    "P4": "Low - request, question or cosmetic issue (respond < 1 business day)",
}


# Domain-knowledge lexicon: cold-start prior used as extra training signal and for fusion.
LEXICON = {
 "Account Access": "login log in sign in signin password pw credentials locked out lockout account locked account disabled mfa 2fa authenticator verification code cannot get in reset password expired",
 "Phishing / Email Security": "phishing phish suspicious email fake email scam spoof impersonating impersonate link attachment unknown sender verify your account bank details refund customs fee mailbox will be deleted clicked entered password text message caller claiming",
 "Endpoint Security Alert": "malware virus trojan ransomware edr antivirus defender antimalware infected popup pop-up ransom note encrypted files strange extension suffix bitcoin payment demand quarantined suspicious process macro powershell",
 "Network / Firewall": "internet down no connectivity offline wifi wi-fi wireless vpn tunnel firewall router switch latency slow network disconnecting dropping dropped link down isp broadband bandwidth power cut",
 "Cloud (Azure / AWS)": "azure aws vm virtual machine app service s3 bucket subscription instance cloud database sql cpu scaling scale storage account kubernetes 503 timeout resource",
 "Backup & Recovery": "backup back up restore restored snapshot recovery recover restore point deleted file folder overwritten repository retention replication backup job storage target",
 "Microsoft 365 / Software": "outlook teams sharepoint onedrive excel word powerpoint mailbox calendar meeting licence office crash crashes freezing freeze send email outbox sync microsoft 365 m365 application",
 "Hardware / Device": "laptop desktop screen monitor keyboard mouse printer battery dock docking station power button hard drive disk not turning on won't power on cracked dead keys black screen flickering",
 "Data & BI (Qlik / Alteryx)": "qlik alteryx dashboard report reload refresh data refresh kpi totals figures numbers workflow flow etl power bi scheduler ledger data load sales dashboard",
 "Access / Change Request": "new starter joiner joiners leaver ex-employee onboarding offboarding access request permissions group add to remove access contractor provision set up accounts equipment",
}
