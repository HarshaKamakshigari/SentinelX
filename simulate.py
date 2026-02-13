"""
SentinelX Simulation — Test the full LangGraph pipeline.
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8001/ingest"

TEST_CASES = [
    {
        "name": "🔴 Encoded PowerShell Attack",
        "log": {
            "host": "finance-01",
            "event_type": "process_creation",
            "command_line": "powershell.exe -enc JAB3AGUAYgBjAGwAaQBlAG4AdAA=",
            "destination_ip": "45.77.12.90",
        },
    },
    {
        "name": "🟠 Known Malicious File",
        "log": {
            "host": "hr-pc",
            "event_type": "file_create",
            "file_hash": "abcd1234",
        },
    },
    {
        "name": "🟡 Suspicious C2 Beacon",
        "log": {
            "host": "dev-server",
            "event_type": "network_connection",
            "destination_ip": "185.220.101.1",
        },
    },
    {
        "name": "🟢 Clean Event (Notepad)",
        "log": {
            "host": "user-laptop",
            "event_type": "process_creation",
            "command_line": "notepad.exe report.txt",
        },
    },
]


def run():
    print("=" * 60)
    print("  SentinelX — LangGraph Pipeline Simulation")
    print("=" * 60)

    for tc in TEST_CASES:
        print(f"\n{'─' * 50}")
        print(f"  Test: {tc['name']}")
        print(f"{'─' * 50}")
        try:
            start = time.time()
            resp = requests.post(BASE_URL, json=tc["log"], timeout=30)
            latency = time.time() - start

            resp.raise_for_status()
            report = resp.json()

            print(f"  Latency     : {latency:.2f}s")
            print(f"  Incident ID : {report.get('incident_id')}")
            print(f"  Severity    : {report.get('severity')}")
            print(f"  Confidence  : {report.get('confidence')}")
            print(f"  MITRE       : {report.get('mitre_techniques')}")
            print(f"  Agents      : {report.get('agents_invoked')}")
            print(f"  Summary     : {report.get('summary', '')[:120]}...")
        except Exception as e:
            print(f"  ❌ FAILED: {e}")

    print(f"\n{'=' * 60}")
    print("  Simulation Complete")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    run()
