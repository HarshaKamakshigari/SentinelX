# Incident Report: SOC-4CBF5EC8

## Overview

| Field | Value |
|---|---|
| Incident ID | SOC-4CBF5EC8 |
| Timestamp | 2026-03-11T21:08:34.058329+00:00 |
| Host | finance-01 |
| Severity | HIGH |
| Confidence | 0.9 |
| MITRE Techniques | T1059.001, T1027 |
| Agents Invoked | ThreatIntelAgent |

## Summary

On 2026-03-11 at 21:08:09 UTC, a highly suspicious PowerShell process (`powershell.exe`) was initiated on the `finance-01` host by the `admin` user. The command line, `powershell.exe -enc SGVsbG8gV29ybGQ=`, utilized an encoded command, a common obfuscation technique employed by adversaries. This process had a null parent, indicating a potentially unusual or direct execution. While the decoded command ("Hello World") is benign, the execution pattern itself, especially on a sensitive finance host and by an administrator, is indicative of potential reconnaissance, initial access, or persistence attempts. The process was observed attempting to communicate with destination IP `45.77.12.90`. No direct malware or threat intelligence match was found for the specific command or destination IP; however, the observed behavior aligns with known adversarial tactics. The incident is triaged with HIGH severity and 0.9 confidence, warranting immediate investigation.

## Timeline

1. 2026-03-11T21:08:09.348216+00:00: A `process_creation` event (ID: `3e672360-5b1a-4dc5-a47c-0d8c9ed0a88c`) for `powershell.exe` was detected on host `finance-01`.
2. The `powershell.exe` process was executed by the `admin` user with the command line `powershell.exe -enc SGVsbG8gV29ybGQ=`.
3. The process was observed with a null parent process, indicating an unusual execution chain.
4. The command was observed attempting to communicate with destination IP `45.77.12.90`.
5. Analysis determined the use of an encoded PowerShell command, a common obfuscation technique, leading to a HIGH severity and 0.9 confidence triage.
6. No direct malware or threat intelligence match was found for the specific command or destination IP, but the execution pattern is highly suspicious and consistent with adversarial activity.

## Detection Details

| Category | Result |
|---|---|
| Heuristic Risk | 0.36842105263157887 |
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

1. Validate whether the encoded PowerShell execution was authorized administrative activity.
2. Isolate and investigate host `finance-01` if activity cannot be confirmed as legitimate.
3. Correlate with authentication logs and EDR telemetry for the `admin` account around event time.
4. Block or monitor outbound communication to `45.77.12.90` pending investigation results.
5. Hunt for similar encoded PowerShell patterns across finance and privileged endpoints.