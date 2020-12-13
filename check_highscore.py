import re
import os
import time
import json
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

# dirty and quick script for tracking the highscore. buy me a beer :))


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
HIGHSCORE_URL = "https://ctf.cybertalent.no/highscore"
USER_URL = "https://ctf.cybertalent.no/u/{}"
USER_PATH = SCRIPT_PATH + "/users/{}.json"

retries = Retry(
    total=5,
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504]
)
s = requests.Session()
s.mount(HIGHSCORE_URL, HTTPAdapter(max_retries=retries))
r = s.get(HIGHSCORE_URL)

soup = BeautifulSoup(r.content, 'html.parser')

highscore = []
users = {}
for position, li in enumerate(soup.find("ol", class_="liste").find_all("li")):
    # Extract all the user information
    user_id = re.search(r"'/u/(.*?)'", li["onclick"]).group(1)
    points = li.find("span", class_="sum").text.strip()
    username = li.find("span", class_="navn").text.strip()[:-len(points)]
    

    # Initialize the user object and add it to the highscore table
    user = {
        "position": position + 1,
        "user_id": user_id,
        "name": username,
        "points": int(points),
    }
    highscore.append(user)

    # Let's add their current solves
    user = user.copy()
    user["categories"] = {}
    r = s.get(USER_URL.format(user_id))
    soup = BeautifulSoup(r.content, 'html.parser')

    # Loop through the categories and map the percentages
    for li in soup.find("ol", class_="liste").find_all("li"):
        percent = li.find("span", class_="sum").text.strip()
        name = li.find("span", class_="navn").text.strip()[:-len(percent)]
        user["categories"][name] = int(percent[:-1]) # Remove the %

    # Save the individual data for each user
    with open(USER_PATH.format(user_id), "w") as f:
        json.dump(user, f, indent=4)
    print("Done processing: {}".format(user_id))

    # Let's be a bit nice and sleep for a bit
    time.sleep(0.2)


with open("{}/highscore.min.json".format(SCRIPT_PATH), "w") as f:
    json.dump(highscore, f)

with open("{}/highscore.json".format(SCRIPT_PATH), "w") as f:
    json.dump(highscore, f, indent=4)
