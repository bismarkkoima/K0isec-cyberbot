import unittest

from app import create_app
from tests.test_assistant import FakeLLM
from guardian.assistant import Assistant


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app(Assistant(FakeLLM(available=False))).test_client()

    def test_pages_load(self):
        for path in ["/", "/check", "/lessons", "/lessons/spot-a-scam", "/help"]:
            with self.subTest(path=path):
                resp = self.client.get(path)
                self.assertEqual(resp.status_code, 200)
                self.assertIn("Content-Security-Policy", resp.headers)

    def test_unknown_pages_return_404(self):
        self.assertEqual(self.client.get("/lessons/nope").status_code, 404)
        self.assertEqual(self.client.get("/nope").status_code, 404)
        self.assertEqual(self.client.get("/api/topic/nope").status_code, 404)

    def test_chat_api(self):
        resp = self.client.post("/api/chat", json={"message": "Is it safe to share my password?"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["source"], "safety-guide")

    def test_chat_api_rejects_bad_input(self):
        self.assertEqual(self.client.post("/api/chat", json={}).status_code, 400)
        self.assertEqual(self.client.post("/api/chat", json={"message": 5}).status_code, 400)
        self.assertEqual(self.client.post("/api/chat", data="not json").status_code, 400)
        resp = self.client.post("/api/chat", json={"message": "hi", "history": "bad"})
        self.assertEqual(resp.status_code, 200)

    def test_check_api(self):
        resp = self.client.post("/api/check", json={"text": "Send bitcoin now to claim your prize"})
        self.assertEqual(resp.get_json()["level"], "high")
        self.assertEqual(self.client.post("/api/check", json={"text": ""}).status_code, 400)

    def test_topic_and_status_api(self):
        self.assertIn("password", self.client.get("/api/topic/passwords").get_json()["reply"].lower())
        self.assertFalse(self.client.get("/api/status").get_json()["online"])


if __name__ == "__main__":
    unittest.main()
