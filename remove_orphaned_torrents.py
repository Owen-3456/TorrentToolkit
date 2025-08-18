import os
import requests
import shutil
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


def get_orphaned_torrents_data():
    """Get orphaned torrent files data without console interaction - for GUI use"""
    try:
        # Login to qBittorrent Web API
        s = requests.Session()
        login_response = s.post(
            f"{qb_url}/api/v2/auth/login",
            data={"username": qb_user, "password": qb_pass},
        )

        if login_response.status_code != 200:
            return {"error": f"Failed to login to qBittorrent: {login_response.status_code}"}

        # Get list of torrents from qBittorrent
        torrents_response = s.get(f"{qb_url}/api/v2/torrents/info")
        if torrents_response.status_code != 200:
            return {"error": f"Failed to get torrents from qBittorrent: {torrents_response.status_code}"}

        torrents = torrents_response.json()
        torrent_files = {os.path.basename(t["content_path"]) for t in torrents}

        # Get files in Completed folder (including subdirectories for categories)
        completed_items = {}
        category_count = 0
        total_items = 0

        # Check if completed folder exists
        if not os.path.exists(completed_folder):
            return {"error": f"Completed folder not found: {completed_folder}"}

        try:
            folder_contents = os.listdir(completed_folder)
        except PermissionError:
            return {"error": f"Cannot access completed folder: {completed_folder}"}

        for item in folder_contents:
            item_path = os.path.join(completed_folder, item)
            if os.path.isdir(item_path):
                # This is a category folder, check inside it
                category_count += 1
                try:
                    subitems = os.listdir(item_path)
                    for subitem in subitems:
                        completed_items[subitem] = item
                        total_items += 1
                except PermissionError:
                    continue
            else:
                # This is a file in the root completed folder
                completed_items[item] = "root"
                total_items += 1

        # Find orphaned files
        orphans = set(completed_items.keys()) - torrent_files

        if not orphans:
            return {"orphans": [], "iso_orphans": [], "deletable_orphans": []}

        # Categorize orphans
        iso_orphans = []
        deletable_orphans = []

        for orphan in sorted(orphans):
            category = completed_items[orphan]
            if category == "ISOs":
                iso_orphans.append((orphan, category))
            else:
                deletable_orphans.append((orphan, category))

        return {
            "orphans": list(orphans),
            "iso_orphans": iso_orphans,
            "deletable_orphans": deletable_orphans,
            "completed_folder": completed_folder
        }

    except Exception as e:
        return {"error": f"Error getting orphaned torrents data: {e}"}


def delete_selected_files(files_to_delete, completed_folder):
    """Delete the selected orphaned files"""
    deleted_count = 0
    error_count = 0
    error_messages = []
    
    for orphan, category in files_to_delete:
        try:
            if category == "root":
                file_path = os.path.join(completed_folder, orphan)
            else:
                file_path = os.path.join(completed_folder, category, orphan)
            
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                deleted_count += 1
            else:
                error_messages.append(f"File not found: {orphan}")
                error_count += 1
                
        except Exception as e:
            error_messages.append(f"Error deleting {orphan}: {e}")
            error_count += 1
    
    return {
        "deleted_count": deleted_count,
        "error_count": error_count,
        "error_messages": error_messages
    }


def remove_orphaned_torrents():
    """Remove orphaned torrent files that are no longer in qBittorrent"""
    try:
        # Login to qBittorrent Web API
        s = requests.Session()
        login_response = s.post(
            f"{qb_url}/api/v2/auth/login",
            data={"username": qb_user, "password": qb_pass},
        )

        if login_response.status_code != 200:
            print(f"❌ Failed to login to qBittorrent: {login_response.status_code}")
            return False

        # Get list of torrents from qBittorrent
        torrents_response = s.get(f"{qb_url}/api/v2/torrents/info")
        if torrents_response.status_code != 200:
            print(
                f"❌ Failed to get torrents from qBittorrent: {torrents_response.status_code}"
            )
            return False

        torrents = torrents_response.json()
        torrent_files = {os.path.basename(t["content_path"]) for t in torrents}

        # Get files in Completed folder (including subdirectories for categories)
        completed_items = {}  # Changed to dict to track which folder each item is in
        category_count = 0
        total_items = 0

        # Check if completed folder exists
        if not os.path.exists(completed_folder):
            print(f"❌ Completed folder not found: {completed_folder}")
            return False

        try:
            folder_contents = os.listdir(completed_folder)
        except PermissionError:
            print(f"❌ Cannot access completed folder: {completed_folder}")
            return False

        for item in folder_contents:
            item_path = os.path.join(completed_folder, item)
            if os.path.isdir(item_path):
                # This is a category folder, check inside it
                category_count += 1
                try:
                    subitems = os.listdir(item_path)
                    print(f"Category '{item}': {len(subitems)} items")
                    for subitem in subitems:
                        completed_items[subitem] = (
                            item  # Track which category folder it's in
                        )
                        total_items += 1
                except PermissionError:
                    print(f"Warning: Cannot access {item_path}")
            else:
                # This is a file in the root completed folder
                completed_items[item] = "root"
                total_items += 1

        print(
            f"Scanned {category_count} category folders, found {total_items} total items"
        )

        # Debug information
        print(f"Found {len(torrents)} torrents in qBittorrent")
        print(f"Found {len(completed_items)} items in completed folder")
        print(f"Torrent files: {sorted(list(torrent_files))[:5]}...")  # Show first 5
        print(
            f"Completed items: {sorted(list(completed_items.keys()))[:5]}..."
        )  # Show first 5
        print()

        # Find orphaned files
        orphans = set(completed_items.keys()) - torrent_files

        if not orphans:
            print("✅ No orphaned files found!")
            return True

        print(f"\n🔍 Found {len(orphans)} orphaned files:")

        # Categorize orphans
        iso_orphans = []
        deletable_orphans = []

        for orphan in sorted(orphans):
            category = completed_items[orphan]
            if category == "ISOs":
                iso_orphans.append((orphan, category))
            else:
                deletable_orphans.append((orphan, category))

        # Show ISO files (excluded by default)
        if iso_orphans:
            print(f"\n📀 ISO files (excluded from deletion by default):")
            for i, (orphan, category) in enumerate(iso_orphans, 1):
                print(f"  {i}. {orphan} (in {category})")

        # Show deletable orphans
        if deletable_orphans:
            print(f"\n🗑️  Files available for deletion:")
            for i, (orphan, category) in enumerate(deletable_orphans, 1):
                print(f"  {i}. {orphan} (in {category})")
        else:
            print("\n✅ No deletable orphaned files found (only ISOs)!")
            return True

        # Get user confirmation and selection
        if not get_user_confirmation(deletable_orphans, completed_folder):
            print("❌ Operation cancelled by user")
            return False

        return True

    except Exception as e:
        print(f"❌ Error removing orphaned torrents: {e}")
        return False


