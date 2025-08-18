import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CONFIGURATION - Update these values with your own
QB_HOST = os.getenv("QB_URL", "http://localhost:8080")
USERNAME = os.getenv("QB_USER", "admin")
PASSWORD = os.getenv("QB_PASS", "admin")

# Best trackers list, updated regularly
# Alternatively, you can put your own list of trackers here
TRACKERS_URL = (
    "https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt"
)


def login(session):
    r = session.post(
        f"{QB_HOST}/api/v2/auth/login",
        data={"username": USERNAME, "password": PASSWORD},
    )
    if r.text != "Ok.":
        raise Exception("Failed to log in to qBittorrent WebUI")


def get_torrents(session):
    r = session.get(f"{QB_HOST}/api/v2/torrents/info")
    return r.json()


def edit_trackers(session, hash, torrent_name, new_trackers):
    # Get existing trackers
    r = session.get(f"{QB_HOST}/api/v2/torrents/trackers", params={"hash": hash})
    existing_trackers = set(t["url"] for t in r.json())

    # Only add trackers that aren't already there
    unique_trackers = [t for t in new_trackers if t not in existing_trackers]
    if unique_trackers:
        trackers_str = "\n".join(unique_trackers)
        session.post(
            f"{QB_HOST}/api/v2/torrents/addTrackers",
            data={"hash": hash, "urls": trackers_str},
        )
        print(f"✅ Added trackers to {torrent_name}")
    else:
        print(f"ℹ️ No new trackers needed for {torrent_name}")


def add_popular_trackers():
    """Add popular trackers to all public torrents in qBittorrent"""
    trackers_to_add = []
    try:
        response = requests.get(TRACKERS_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        trackers_to_add = [
            tracker.strip() for tracker in response.text.splitlines() if tracker.strip()
        ]
        if not trackers_to_add:
            print("⚠️ Fetched tracker list is empty. No trackers will be added.")
            return False
        print(f"ℹ️ Successfully fetched {len(trackers_to_add)} trackers.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching trackers: {e}")
        print("ℹ️ Proceeding without adding new trackers.")
        return False  # Or, optionally, proceed with an empty list or a default list

    try:
        with requests.Session() as s:
            login(s)
            torrents = get_torrents(s)
            for torrent in torrents:
                if not torrent.get("private"):  # Only edit public torrents
                    edit_trackers(s, torrent["hash"], torrent["name"], trackers_to_add)
        return True
    except Exception as e:
        print(f"❌ Error adding trackers: {e}")
        return False


def main():
    add_popular_trackers()


if __name__ == "__main__":
    main()