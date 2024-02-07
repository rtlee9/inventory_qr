from ..url import update, delete, create

import unittest
from unittest.mock import patch
import json

headers = {
    "x-api-key": "oeOkrE9AOw5jsUOEpz1OIai4N0kf8c4uZj75jPh8",
    "Content-Type": "application/json",
}


class TestCreateFunction(unittest.TestCase):

    @patch("requests.post")
    def test_create_with_long_url_and_target(self, mock_post):
        mock_post.return_value.json.return_value = {
            "shortUrl": "https://example.com/s/abc123"
        }
        result = create("https://www.example.com/very/long/url", "custom_key")
        self.assertEqual(result, {"shortUrl": "https://example.com/s/abc123"})

    @patch("requests.post")
    def test_create_with_long_url_only(self, mock_post):
        mock_post.return_value.json.return_value = {
            "shortUrl": "https://example.com/s/def456"
        }
        result = create("https://www.example.com/another/long/url", None)
        self.assertEqual(result, {"shortUrl": "https://example.com/s/def456"})

    @patch("requests.post")
    def test_create_with_target_only(self, mock_post):
        mock_post.return_value.json.return_value = {
            "shortUrl": "https://example.com/s/ghi789"
        }
        result = create(None, "custom_key")
        self.assertEqual(result, {"shortUrl": "https://example.com/s/ghi789"})


class TestDeleteFunction(unittest.TestCase):

    @patch("requests.post")
    def test_delete_valid_key(self, mock_post):
        mock_post.return_value.json.return_value = {
            "message": "Key deleted successfully"
        }
        key = "valid_key"
        response = delete(key)
        mock_post.assert_called_once_with(
            "https://api.aws3.link/remove",
            headers=headers,
            data=json.dumps({"key": key}),
        )
        self.assertEqual(response, {"message": "Key deleted successfully"})

    @patch("requests.post")
    def test_delete_invalid_key(self, mock_post):
        mock_post.return_value.json.return_value = {"error": "Invalid key"}
        key = "invalid_key"
        response = delete(key)
        mock_post.assert_called_once_with(
            "https://api.aws3.link/remove",
            headers=headers,
            data=json.dumps({"key": key}),
        )
        self.assertEqual(response, {"error": "Invalid key"})

    @patch("requests.post")
    def test_response_format(self, mock_post):
        mock_post.return_value.json.return_value = {
            "message": "Key deleted successfully"
        }
        key = "valid_key"
        response = delete(key)
        self.assertIsInstance(response, dict)


if __name__ == "__main__":
    unittest.main()
