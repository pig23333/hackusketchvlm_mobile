"""
Integration tests for SketchVLM Mobile REST API server.
All comments and documentation are in English.
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main


class TestServerEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(main.app)

    def test_health_check(self):
        """Verify /health endpoint returns 200 and healthy status."""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("supported_models", data)

    def test_web_dashboard(self):
        """Verify root / serves HTML dashboard."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("SketchVLM Video AI Service", resp.text)

    def test_status_not_found(self):
        """Verify /api/video/status returns 404 for unknown job ID."""
        resp = self.client.get("/api/video/status/job_nonexistent")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
