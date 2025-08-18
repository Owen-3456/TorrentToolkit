import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Settings
qb_url = os.getenv("QB_URL")
qb_user = os.getenv("QB_USER", "admin")
qb_pass = os.getenv("QB_PASS", "admin")
completed_folder = os.getenv("COMPLETED_FOLDER")

# Validate required environment variables
if not qb_url:
    raise ValueError("QB_URL environment variable is required")
if not completed_folder:
    raise ValueError("COMPLETED_FOLDER environment variable is required")

# Login to qBittorrent Web API
s = requests.Session()
login_response = s.post(
    f"{qb_url}/api/v2/auth/login", data={"username": qb_user, "password": qb_pass}
)

if login_response.status_code != 200:
    raise Exception(f"Failed to login to qBittorrent: {login_response.status_code}")

# Get list of torrents from qBittorrent
torrents_response = s.get(f"{qb_url}/api/v2/torrents/info")
if torrents_response.status_code != 200:
    raise Exception(
        f"Failed to get torrents from qBittorrent: {torrents_response.status_code}"
    )

torrents = torrents_response.json()
torrent_files = {os.path.basename(t["content_path"]) for t in torrents}

# Get files in Completed folder (including subdirectories for categories)
completed_items = {}  # Changed to dict to track which folder each item is in
category_count = 0
total_items = 0

# Check if completed folder exists
if not os.path.exists(completed_folder):
    raise FileNotFoundError(f"Completed folder not found: {completed_folder}")

try:
    folder_contents = os.listdir(completed_folder)
except PermissionError:
    raise PermissionError(f"Cannot access completed folder: {completed_folder}")

for item in folder_contents:
    item_path = os.path.join(completed_folder, item)
    if os.path.isdir(item_path):
        # This is a category folder, check inside it
        category_count += 1
        try:
            subitems = os.listdir(item_path)
            print(f"Category '{item}': {len(subitems)} items")
            for subitem in subitems:
                completed_items[subitem] = item  # Track which category folder it's in
                total_items += 1
        except PermissionError:
            print(f"Warning: Cannot access {item_path}")
    else:
        # This is a file in the root completed folder
        completed_items[item] = "root"
        total_items += 1

print(f"Scanned {category_count} category folders, found {total_items} total items")

# Debug information
print(f"Found {len(torrents)} torrents in qBittorrent")
print(f"Found {len(completed_items)} items in completed folder")
print(f"Torrent files: {sorted(list(torrent_files))[:5]}...")  # Show first 5
print(f"Completed items: {sorted(list(completed_items.keys()))[:5]}...")  # Show first 5
print()

# Find orphaned files
orphans = set(completed_items.keys()) - torrent_files

print("Orphaned files:")
delete_commands = []
iso_orphans = []

for orphan in sorted(orphans):
    category = completed_items[orphan]
    print(f"{orphan} (in {category})")

    if category == "ISOs":
        iso_orphans.append(orphan)
    else:
        # Convert Windows path to Linux path format and create delete command
        linux_path = f"/mnt/y/Completed/{category}/{orphan}"
        delete_commands.append(f'rm -rf "{linux_path}"')

print(f"\nFound {len(orphans)} orphaned files total")
print(f"Excluding {len(iso_orphans)} files in ISOs folder")
print(f"Will delete {len(delete_commands)} orphaned files")

if delete_commands:
    print("\nLinux commands to delete orphaned files (excluding ISOs):")
    print("#!/bin/bash")
    for cmd in delete_commands:
        print(cmd)
else:
    print("\nNo orphaned files to delete (excluding ISOs)")