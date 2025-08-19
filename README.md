# TorrentToolkit

A simple Python GUI for managing qBittorrent torrents.

## Features

- Add popular trackers to torrents
- Remove orphaned download files  
- Generate HTML reports with charts
- Clean dark theme GUI

## Setup

1. Install Python 3.8+
2. Clone this repo
3. Install requirements: `pip install -r requirements.txt`
4. Enable qBittorrent Web UI (Tools → Options → Web UI)
5. Create `.env` file:
   ```
   QB_URL=http://localhost:8080
   QB_USER=admin
   QB_PASS=your_password
   COMPLETED_FOLDER=C:\path\to\downloads
   ```

## Usage

Run the GUI:
```bash
python main.py
```

Or use individual scripts:
```bash
python add_popular_trackers.py
python remove_orphaned_torrents.py  
python generate_report.py
```

## Requirements

- Python 3.8+
- qBittorrent with Web UI enabled
- Dependencies: `requests`, `python-dotenv`, `matplotlib`