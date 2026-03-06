from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.binary_location = "/usr/bin/chromium"

options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/bin/chromedriver")

driver = webdriver.Chrome(service=service, options=options)

username = "tiktok"
url = f"https://www.tiktok.com/@{username}"
driver.get(url)
time.sleep(5)

try:
    print("Title:", driver.title)

    name = driver.find_element(By.CSS_SELECTOR, '[data-e2e="user-subtitle"]').text
    following = driver.find_element(By.CSS_SELECTOR, 'strong[data-e2e="following-count"]').text
    followers = driver.find_element(By.CSS_SELECTOR, 'strong[data-e2e="followers-count"]').text
    likes = driver.find_element(By.CSS_SELECTOR, 'strong[data-e2e="likes-count"]').text

    print("Name:", name)
    print("Following:", following)
    print("Followers:", followers)
    print("Likes:", likes)

except Exception as e:
    print("Error:", e)

driver.quit()