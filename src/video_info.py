import json
import sys
import time
import random
import re
from playwright.sync_api import sync_playwright

def get_exact_video_stats_stealth(url: str) -> dict:
    with sync_playwright() as p:
        # Launch browser with specific args to bypass detection
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ])
        
        # Use a real session cookie if provided to get exact numbers
        # You can get this from your browser's DevTools (Cookie: sessionid=...)
        session_id = "YOUR_SESSION_ID_HERE" # Replace with your actual sessionid
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        if session_id and session_id != "YOUR_SESSION_ID_HERE":
            context.add_cookies([{
                "name": "sessionid",
                "value": session_id,
                "domain": ".tiktok.com",
                "path": "/"
            }])
        
        page = context.new_page()
        
        # Hide the 'webdriver' property to remain stealthy
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            # Navigate to the video URL
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Small random delay to mimic human behavior
            time.sleep(random.uniform(2, 4))
            
            # Find the script tag that contains the rehydration data
            script_ids = ["__UNIVERSAL_DATA_FOR_REHYDRATION__", "SIGI_STATE", "sigi-state", "RENDER_DATA"]
            data = None
            
            for script_id in script_ids:
                element = page.locator(f"script#{script_id}").first
                if element.count() > 0:
                    content = element.inner_html()
                    if content:
                        try:
                            # Handle URL-encoded content (common in RENDER_DATA)
                            if content.startswith("%"):
                                from urllib.parse import unquote
                                content = unquote(content)
                            data = json.loads(content)
                            break
                        except:
                            continue
            
            if not data:
                # Fallback: Extract from raw page source using regex
                html = page.content()
                match = re.search(r'\"stats\":(\{.*?\"diggCount\":\d+.*?\})', html)
                if match:
                    return json.loads(match.group(1))
                raise Exception("TikTok blocked the browser or layout changed.")

            # Recursive search for stats to handle dynamic JSON paths
            def find_stats(obj):
                if isinstance(obj, dict):
                    # Prioritize 'stats' over 'statsV2' for exact numbers
                    if "diggCount" in obj and "playCount" in obj:
                        # Ensure it's not the V2 version which has strings
                        if isinstance(obj.get("diggCount"), int):
                            return obj
                    
                    # Store potential V2 stats as fallback
                    v2_stats = None
                    if "diggCount" in obj and "playCount" in obj:
                        v2_stats = obj

                    for v in obj.values():
                        res = find_stats(v)
                        if res: return res
                    
                    return v2_stats # Return V2 if exact not found in this branch
                elif isinstance(obj, list):
                    for item in obj:
                        res = find_stats(item)
                        if res: return res
                return None

            stats = find_stats(data)
            
            if not stats:
                # Last resort: Try to find any digits for diggCount in the raw HTML
                html = page.content()
                # Look for the pattern "diggCount":12345
                match = re.search(r'\"diggCount\":(\d+)', html)
                if match:
                    # If we found a raw digit, let's try to capture the whole block
                    stats_match = re.search(r'\"stats\":(\{.*?\"diggCount\":' + match.group(1) + r'.*?\})', html)
                    if stats_match:
                        return json.loads(stats_match.group(1))

            if not stats:
                raise Exception("Could not find exact stats in page data.")

            return stats

        finally:
            browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.video_info <url>")
        sys.exit(1)

    try:
        result = get_exact_video_stats_stealth(sys.argv[1])
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")