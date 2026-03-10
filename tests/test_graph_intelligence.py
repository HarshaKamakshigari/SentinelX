import unittest

from sentinelx.graph.graph_engine import (
    EDGE_TTL_SECONDS,
    add_edges,
    add_nodes,
    prune_graph,
    reset_graph,
    temporal_graph,
)
from sentinelx.graph.graph_layer_node import graph_layer_node
from sentinelx.graph.graph_metrics import compute_graph_score, reset_graph_metrics


class GraphIntelligenceTests(unittest.TestCase):
    def setUp(self) -> None:
        reset_graph()
        reset_graph_metrics()

    def test_add_nodes_and_edges_for_connection_event(self) -> None:
        event = {
            "host": "finance-01",
            "user_id": "alice",
            "process_name": "powershell.exe",
            "destination_ip": "45.77.12.90",
        }

        add_nodes(event)
        add_edges(event)

        self.assertIn("host:finance-01", temporal_graph.nodes)
        self.assertIn("user:alice", temporal_graph.nodes)
        self.assertIn("process:powershell.exe", temporal_graph.nodes)
        self.assertIn("ip:45.77.12.90", temporal_graph.nodes)
        self.assertTrue(temporal_graph.has_edge("process:powershell.exe", "host:finance-01"))
        self.assertTrue(temporal_graph.has_edge("user:alice", "process:powershell.exe"))
        self.assertTrue(temporal_graph.has_edge("process:powershell.exe", "ip:45.77.12.90"))
        self.assertEqual(
            temporal_graph.edges["process:powershell.exe", "ip:45.77.12.90"]["relation"],
            "connected_to",
        )

    def test_prune_graph_removes_expired_edges_and_orphans(self) -> None:
        event = {
            "process_name": "powershell.exe",
            "destination_ip": "45.77.12.90",
        }

        add_nodes(event)
        add_edges(event)
        temporal_graph.edges["process:powershell.exe", "ip:45.77.12.90"]["timestamp"] = 0

        prune_graph(now_ts=EDGE_TTL_SECONDS + 1)

        self.assertEqual(temporal_graph.number_of_edges(), 0)
        self.assertNotIn("process:powershell.exe", temporal_graph.nodes)
        self.assertNotIn("ip:45.77.12.90", temporal_graph.nodes)

    def test_graph_score_drops_for_repeated_connections(self) -> None:
        event = {
            "process_name": "powershell.exe",
            "destination_ip": "45.77.12.90",
        }

        add_nodes(event)
        add_edges(event)
        first_score = compute_graph_score(event)

        add_nodes(event)
        add_edges(event)
        second_score = compute_graph_score(event)

        self.assertGreater(first_score, second_score)
        self.assertGreater(first_score, 0)

    def test_graph_layer_uses_normalized_event(self) -> None:
        result = graph_layer_node(
            {
                "normalized_event": {
                    "process_name": "powershell.exe",
                    "destination_ip": "45.77.12.90",
                },
                "log_data": {},
            }
        )

        self.assertIn("graph_anomaly_score", result)
        self.assertGreater(result["graph_anomaly_score"], 0)


if __name__ == "__main__":
    unittest.main()
