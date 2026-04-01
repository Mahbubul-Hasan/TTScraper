import requests
import re
import json
import sys

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.tiktok.com/",
}

def get_video_stats(url: str) -> dict:
    res = requests.get(url, headers=HEADERS, timeout=10)

    if res.status_code != 200:
        raise Exception(f"HTTP {res.status_code}")

    match = re.search(
        r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>',
        res.text,
        re.DOTALL
    )
    if not match:
        raise Exception("Data not found")

    data = json.loads(match.group(1))

    stats = (
        data.get("__DEFAULT_SCOPE__", {})
            .get("webapp.video-detail", {})
            .get("itemInfo", {})
            .get("itemStruct", {})
            .get("stats")
    )

    if not stats:
        raise Exception("Video stats not found")

    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <video_url>")
        exit()

    try:
        print(json.dumps(get_video_stats(sys.argv[1]), indent=2))
    except Exception as e:
        print("Error:", e)