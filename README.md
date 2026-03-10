# Hunter Memory System for OpenClaw

> Zero-cost local memory system for OpenClaw with hybrid semantic + keyword search

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw Plugin](https://img.shields.io/badge/openclaw-plugin-green.svg)](https://openclaw.com)

## ðŸŽ¯ What This Does

Replaces OpenClaw's built-in memory system with a **local, zero-cost alternative** using sentence-transformers and SQLite vector search.

**Benefits:**
- ðŸ’° **Save $50-100/month** - Zero API costs for memory searches
- âš¡ **Faster searches** - <100ms vs 200-500ms
- ðŸ”’ **Private** - All data stays local
- ðŸŒ **Cross-platform** - Works on Windows, Linux, Mac
- ðŸ“´ **Offline** - No internet required after setup

## ðŸš€ Quick Start

```bash
# Clone the repository
git clone https://github.com/yPhi-Box/hunter-memory-system.git
cd hunter-memory-system

# Run the installer
./install.sh  # Linux/Mac
# or
.\install.ps1  # Windows

# Follow the prompts (takes 5 minutes)
```

**That's it!** The installer handles everything:
- âœ… Checks system requirements
- âœ… Installs dependencies
- âœ… Indexes your memory files
- âœ… Configures OpenClaw
- âœ… Sets up auto-start (optional)

## ðŸ“‹ Requirements

**Minimum:**
- Python 3.12+
- 1GB RAM (2GB+ recommended)
- 500MB disk space
- OpenClaw 2026.2.0+

**Tested on:**
- âœ… Windows 11
- âœ… Ubuntu 24.04
- âš ï¸ macOS (should work, not tested)

## ðŸŽ¬ Demo

```bash
# Start the server
python3 server.py

# Test it
curl http://127.0.0.1:8765/health
# {"status":"ok"}

# Search your memory
curl -X POST http://127.0.0.1:8765/search \
  -H "Content-Type: application/json" \
  -d '{"query": "topic you want to recall", "max_results": 5}'
```

Or use it naturally in OpenClaw:
```
You: "What do you remember about [topic]?"
OpenClaw: [searches memory and returns results]
```

## ðŸ“Š Cost Savings

| Setting | Savings/Month | How |
|---------|---------------|-----|
| Memory Plugin | $50-100 | Zero API costs for embeddings |
| Aggressive Compaction* | $10-30 | Fewer tokens per session |
| **Total** | **$60-130** | Combined effect |

\* Optional setting the installer can configure (recommended: yes)

## ðŸ—ï¸ Architecture

```
Memory files â†’ Chunker (500 chars) â†’ Local Embeddings (sentence-transformers)
                                              â†“
                                         SQLite DB
                                      â†™ï¸         â†˜ï¸
                              Vector Search    FTS5 (keyword)
                                      â†˜ï¸         â†™ï¸
                                    Hybrid Scorer
                                          â†“
                                 Ranked Results
```

**Components:**
- **Chunker** - Smart text splitting with overlap
- **Embedder** - Local embeddings (all-MiniLM-L6-v2, 384 dims)
- **Database** - SQLite + sqlite-vec + FTS5
- **Search** - Hybrid semantic + keyword + temporal decay
- **Server** - FastAPI HTTP API
- **Plugin** - OpenClaw TypeScript integration

## ðŸ“– Documentation

- **[Quick Start Guide](QUICK-START.md)** - 5-minute setup (read this first)
- **[Setup Guide](SETUP-FOR-BLADE.md)** - Detailed manual installation
- **[Package Contents](PACKAGE-CONTENTS.md)** - What's included
- **[Plugin README](openclaw-plugin/README.md)** - OpenClaw plugin docs
- **[Diagnostic Report](DIAGNOSTIC-REPORT.md)** - Test results

## ðŸ”§ Manual Installation

If you prefer manual setup over the installer:

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Index your memory files
python3 cli.py index ~/.openclaw/workspace/memory

# 3. Start the server
python3 server.py  # Keep this running

# 4. Install OpenClaw plugin
openclaw plugins install -l ./openclaw-plugin

# 5. Configure OpenClaw
# Edit ~/.openclaw/openclaw.json and add:
# {
#   "plugins": {
#     "slots": {
#       "memory": "hunter-memory"
#     }
#   }
# }

# 6. Restart OpenClaw
openclaw gateway restart
```

## ðŸ”„ Auto-Start Setup

### Linux (systemd)
```bash
sudo cp systemd/hunter-memory.service /etc/systemd/system/
# Edit file: replace USERNAME and INSTALL_PATH
sudo systemctl enable hunter-memory
sudo systemctl start hunter-memory
```

### macOS (launchd)
See [QUICK-START.md](QUICK-START.md) for launchd plist example

### Windows (Task Scheduler)
See [QUICK-START.md](QUICK-START.md) for PowerShell script

## ðŸ§ª Testing

```bash
# Run local tests
python3 test_system.py

# Test from remote machine
python3 test_remote.py  # Edit SERVER_URL first
```

## ðŸ› ï¸ CLI Tools

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

## ðŸ› Troubleshooting

### Server won't start
```bash
# Check Python version
python3 --version  # Need 3.12+

# Reinstall dependencies
pip install -r requirements.txt

# Check if port is in use
lsof -i :8765
```

### Plugin not loading
```bash
# Check plugin status
openclaw plugins list | grep hunter-memory

# Reinstall plugin
openclaw plugins install -l ./openclaw-plugin

# Check config
cat ~/.openclaw/openclaw.json | grep -A 5 "slots"

# Restart gateway
openclaw gateway restart
```

### No search results
```bash
# Check if database is populated
curl http://127.0.0.1:8765/stats

# If total_chunks is 0, reindex
python3 cli.py index /path/to/memory
```

## ðŸ¤ Contributing

Contributions welcome! This is a working system but there's always room for improvement.

**Areas for contribution:**
- [ ] Add more embedding models
- [ ] Improve hybrid search scoring
- [ ] Add web UI for search
- [ ] Add authentication to server
- [ ] Create Docker container
- [ ] Add more tests
- [ ] Improve documentation

**To contribute:**
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## ðŸ“„ License

MIT License - See [LICENSE](LICENSE) file for details

## ðŸ™ Credits

Built by Hunter (Ben Foxx) for the OpenClaw community.

Powered by:
- [sentence-transformers](https://www.sbert.net/) - Local embeddings
- [sqlite-vec](https://github.com/asg017/sqlite-vec) - Vector search
- [FastAPI](https://fastapi.tiangolo.com/) - HTTP server
- [OpenClaw](https://openclaw.com) - AI assistant platform

## ðŸ“ž Support

- **Issues:** [GitHub Issues](https://github.com/yPhi-Box/hunter-memory-system/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yPhi-Box/hunter-memory-system/discussions)
- **Community:** [OpenClaw Discord](https://discord.com/invite/clawd)

## â­ Star History

If this saves you money, consider giving it a star! â­

---

**Made with â¤ï¸ for the OpenClaw community**

