import unittest
from unittest.mock import patch
from app.whatsapp.verification import verify


class TestVerification(unittest.TestCase):

    @patch.dict("os.environ", {"WHATSAPP_VERIFY_TOKEN": "school-app-2026"})
    def test_valid_verification(self):
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "school-app-2026",
            "hub.challenge": "abc123"
        }
        response, status = verify(params)
        self.assertEqual(status, 200)
        self.assertEqual(response, "abc123")

    @patch.dict("os.environ", {"WHATSAPP_VERIFY_TOKEN": "school-app-2026"})
    def test_wrong_token_returns_403(self):
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "abc123"
        }
        response, status = verify(params)
        self.assertEqual(status, 403)

    @patch.dict("os.environ", {"WHATSAPP_VERIFY_TOKEN": "school-app-2026"})
    def test_wrong_mode_returns_403(self):
        params = {
            "hub.mode": "unsubscribe",
            "hub.verify_token": "school-app-2026",
            "hub.challenge": "abc123"
        }
        response, status = verify(params)
        self.assertEqual(status, 403)

    @patch.dict("os.environ", {"WHATSAPP_VERIFY_TOKEN": "school-app-2026"})
    def test_missing_params_returns_403(self):
        response, status = verify({})
        self.assertEqual(status, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)

