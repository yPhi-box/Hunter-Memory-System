# Hunter Memory System for OpenClaw

Zero-cost local memory system for OpenClaw with hybrid semantic + keyword search.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw Plugin](https://img.shields.io/badge/openclaw-plugin-green.svg)](https://openclaw.com)

## What This Does

Replaces OpenClaw's built-in memory system with a local, zero-cost alternative using sentence-transformers and SQLite vector search.

**Benefits:**
- Save $50-100/month - Zero API costs for memory searches
- Faster searches - Under 100ms vs 200-500ms
- Private - All data stays local
- Cross-platform - Works on Windows, Linux, Mac
- Offline - No internet required after setup

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yPhi-Box/hunter-memory-system.git
cd hunter-memory-system

# Run the installer
./install.sh  # Linux/Mac
.\install.ps1  # Windows
```

The installer handles everything: checks system requirements, installs dependencies, indexes your memory files, configures OpenClaw, and sets up auto-start. Takes about 5 minutes.

## Requirements

**Minimum:**
- Python 3.12+
- 1GB RAM (2GB+ recommended)
- 500MB disk space
- OpenClaw 2026.2.0+

**Tested on:**
- Windows 11
- Ubuntu 24.04
- macOS (should work, not tested)

## How It Works

```
Memory files -> Chunker (500 chars) -> Local Embeddings (sentence-transformers)
                                              |
                                         SQLite DB
                                    /                \
                        Vector Search            FTS5 (keyword)
                                    \                /
                                      Hybrid Scorer
                                            |
                                    Ranked Results
```

**Components:**
- **Chunker** - Smart text splitting with overlap
- **Embedder** - Local embeddings (all-MiniLM-L6-v2, 384 dims)
- **Database** - SQLite + sqlite-vec + FTS5
- **Search** - Hybrid semantic + keyword + temporal decay
- **Server** - FastAPI HTTP API
- **Plugin** - OpenClaw TypeScript integration

## Cost Savings

| Setting | Savings/Month | How |
|---------|---------------|-----|
| Memory Plugin | $50-100 | Zero API costs for embeddings |
| Aggressive Compaction | $10-30 | Fewer tokens per session |
| **Total** | **$60-130** | Combined effect |

*Aggressive compaction is optional - installer will ask if you want to enable it.*

## Usage

Once installed, use it naturally in OpenClaw:

```
You: "What do you remember about [topic]?"
OpenClaw: [searches memory and returns results]
```

Or test the API directly:

```bash
# Start the server
python3 server.py

# Check health
curl http://127.0.0.1:8765/health

# Search
curl -X POST http://127.0.0.1:8765/search \
  -H "Content-Type: application/json" \
  -d '{"query": "topic you want to recall", "max_results": 5}'
```

## Documentation

- [Quick Start Guide](QUICK-START.md) - 5-minute setup (read this first)
- [Setup Guide](SETUP-FOR-BLADE.md) - Detailed manual installation
- [Package Contents](PACKAGE-CONTENTS.md) - What's included
- [Plugin README](openclaw-plugin/README.md) - OpenClaw plugin docs
- [Diagnostic Report](DIAGNOSTIC-REPORT.md) - Test results

## Manual Installation

If you prefer manual setup:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Index memory files
python3 cli.py index ~/.openclaw/workspace/memory

# 3. Start server
python3 server.py

# 4. Install plugin
openclaw plugins install -l ./openclaw-plugin

# 5. Configure OpenClaw (edit ~/.openclaw/openclaw.json)
{
  "plugins": {
    "slots": {
      "memory": "hunter-memory"
    }
  }
}

# 6. Restart OpenClaw
openclaw gateway restart
```

## Auto-Start Setup

**Linux (systemd):**
```bash
sudo cp systemd/hunter-memory.service /etc/systemd/system/
# Edit file: replace USERNAME and INSTALL_PATH
sudo systemctl enable hunter-memory
sudo systemctl start hunter-memory
```

**macOS / Windows:** See [QUICK-START.md](QUICK-START.md) for platform-specific instructions.

## CLI Tools

```bash
# Index files
python3 cli.py index /path/to/memory

# Search from command line
python3 cli.py search "your query" 5

# View stats
python3 cli.py stats

# Watch for changes (auto-reindex)
python3 cli.py watch /path/to/memory
```

## Troubleshooting

**Server won't start:**
```bash
python3 --version  # Need 3.12+
pip install -r requirements.txt
lsof -i :8765  # Check if port is in use
```

**Plugin not loading:**
```bash
openclaw plugins list | grep hunter-memory
openclaw plugins install -l ./openclaw-plugin
cat ~/.openclaw/openclaw.json | grep -A 5 "slots"
openclaw gateway restart
```

**No search results:**
```bash
curl http://127.0.0.1:8765/stats
# If total_chunks is 0:
python3 cli.py index /path/to/memory
```

## Contributing

Contributions welcome. Areas for improvement:

- Add more embedding models
- Improve hybrid search scoring
- Add web UI for search
- Add authentication to server
- Create Docker container
- Add more tests

**To contribute:**
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Credits

Built by Hunter (Ben Foxx) for the OpenClaw community.

**Powered by:**
- [sentence-transformers](https://www.sbert.net/) - Local embeddings
- [sqlite-vec](https://github.com/asg017/sqlite-vec) - Vector search
- [FastAPI](https://fastapi.tiangolo.com/) - HTTP server
- [OpenClaw](https://openclaw.com) - AI assistant platform

## Support

- Issues: [GitHub Issues](https://github.com/yPhi-Box/hunter-memory-system/issues)
- Discussions: [GitHub Discussions](https://github.com/yPhi-Box/hunter-memory-system/discussions)
- Community: [OpenClaw Discord](https://discord.com/invite/clawd)

---

Made for the OpenClaw community.
