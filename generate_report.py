import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Settings
qb_url = os.getenv("QB_URL")
qb_user = os.getenv("QB_USER", "admin")
qb_pass = os.getenv("QB_PASS", "admin")


def generate_html_report():
    """Generate a comprehensive HTML report of qBittorrent status with graphs"""
    try:
        # Login to qBittorrent Web API
        s = requests.Session()
        login_response = s.post(
            f"{qb_url}/api/v2/auth/login",
            data={"username": qb_user, "password": qb_pass},
        )

        if login_response.status_code != 200:
            print(f"❌ Failed to login to qBittorrent: {login_response.status_code}")
            return False, None

        # Get server info
        server_info = s.get(f"{qb_url}/api/v2/app/version").text.strip('"')

        # Get torrents info
        torrents_response = s.get(f"{qb_url}/api/v2/torrents/info")
        if torrents_response.status_code != 200:
            print(
                f"❌ Failed to get torrents from qBittorrent: {torrents_response.status_code}"
            )
            return False, None

        torrents = torrents_response.json()

        # Generate statistics
        stats = calculate_statistics(torrents)

        # Generate HTML report
        html_content = generate_html_content(server_info, stats, torrents)

        # Save HTML file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qbittorrent_report_{timestamp}.html"
        filepath = os.path.join(os.getcwd(), filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ HTML report generated: {filename}")
        return True, filepath

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False, None


def calculate_statistics(torrents):
    """Calculate statistics from torrents data"""
    stats = {}

    # Basic counts
    stats["total_torrents"] = len(torrents)
    stats["downloading"] = len(
        [t for t in torrents if t["state"] in ["downloading", "queuedDL", "stalledDL"]]
    )
    stats["seeding"] = len(
        [t for t in torrents if t["state"] in ["uploading", "queuedUP", "stalledUP"]]
    )
    stats["completed"] = len([t for t in torrents if t["state"] == "uploading"])
    stats["paused"] = len([t for t in torrents if "paused" in t["state"]])
    stats["error"] = len([t for t in torrents if "error" in t["state"]])

    # Size statistics
    stats["total_size"] = sum(t["size"] for t in torrents)
    stats["downloaded"] = sum(t["downloaded"] for t in torrents)
    stats["uploaded"] = sum(t["uploaded"] for t in torrents)
    stats["ratio"] = (
        stats["uploaded"] / stats["downloaded"] if stats["downloaded"] > 0 else 0
    )

    # Categories
    categories = {}
    for torrent in torrents:
        cat = torrent.get("category", "Uncategorized") or "Uncategorized"
        categories[cat] = categories.get(cat, 0) + 1
    stats["categories"] = categories

    # States distribution
    states = {}
    for torrent in torrents:
        state = torrent["state"]
        states[state] = states.get(state, 0) + 1
    stats["states"] = states

    # Active torrents
    stats["active_torrents"] = [
        t for t in torrents if t["state"] in ["downloading", "uploading"]
    ][:10]

    return stats


def generate_html_content(server_info, stats, torrents):
    """Generate HTML content with charts and styling"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>qBittorrent Status Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 1.1em;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .charts-section {{
            padding: 30px;
            background: #f8f9fa;
        }}
        .chart-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }}
        .chart-box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .chart-box h3 {{
            margin: 0 0 20px 0;
            text-align: center;
            color: #667eea;
        }}
        .active-torrents {{
            padding: 30px;
        }}
        .torrent-item {{
            display: flex;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .torrent-icon {{
            margin-right: 10px;
            font-size: 1.2em;
        }}
        .torrent-name {{
            flex: 1;
            font-weight: 500;
        }}
        .torrent-progress {{
            margin-left: 10px;
            padding: 2px 8px;
            background: #e9ecef;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: #e9ecef;
            border-radius: 3px;
            overflow: hidden;
            margin: 5px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 qBittorrent Status Report</h1>
            <p>Generated: {current_time} | Version: {server_info} | Server: {qb_url}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📁 Total Torrents</h3>
                <div class="stat-value">{stats['total_torrents']}</div>
            </div>
            <div class="stat-card">
                <h3>⬇️ Downloading</h3>
                <div class="stat-value">{stats['downloading']}</div>
            </div>
            <div class="stat-card">
                <h3>⬆️ Seeding</h3>
                <div class="stat-value">{stats['seeding']}</div>
            </div>
            <div class="stat-card">
                <h3>⏸️ Paused</h3>
                <div class="stat-value">{stats['paused']}</div>
            </div>
            <div class="stat-card">
                <h3>💾 Total Size</h3>
                <div class="stat-value">{format_bytes(stats['total_size'])}</div>
            </div>
            <div class="stat-card">
                <h3>⬇️ Downloaded</h3>
                <div class="stat-value">{format_bytes(stats['downloaded'])}</div>
            </div>
            <div class="stat-card">
                <h3>⬆️ Uploaded</h3>
                <div class="stat-value">{format_bytes(stats['uploaded'])}</div>
            </div>
            <div class="stat-card">
                <h3>📈 Ratio</h3>
                <div class="stat-value">{stats['ratio']:.2f}</div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-container">
                <div class="chart-box">
                    <h3>Torrent States Distribution</h3>
                    <canvas id="statesChart"></canvas>
                </div>
                <div class="chart-box">
                    <h3>Categories Distribution</h3>
                    <canvas id="categoriesChart"></canvas>
                </div>
            </div>
        </div>
        
        {generate_active_torrents_html(stats['active_torrents'])}
    </div>
    
    <script>
        // States Chart
        const statesCtx = document.getElementById('statesChart').getContext('2d');
        new Chart(statesCtx, {{
            type: 'doughnut',
            data: {{
                labels: {list(stats['states'].keys())},
                datasets: [{{
                    data: {list(stats['states'].values())},
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c',
                        '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // Categories Chart
        const categoriesCtx = document.getElementById('categoriesChart').getContext('2d');
        new Chart(categoriesCtx, {{
            type: 'bar',
            data: {{
                labels: {list(stats['categories'].keys())},
                datasets: [{{
                    label: 'Torrents',
                    data: {list(stats['categories'].values())},
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html


def generate_active_torrents_html(active_torrents):
    """Generate HTML for active torrents section"""
    if not active_torrents:
        return ""

    html = """
        <div class="active-torrents">
            <h3>🚀 Active Torrents</h3>
    """

    for torrent in active_torrents:
        state_icon = "⬇️" if "download" in torrent["state"] else "⬆️"
        progress = torrent["progress"] * 100

        html += f"""
            <div class="torrent-item">
                <div class="torrent-icon">{state_icon}</div>
                <div class="torrent-name">{torrent['name'][:60]}{'...' if len(torrent['name']) > 60 else ''}</div>
                <div class="torrent-progress">{progress:.1f}%</div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
        """

    html += "</div>"
    return html


def format_bytes(bytes_value):
    """Convert bytes to human readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def generate_report():
    """Generate a text report for console use"""
    try:
        success, filepath = generate_html_report()
        if success:
            print(f"✅ HTML report generated successfully!")
            return True
        return False
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False


def main():
    generate_report()


if __name__ == "__main__":
    main()
