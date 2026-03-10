# Quick Start Guide

Get the Hunter Memory System running in 5 minutes.

## Prerequisites

- Python 3.12+
- 1GB+ RAM
- 500MB+ disk space
- OpenClaw 2026.2.0+

## Installation

### Linux / Mac

```bash
cd hunter-memory-system
./install.sh
```

### Windows

```powershell
cd hunter-memory-system
.\install.ps1
```

## What the Installer Does

1. Checks system requirements (RAM, disk space, Python version)
2. Installs Python dependencies
3. Asks for your OpenClaw memory directory path
4. Indexes all your memory files
5. Installs the OpenClaw plugin
6. Asks if you want to update config automatically
7. Optionally enables aggressive token compaction (saves 10-20% extra)

## Post-Installation

### Start the Memory Server

```bash
# Linux/Mac
cd hunter-memory-system
python3 server.py

# Windows
cd hunter-memory-system
python server.py
```

Keep this running in the background.

### Restart OpenClaw

```bash
openclaw gateway restart
```

### Test It

```bash
# Check server health
curl http://127.0.0.1:8765/health

# Should return: {"status":"ok"}
```

Or just use OpenClaw naturally:
```
You: "What do you remember about [topic]?"
OpenClaw: [searches and returns results]
```

## Auto-Start (Optional)

### Linux (systemd)

```bash
# Edit the service file first
nano systemd/hunter-memory.service
# Replace USERNAME with your username
# Replace INSTALL_PATH with full path to hunter-memory-system

# Install
sudo cp systemd/hunter-memory.service /etc/systemd/system/
sudo systemctl enable hunter-memory
sudo systemctl start hunter-memory

# Check status
sudo systemctl status hunter-memory
```

### macOS (launchd)

Create `~/Library/LaunchAgents/com.hunter.memory.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hunter.memory</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/PATH/TO/hunter-memory-system/server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/hunter-memory.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/hunter-memory.error.log</string>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.hunter.memory.plist
```

### Windows (Task Scheduler)

Create a PowerShell script `start-hunter-memory.ps1`:

```powershell
Set-Location "C:\path\to\hunter-memory-system"
python server.py
```

Then:
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Hunter Memory Server"
4. Trigger: At log on
5. Action: Start a program
6. Program: `powershell.exe`
7. Arguments: `-File "C:\path\to\start-hunter-memory.ps1"`
8. Finish

## Troubleshooting

### Port Already in Use

```bash
# Linux/Mac
lsof -i :8765
kill [PID]

# Windows
netstat -ano | findstr :8765
taskkill /PID [PID] /F
```

### Python Not Found

Make sure Python 3.12+ is installed:
```bash
python3 --version
# or on Windows:
python --version
```

### Dependencies Won't Install

Try upgrading pip first:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Plugin Not Loading

```bash
# Check if installed
openclaw plugins list

# Reinstall
openclaw plugins install -l ./openclaw-plugin

# Check config
cat ~/.openclaw/openclaw.json
```

### No Search Results

```bash
# Check database stats
curl http://127.0.0.1:8765/stats

# If total_chunks is 0, reindex
python3 cli.py index ~/.openclaw/workspace/memory
```

## Uninstall

1. Stop the server (Ctrl+C)
2. Remove plugin: `openclaw plugins uninstall hunter-memory`
3. Remove from config: Edit `~/.openclaw/openclaw.json` and remove the `plugins.slots.memory` entry
4. Restart OpenClaw: `openclaw gateway restart`
5. Delete the hunter-memory-system directory

## Next Steps

- Read [README.md](README.md) for more details
- See [SETUP-FOR-BLADE.md](SETUP-FOR-BLADE.md) for manual installation steps
- Check [PACKAGE-CONTENTS.md](PACKAGE-CONTENTS.md) to understand what's included

## Support

- Issues: https://github.com/yPhi-Box/hunter-memory-system/issues
- Discord: https://discord.com/invite/clawd
