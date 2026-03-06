import requests
import json
import re
import sys


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_profile(username):

    url = f"https://www.tiktok.com/@{username}"

    res = requests.get(url, headers=HEADERS)

    if res.status_code != 200:
        raise Exception(f"Failed request {res.status_code}")

    html = res.text

    # Extract SIGI_STATE JSON
    match = re.search(
        r'<script id="SIGI_STATE" type="application/json">(.*?)</script>',
        html
    )

    if not match:
        raise Exception("SIGI_STATE not found (TikTok likely blocked request)")

    data = json.loads(match.group(1))

    user_data = data["UserModule"]["users"].get(username)
    stats_data = data["UserModule"]["stats"].get(username)

    result = {
        "code": 0,
        "msg": "success",
        "data": {
            "user": {
                "id": user_data["id"],
                "uniqueId": user_data["uniqueId"],
                "nickname": user_data["nickname"],
                "avatarThumb": user_data["avatarThumb"],
                "avatarMedium": user_data["avatarMedium"],
                "avatarLarger": user_data["avatarLarger"],
                "signature": user_data["signature"],
                "verified": user_data["verified"],
                "secUid": user_data["secUid"],
                "privateAccount": user_data["privateAccount"],
                "createTime": user_data["createTime"],
                "bioLink": user_data.get("bioLink", {}),
            },
            "stats": {
                "followingCount": stats_data["followingCount"],
                "followerCount": stats_data["followerCount"],
                "heartCount": stats_data["heartCount"],
                "videoCount": stats_data["videoCount"],
                "diggCount": stats_data["diggCount"],
                "heart": stats_data["heart"],
            }
        }
    }

    return result


def main():

    if len(sys.argv) < 2:
        print("Usage: python main.py username")
        return

    username = sys.argv[1]

    try:

        result = fetch_profile(username)

        print(json.dumps(result, indent=2))

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    main()