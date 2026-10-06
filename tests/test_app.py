import json
import threading
import unittest
import urllib.error
import urllib.request

from app import make_server


class WesterosApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(0)  # port 0 = OS picks a free port
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path):
        url = f"http://127.0.0.1:{self.port}{path}"
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_root_greets(self):
        status, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertIn("Westeros", body["message"])

    def test_healthz(self):
        status, body = self.get("/healthz")
        self.assertEqual(status, 200)
        # self.assertEqual(body["status"], "ok")
        self.assertEqual(body["status"], "fine")

    def test_list_locations(self):
        status, body = self.get("/locations")
        self.assertEqual(status, 200)
        self.assertIn("winterfell", body["locations"])
        self.assertIn("the-wall", body["locations"])

    def test_known_location(self):
        status, body = self.get("/locations/kings-landing")
        self.assertEqual(status, 200)
        self.assertEqual(body["name"], "King's Landing")
        self.assertTrue(body["fact"])

    def test_location_is_case_insensitive(self):
        status, body = self.get("/locations/Winterfell")
        self.assertEqual(status, 200)
        self.assertEqual(body["region"], "The North")

    def test_unknown_location_is_404(self):
        status, body = self.get("/locations/pentos")
        self.assertEqual(status, 404)
        self.assertIn("error", body)

    def test_unknown_path_is_404(self):
        status, _ = self.get("/nope")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
