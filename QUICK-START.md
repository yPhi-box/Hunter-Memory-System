# Hunter Memory System - Quick Start

## What You Get

✅ **Zero API costs** for memory searches (saves $50-100/month)
✅ **Fast search** (<100ms vs 200-500ms)
✅ **Optional token savings** (10-20% extra with aggressive compaction)
✅ **Works offline** (no external APIs)

## System Requirements

**Minimum:**
- 1GB RAM (2GB+ recommended)
- 500MB disk space
- Python 3.12+
- OpenClaw installed

**Performance tested on:**
- Windows 11 (2 CPU, 12GB RAM) ✓
- Ubuntu 24.04 (1 CPU, 2GB RAM) ✓
- Expected to work on Mac (not tested)

## Installation (One Command)

### Linux/Mac
```bash
cd hunter-memory-system
chmod +x install.sh
./install.sh
```

### Windows
```powershell
cd hunter-memory-system
.\install.ps1
```

The installer will:
1. Check system requirements
2. Install Python dependencies (~200MB download)
3. Index your memory files
4. Install OpenClaw plugin
5. Update config automatically
6. **Ask if you want aggressive compaction** (recommended: yes)

**Total time: 5-10 minutes** (mostly pip downloads)

## What the Installer Asks You

### 1. Memory Path
**Question:** "Enter path to OpenClaw workspace memory directory"

**Answer:** 
- Linux/Mac: `~/.openclaw/workspace/memory`
- Windows: `C:\Users\YourName\.openclaw\workspace\memory`

### 2. Update Config Automatically?
**Question:** "Automatically update config? (y/n)"

**Recommend:** Yes (y)

**What it does:** Adds this to your `openclaw.json`:
```json
{
  "plugins": {
    "slots": {
      "memory": "hunter-memory"
    }
  }
}
```

### 3. Enable Aggressive Compaction?
**Question:** "Enable aggressive compaction (15k tokens)? (y/n)"

**Recommend:** Yes (y)

**What it does:**
- Changes `reserveTokensFloor` from 35,000 → 15,000 tokens
- Saves 10-20% on Claude API costs
- Requires memory server to be running
- Can revert anytime (backup is created)

**Why it's safe:**
With the memory system, you don't need huge context buffers. The system recalls information instantly from the database instead.

**If your memory server goes down:** OpenClaw will still work, just without memory search. Revert to 35k tokens if you want larger buffer without memory system.

## After Installation

### Start the Server
```bash
# Linux/Mac
python3 server.py

# Windows
python server.py
```

**Keep this running.** You can:
- Run in `tmux`/`screen`
- Set up as systemd service (Linux)
- Set up as Task Scheduler task (Windows)

### Restart OpenClaw
```bash
openclaw gateway restart
```

### Test It Works
```bash
# Check server
curl http://127.0.0.1:8765/health

# Check plugin
openclaw plugins list | grep hunter-memory

# Try it in chat
# Ask OpenClaw: "Search my memory for [topic]"
```

## What Gets Changed

### Always Changed
- `plugins.slots.memory = "hunter-memory"` → Uses local memory instead of OpenAI

### Optionally Changed (if you say yes)
- `agents.defaults.compaction.reserveTokensFloor = 15000` → More aggressive compaction

### Never Changed
- Your model settings
- Your auth tokens
- Your memory files (only indexed, not modified)
- Any other OpenClaw settings

## Cost Savings Breakdown

| Setting | Monthly Savings | How |
|---------|----------------|-----|
| Memory plugin | $50-100 | Zero API costs for memory searches |
| Aggressive compaction | $10-30 | Fewer tokens per session |
| **Total** | **$60-130** | Combined effect |

**Break-even:** Immediate (costs $0 to run)

## Reverting Changes

### Remove Memory Plugin
Edit `openclaw.json`:
```json
{
  "plugins": {
    "slots": {
      "memory": "memory-core"  // Back to built-in
    }
  }
}
```

### Restore Original Compaction
The installer creates backups:
```bash
# Find backup
ls ~/.openclaw/openclaw.json.backup-*

# Restore it
cp ~/.openclaw/openclaw.json.backup-TIMESTAMP ~/.openclaw/openclaw.json
```

Or manually edit `openclaw.json`:
```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "reserveTokensFloor": 35000  // Back to default
      }
    }
  }
}
```

## Troubleshooting

### "Memory server unavailable"
1. Check if server is running: `curl http://127.0.0.1:8765/health`
2. Start it: `python3 server.py`

### "Plugin not loaded"
1. Check: `openclaw plugins list | grep hunter`
2. If missing: `openclaw plugins install -l /path/to/openclaw-plugin`
3. Restart: `openclaw gateway restart`

### "No results found"
1. Check indexing: `curl http://127.0.0.1:8765/stats`
2. If `total_chunks` is 0: `python3 cli.py index /path/to/memory`

### Server won't start
1. Check Python: `python3 --version` (need 3.12+)
2. Check dependencies: `pip install -r requirements.txt`
3. Check port: `lsof -i :8765` (kill if occupied)

## Next Steps

### Auto-Start Server (Recommended)

**Linux (systemd):**
```bash
sudo cp systemd/hunter-memory.service /etc/systemd/system/
# Edit file: replace USERNAME and INSTALL_PATH
sudo systemctl enable hunter-memory
sudo systemctl start hunter-memory
```

**Windows (Task Scheduler):**
See README.md for PowerShell script

**Mac (launchd):**
See README.md for plist file

### File Watcher (Optional)
Auto-reindex when memory files change:
```bash
python3 cli.py watch ~/.openclaw/workspace/memory
```

## Support

**Questions?** Check:
1. README.md (full documentation)
2. DIAGNOSTIC-REPORT.md (test results)
3. SETUP-FOR-BLADE.md (detailed setup guide)

**Issues?** 
- Check server logs (terminal where server.py runs)
- Check OpenClaw logs: `openclaw status`
