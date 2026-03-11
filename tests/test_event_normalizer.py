import unittest
import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sentinelx.normalization.event_normalizer import normalize_raw, normalize_structured


class EventNormalizerTests(unittest.TestCase):
    def test_normalize_structured_infers_process_name_from_command_line(self) -> None:
        normalized = normalize_structured(
            {
                "host": "finance-01",
                "event_type": "process_creation",
                "command_line": '"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -enc AAAA',
                "destination_ip": "45.77.12.90",
                "user_id": "alice",
            }
        )

        self.assertEqual(normalized["process_name"], "powershell.exe")
        self.assertEqual(normalized["user_id"], "alice")
        self.assertEqual(normalized["destination_ip"], "45.77.12.90")

    def test_normalize_raw_extracts_ip_and_process_name(self) -> None:
        normalized = normalize_raw("powershell.exe -enc AAAA connecting to 45.77.12.90")

        self.assertEqual(normalized["process_name"], "powershell.exe")
        self.assertEqual(normalized["destination_ip"], "45.77.12.90")
        self.assertEqual(normalized["event_type"], "raw_event")


if __name__ == "__main__":
    unittest.main()
