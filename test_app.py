"""
Automated Comprehensive Test Suite for 5G Network Slicing Application
Tests routes, API endpoints, scenario allocations, dynamic algorithms,
capacity constraints (sum == 100), non-negativity, QoS, and history.
"""

import unittest
import json
from app import app, TOTAL_CAPACITY, MIN_RESERVATIONS, DEFAULT_STATE

class Test5GNetworkSlicing(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_routes_status_codes(self):
        """Test all frontend HTML page routes return 200 OK"""
        routes = ["/", "/dashboard", "/results"]
        for r in routes:
            res = self.app.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} failed with {res.status_code}")
            self.assertIn(b"5G", res.data)

    def test_api_state_initial(self):
        """Test initial state has 100 Mbps total and 20/30/50 baseline"""
        res = self.app.get("/api/state")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])

        state = data["state"]
        self.assertEqual(state["total_bandwidth"], 100)
        self.assertEqual(state["allocated_bandwidth"], 100)
        self.assertEqual(state["available_bandwidth"], 0)

        slices = state["slices"]
        total_bw = slices["emergency"]["bandwidth"] + slices["iot"]["bandwidth"] + slices["video"]["bandwidth"]
        self.assertEqual(total_bw, 100, "Initial bandwidth sum must equal 100")
        self.assertEqual(slices["emergency"]["bandwidth"], 20)
        self.assertEqual(slices["iot"]["bandwidth"], 30)
        self.assertEqual(slices["video"]["bandwidth"], 50)

    def test_all_scenarios_and_invariant_100mbps(self):
        """Test all 7 simulation scenarios and ensure sum == 100 Mbps and >= 0"""
        scenarios = ["normal", "emergency", "iot", "video", "congestion", "degradation", "recover"]

        for scen in scenarios:
            res = self.app.post("/api/simulate",
                                data=json.dumps({"scenario": scen}),
                                content_type="application/json")
            self.assertEqual(res.status_code, 200, f"Scenario '{scen}' failed")
            data = json.loads(res.data)
            self.assertTrue(data["success"])

            alloc = data["allocation"]
            total = alloc["emergency"] + alloc["iot"] + alloc["video"]
            self.assertEqual(total, 100, f"Scenario '{scen}' total bandwidth violation: {total} != 100")

            # Non-negativity check
            for k in ["emergency", "iot", "video"]:
                self.assertGreaterEqual(alloc[k], 0, f"Scenario '{scen}' negative allocation for {k}")

            # Minimum guarantee preservation check
            self.assertGreaterEqual(alloc["emergency"], MIN_RESERVATIONS["emergency"])
            self.assertGreaterEqual(alloc["iot"], MIN_RESERVATIONS["iot"])
            self.assertGreaterEqual(alloc["video"], MIN_RESERVATIONS["video"])

    def test_emergency_priority_preemption(self):
        """Emergency scenario must boost emergency bandwidth and protect priority"""
        res = self.app.post("/api/simulate",
                            data=json.dumps({"scenario": "emergency"}),
                            content_type="application/json")
        data = json.loads(res.data)
        alloc = data["allocation"]
        self.assertGreater(alloc["emergency"], 20, "Emergency bandwidth should increase during surge")
        self.assertEqual(alloc["emergency"] + alloc["iot"] + alloc["video"], 100)

    def test_congestion_and_unmet_demand(self):
        """Congestion scenario should report unmet demand when requested > 100 Mbps"""
        res = self.app.post("/api/simulate",
                            data=json.dumps({"scenario": "congestion"}),
                            content_type="application/json")
        data = json.loads(res.data)
        self.assertGreater(data["total_demand"], 100, "Congestion total demand should exceed 100")
        self.assertGreater(data["unmet_demand"], 0, "Congestion should report unmet demand")
        self.assertEqual(data["allocation"]["emergency"] + data["allocation"]["iot"] + data["allocation"]["video"], 100)

    def test_slice_degradation_and_qos(self):
        """Degradation scenario should mark video slice as DEGRADED and elevate loss/jitter"""
        res = self.app.post("/api/simulate",
                            data=json.dumps({"scenario": "degradation"}),
                            content_type="application/json")
        data = json.loads(res.data)
        state = data["state"]
        self.assertEqual(state["slices"]["video"]["status"], "DEGRADED")

        # Now test recover restores normal status
        res2 = self.app.post("/api/simulate",
                             data=json.dumps({"scenario": "recover"}),
                             content_type="application/json")
        data2 = json.loads(res2.data)
        self.assertEqual(data2["state"]["slices"]["video"]["status"], "ACTIVE")

    def test_custom_demand_allocation(self):
        """Test custom interactive demand allocation"""
        custom_payload = {
            "scenario": "custom",
            "demands": {"emergency": 70, "iot": 50, "video": 40}
        }
        res = self.app.post("/api/simulate",
                            data=json.dumps(custom_payload),
                            content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        alloc = data["allocation"]
        self.assertEqual(alloc["emergency"] + alloc["iot"] + alloc["video"], 100)
        self.assertGreaterEqual(alloc["emergency"], 15)
        self.assertGreaterEqual(alloc["iot"], 10)
        self.assertGreaterEqual(alloc["video"], 5)

    def test_invalid_scenario_error_handling(self):
        """Invalid scenario name should return 400 Bad Request with meaningful message"""
        res = self.app.post("/api/simulate",
                            data=json.dumps({"scenario": "unknown_scenario_xyz"}),
                            content_type="application/json")
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertFalse(data["success"])
        self.assertIn("Invalid scenario", data["error"])

    def test_reset_endpoint(self):
        """Reset endpoint should restore baseline 20/30/50 allocation"""
        # First put it in congestion
        self.app.post("/api/simulate", data=json.dumps({"scenario": "congestion"}), content_type="application/json")

        # Now reset
        res = self.app.post("/api/reset")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        alloc = data["after"]
        self.assertEqual(alloc["emergency"], 20)
        self.assertEqual(alloc["iot"], 30)
        self.assertEqual(alloc["video"], 50)
        self.assertEqual(alloc["emergency"] + alloc["iot"] + alloc["video"], 100)

    def test_history_and_clear(self):
        """History endpoint should record simulation runs and clear cleanly"""
        self.app.post("/api/simulate", data=json.dumps({"scenario": "emergency"}), content_type="application/json")
        self.app.post("/api/simulate", data=json.dumps({"scenario": "iot"}), content_type="application/json")

        res = self.app.get("/api/history")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertGreater(data["count"], 0)
        self.assertIn("emergency_bw", data["history"][0])

        # Test clear
        clear_res = self.app.post("/api/history/clear")
        self.assertEqual(clear_res.status_code, 200)

        res_after = self.app.get("/api/history")
        data_after = json.loads(res_after.data)
        self.assertEqual(data_after["count"], 0)

    def test_thresholds_endpoint(self):
        """Thresholds endpoint can read and update QoS thresholds"""
        res = self.app.get("/api/thresholds")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("latency_warning", data["thresholds"])

        # Update
        post_res = self.app.post("/api/thresholds",
                                 data=json.dumps({"latency_warning": 45.0, "latency_fail": 90.0}),
                                 content_type="application/json")
        self.assertEqual(post_res.status_code, 200)
        post_data = json.loads(post_res.data)
        self.assertEqual(post_data["thresholds"]["latency_warning"], 45.0)

if __name__ == "__main__":
    unittest.main()

