import requests
import json
from typing import Optional
import os
from dotenv import load_dotenv
import sqlite3
from contextlib import closing
from urllib.parse import urlencode


load_dotenv()

AWS_API_KEY = os.getenv("SHORTENER_API_KEY")
HEADERS = {
    "x-api-key": AWS_API_KEY,
    "Content-Type": "application/json",
}

conn = sqlite3.connect("url_actions.db")

# Log a URL deletion action
# cursor.execute("INSERT INTO url_actions (action_type, url, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)", ('delete', deleted_url))

# db is set up in CLI `sqlite3 url_actions.db` with
# CREATE TABLE url_actions (
#    id INTEGER PRIMARY KEY,
#    action_type TEXT,
#    long_url TEXT,
#    response_json TEXT,
#    response_code INTEGER,
#    timestamp DATETIME,
#    url_key TEXT
# );


def create(long_url: str, key: Optional[str]) -> dict:
    """
    Create a shortened URL.

    Args:
    long_url (str): The long URL to be shortened.
    key (str): The custom key for the shortened URL.

    Returns:
    dict: The response containing the shortened URL information.
    """
    tracking_params = {"utm_source": "ad-shop", "utm_medium": "qr-sticker", "utm_campaign": "qr-code-stickers"}
    url_params = urlencode(tracking_params)
    if "?" in long_url:
         long_url += "&" + url_params
    else:
         long_url += "?" + url_params
    body = {
        # TODO: append tracking params dict to long_url
        "longUrl": long_url,
    }
    if key:
        body["customKey"] = key
    response = requests.post(
        "https://api.aws3.link/shorten", headers=HEADERS, data=json.dumps(body)
    )
    data = response.json()

    # log to db
    with closing(conn.cursor()) as cursor:
        cursor.execute(
            "INSERT INTO url_actions (action_type, long_url, response_json, response_code, timestamp, url_key) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)",
            ("create", long_url, json.dumps(data), response.status_code, key),
        )

    return data


def delete(key):
    """
    Deletes the specified key from the AWS3 API.

    Args:
    key (str): The key to be deleted.

    Returns:
    dict: The JSON response from the API.
    """
    # Make a POST request to the AWS3 API to remove the specified key
    response = requests.post(
        "https://api.aws3.link/remove",
        headers=HEADERS,
        data=json.dumps({"key": key}),
    )
    data = response.json()

    # log to db
    with closing(conn.cursor()) as cursor:
        cursor.execute(
            "INSERT INTO url_actions (action_type, long_url, response_json, response_code, timestamp, url_key) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)",
            ("delete", None, json.dumps(data), response.status_code, key),
        )

    # Return the JSON response from the API
    return data


def update(key: str, new_long_url: str):
    """
    Update the given key with a new long URL.

    Parameters:
    key (str): The key to be updated.
    new_long_url (str): The new long URL to update with.

    Returns:
    None
    """
    delete(key)
    create(new_long_url, key)


def track(key):
    """
    Tracks hits corresponding to the specified key from the API.

    Args:
    key (str): The key to be tracked.

    Returns:
    dict: The JSON response from the API.
    """
    # Make a POST request to the AWS3 API to remove the specified key
    response = requests.post(
        "https://api.aws3.link/track",
        headers=HEADERS,
        data=json.dumps({"key": key}),
    )

    # Return the JSON response from the API
    return response.json()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CLI for shortned URL manipulation")

    # TODO: make all arguments below optional except for action
    parser.add_argument(
        "action",
        choices=["create", "update", "delete", "track"],
        help="Action to perform",
    )
    parser.add_argument("key", type=str, help="Key to be updated or deleted")
    parser.add_argument(
        "--long-url", type=str, help="New long URL to update with", required=False
    )

    args = parser.parse_args()

    if args.action == "create":
        print(create(args.long_url, args.key))
    elif args.action == "update":
        print(update(args.key, args.long_url))
    elif args.action == "delete":
        print(delete(args.key))
    elif args.action == "track":
        print(track(args.key))
    conn.commit()
