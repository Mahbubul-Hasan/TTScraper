import requests
import re
import json
import sys

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
}

def get_stats(username: str) -> dict:
    res = requests.get(
        f"https://www.tiktok.com/@{username}",
        headers=HEADERS,
        timeout=10
    )
    if res.status_code != 200:
        raise Exception(f"HTTP {res.status_code}")

    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
        res.text,
        re.DOTALL
    )
    if not match:
        raise Exception("UNIVERSAL_DATA not found (blocked or changed)")

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        raise Exception("Invalid JSON extracted")

    stats = (
        data.get("__DEFAULT_SCOPE__", {})
            .get("webapp.user-detail", {})
            .get("userInfo", {})
            .get("statsV2")
    )
    if not stats:
        raise Exception("StatsV2 missing (likely bot detection)")

    return stats

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <username>")
        return

    try:
        print(json.dumps(get_stats(sys.argv[1]), indent=4))
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()