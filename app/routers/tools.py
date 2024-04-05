import json
import time

import requests
from langchain_core.tools import tool


@tool
def send_notification():
    """Push notification"""
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Authorization": "Basic OTU1NjZhYzgtODk5ZC00MDVkLWJlZGQtMTFjMTMyNTIxZjYz",
        "Content-Type": "application/json",
    }
    payload = {
        "app_id": "c641c4e2-0fc0-4059-b054-c72bab45770e",
        "included_segments": ["Total Subscriptions"],
        "data": {"foo": "bar"},
        "contents": {"en": "Giant shrimp"},
        "headings": {"en": "Found the biggest shrimp I've ever seen."},
        "app_url": "appchatproxy://home/new?id=123",
        "big_picture": "https://img.onesignal.com/tmp/fe0d0e8a-78ea-467a-9e24-7694c6a5f07d/0AAtEOwaQxqUMwlHvmMr_cappucino1.png",
        "android_channel_id": "01d0e1b3-3315-43be-8a3e-0d026757f816",
        "small_icon": "ic_stat_onesignal_default",
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification. Status code:", response.status_code)
        print("Response content:", response.content)


@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int




@tool
def delay(s: int):
    """Delay in s in seconds time"""
    time.sleep(s)


@tool
def create_account(username: str, email: str, address: str) -> str:
    """Use tool to create account"""
    
    return json.dumps({"username": username, "email": email, "address": address})
