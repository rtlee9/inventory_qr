import requests
import json
from typing import Optional
import os
from dotenv import load_dotenv


load_dotenv()

AWS_API_KEY = os.getenv("SHORTENER_API_KEY")
HEADERS = {
    "x-api-key": AWS_API_KEY,
    "Content-Type": "application/json",
}


def create(long_url: str, key: Optional[str]) -> dict:
    """
    Create a shortened URL.

    Args:
    long_url (str): The long URL to be shortened.
    key (str): The custom key for the shortened URL.

    Returns:
    dict: The response containing the shortened URL information.
    """
    body = {
        "longUrl": long_url,
    }
    if key:
        body["customKey"] = key
    response = requests.post(
        "https://api.aws3.link/shorten", headers=HEADERS, data=json.dumps(body)
    ).json()
    return response


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

    # Return the JSON response from the API
    return response.json()


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