def get_user_confirmation(deletable_orphans, completed_folder):
    """Get user confirmation and allow selection of files to exclude from deletion"""
    if not deletable_orphans:
        return False

    print(f"\n⚠️  WARNING: This will permanently delete the selected files from:")
    print(f"   {completed_folder}")

    # Ask if user wants to proceed
    while True:
        proceed = (
            input("\nDo you want to proceed with deletion? (y/n): ").lower().strip()
        )
        if proceed in ["y", "yes"]:
            break
        elif proceed in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no")

    # Allow user to exclude specific files
    excluded_indices = set()

    while True:
        exclude_input = input(
            "\nEnter numbers of files to EXCLUDE from deletion (comma-separated, or 'none' to delete all): "
        ).strip()

        if exclude_input.lower() in ["none", ""]:
            break

        try:
            if exclude_input:
                indices = [int(x.strip()) for x in exclude_input.split(",")]
                valid_indices = []
                for idx in indices:
                    if 1 <= idx <= len(deletable_orphans):
                        valid_indices.append(idx)
                        excluded_indices.add(idx - 1)  # Convert to 0-based
                    else:
                        print(
                            f"Invalid number: {idx}. Please use numbers 1-{len(deletable_orphans)}"
                        )
                        continue

                if valid_indices:
                    print(
                        f"Files to exclude: {', '.join(str(x) for x in valid_indices)}"
                    )
                break
        except ValueError:
            print("Please enter valid numbers separated by commas, or 'none'")

    # Show final deletion list
    files_to_delete = [
        (orphan, category)
        for i, (orphan, category) in enumerate(deletable_orphans)
        if i not in excluded_indices
    ]

    if not files_to_delete:
        print("\n✅ No files selected for deletion")
        return False

    print(f"\n🗑️  Final deletion list ({len(files_to_delete)} files):")
    for orphan, category in files_to_delete:
        print(f"  • {orphan} (in {category})")

    # Final confirmation
    while True:
        final_confirm = (
            input(f"\nConfirm deletion of {len(files_to_delete)} files? (y/n): ")
            .lower()
            .strip()
        )
        if final_confirm in ["y", "yes"]:
            break
        elif final_confirm in ["n", "no"]:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no")

    # Perform deletion
    return delete_files(files_to_delete, completed_folder)


def delete_files(files_to_delete, completed_folder):
    """Delete the selected orphaned files"""
    deleted_count = 0
    error_count = 0

    print(f"\n🚀 Starting deletion of {len(files_to_delete)} files...")

    for orphan, category in files_to_delete:
        try:
            if category == "root":
                file_path = os.path.join(completed_folder, orphan)
            else:
                file_path = os.path.join(completed_folder, category, orphan)

            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"✅ Deleted directory: {orphan}")
                else:
                    os.remove(file_path)
                    print(f"✅ Deleted file: {orphan}")
                deleted_count += 1
            else:
                print(f"⚠️  File not found (may have been moved): {orphan}")

        except Exception as e:
            print(f"❌ Error deleting {orphan}: {e}")
            error_count += 1

    print(f"\n📊 Deletion Summary:")
    print(f"   ✅ Successfully deleted: {deleted_count} files")
    if error_count > 0:
        print(f"   ❌ Errors: {error_count} files")

    return error_count == 0


def main():
    remove_orphaned_torrents()


if __name__ == "__main__":
    main()
