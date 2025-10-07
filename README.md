# Server Stress Tester

A Python-based tool for testing server performance by measuring response times and simulating high request loads. Controlled via a Telegram bot, this script pings a target URL, evaluates server strength, and sends a configurable number of HTTP requests to stress-test the server. Results are logged to a file and reported back via Telegram.

**Note**: This tool is for educational purposes only. Use responsibly and with explicit permission from server owners.

## Features
- **Ping Test**: Measures server response time for a single request.
- **Capacity Test**: Sends 1000 async HTTP requests to calculate average request time.
- **Server Strength Evaluation**:
  - Strong: Response time < 1s and avg request time < 0.1s.
  - Medium: Response time < 2s or avg request time < 0.5s.
  - Weak: Otherwise.
- **Stress Test**: Sends 10K (Strong), 25K (Medium), or 50K (Weak) async requests to simulate load.
- **Telegram Integration**: Control via `/scan <url>` command, with real-time results sent to a private chat.
- **Stealth**: Randomizes user-agents, referers, cookies, and query parameters to mimic varied traffic.
- **Logging**: Saves successful request details (URL, status, time) to `attack_log.txt`.

## Prerequisites
- **Python 3.8+** (tested on 3.12)
- **Termux** (for mobile deployment, optional)
- **Dependencies**:
  - `requests`
  - `aiohttp`
  - `python-telegram-bot>=20.0`

## Installation
1. **Install Termux** (if using mobile):
   ```bash
   pkg install python
2. Install Python dependencies: 
pip install requests aiohttp python-telegram-bot>=20.0
3. clone
4. git clone https://github.com/yourusername/server-stress-tester.git
cd server-stress-tester
