# Hunter Memory System - OpenClaw Plugin

Custom local memory system for OpenClaw with **zero API costs**. Provides hybrid semantic + keyword search using local embeddings and SQLite vector storage.

## Features

- **Zero API costs** - Local embeddings using sentence-transformers
- **Hybrid search** - Semantic similarity + keyword matching + temporal decay
- **Fast** - SQLite with vector extensions, <100ms search
- **Cross-platform** - Works on Windows, Mac, Linux
- **Auto-indexing** - File watcher for automatic updates
- **Portable** - Single SQLite database file

## Architecture

```
Memory files → Chunker → Local embeddings → SQLite + sqlite-vec → Search API → OpenClaw Plugin
```

## Installation

### 1. Install the Memory System Server

The plugin requires the memory system HTTP server to be running.

```bash
# Clone or download the memory system
cd /path/to/memory-system

# Install Python dependencies
pip install -r requirements.txt

# Index your memory files
python cli.py index /path/to/memory

# Start the server
python server.py
```

The server will run on `http://127.0.0.1:8765` by default.

### 2. Install the OpenClaw Plugin

```bash
# Install from local directory
openclaw plugins install /path/to/openclaw-plugin

# Or install from npm (when published)
openclaw plugins install @hunter/openclaw-memory
```

### 3. Configure OpenClaw

Edit your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "plugins": {
    "slots": {
      "memory": "hunter-memory"
    },
    "entries": {
      "hunter-memory": {
        "enabled": true,
        "config": {
          "serverUrl": "http://127.0.0.1:8765",
          "maxResults": 10,
          "minScore": 0.0,
          "semanticWeight": 0.6,
          "keywordWeight": 0.4
        }
      }
    }
  }
}
```

### 4. Restart OpenClaw Gateway

```bash
openclaw gateway restart
```

## Usage

The plugin provides two tools:

### memory_search

Semantically search memory files. Use this to recall past conversations, decisions, or information.

```
memory_search query="Foxx Insurance Florida"
```

Returns:
- Relevant chunks with file paths and line numbers
- Similarity scores (semantic + keyword + combined)
- Ranked by relevance

### memory_get

Retrieve specific lines from a memory file (use after memory_search).

```
memory_get path="memory/2026-03-09.md" from=100 lines=50
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `serverUrl` | `http://127.0.0.1:8765` | Memory server HTTP endpoint |
| `maxResults` | `10` | Maximum search results to return |
| `minScore` | `0.0` | Minimum similarity threshold (0-1) |
| `semanticWeight` | `0.6` | Weight for semantic search (0-1) |
| `keywordWeight` | `0.4` | Weight for keyword search (0-1) |

## Memory System Setup

### Start Server on Boot (Recommended)

**Windows (Task Scheduler):**
```powershell
# Create startup task
$action = New-ScheduledTaskAction -Execute "C:\Python312\python.exe" -Argument "C:\path\to\memory-system\server.py"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "HunterMemoryServer" -Action $action -Trigger $trigger -RunLevel Highest
```

**Linux (systemd):**
```bash
# Create service file
sudo tee /etc/systemd/system/hunter-memory.service > /dev/null <<EOF
[Unit]
Description=Hunter Memory System Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/path/to/memory-system
ExecStart=/usr/bin/python3 server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable hunter-memory
sudo systemctl start hunter-memory
```

### Auto-Index File Changes

Run the file watcher to automatically reindex when memory files change:

```bash
# Start watcher (foreground)
python cli.py watch /path/to/memory /path/to/workspace/memory

# Or run as background service (add to startup)
```

## Troubleshooting

### "Memory server unavailable"

1. Check if server is running:
   ```bash
   curl http://127.0.0.1:8765/health
   ```

2. Check server logs:
   ```bash
   # If running in terminal, check output
   # If running as service:
   # Windows: Check Task Scheduler history
   # Linux: sudo journalctl -u hunter-memory -f
   ```

3. Verify config `serverUrl` matches where server is running

### "No results found"

1. Check if memory files are indexed:
   ```bash
   python cli.py stats
   ```

2. Reindex if needed:
   ```bash
   python cli.py reindex /path/to/memory
   ```

### Plugin not loading

1. Verify installation:
   ```bash
   openclaw plugins list
   ```

2. Check OpenClaw config has correct plugin slot:
   ```json
   {
     "plugins": {
       "slots": {
         "memory": "hunter-memory"
       }
     }
   }
   ```

3. Restart gateway after config changes:
   ```bash
   openclaw gateway restart
   ```

## Performance

- **Indexing:** 2-3 seconds per file (500 chunk batches)
- **Search:** <100ms typical query
- **Storage:** ~10KB per chunk (text + embedding)
- **API costs:** $0 (local embeddings)

## Comparison to Built-in Memory

| Feature | Hunter Memory | OpenClaw Built-in |
|---------|---------------|-------------------|
| API costs | $0 | $0.013/1K tokens (OpenAI embeddings) |
| Search speed | <100ms | ~200-500ms |
| Storage | SQLite (portable) | QDrant (requires server) |
| Embeddings | Local (sentence-transformers) | OpenAI API |
| Cross-platform | Yes | Yes |
| Auto-indexing | Yes (file watcher) | Yes |
| Hybrid search | Semantic + keyword + temporal | Semantic only |

**Estimated savings:** $50-100/month for active users

## Architecture Details

### Components

- **chunker.py** - Smart text chunking with overlap (500 chars, 50 overlap)
- **embedder.py** - Local embeddings using sentence-transformers/all-MiniLM-L6-v2 (384 dims)
- **database.py** - SQLite + sqlite-vec for vector search, FTS5 for keyword search
- **search.py** - Hybrid search combining semantic + keyword + temporal decay
- **server.py** - FastAPI HTTP server
- **watcher.py** - File system watcher for auto-reindex
- **index.ts** - OpenClaw plugin (this package)

### Data Flow

1. Memory files updated → File watcher detects change
2. Watcher → Reindex file (chunk + embed + store)
3. OpenClaw calls `memory_search` → Plugin → HTTP server
4. Server → Hybrid search (semantic + keyword + temporal)
5. Results → Plugin → OpenClaw → User

## Development

### Local Development

```bash
# Clone repo
git clone https://github.com/hunter/openclaw-memory
cd openclaw-memory/openclaw-plugin

# Install plugin in dev mode (symlink)
openclaw plugins install -l .

# Make changes to index.ts
# Restart gateway to reload
openclaw gateway restart
```

### Testing

```bash
# Test memory search
openclaw plugins test hunter-memory memory_search '{"query": "test"}'

# Check plugin status
openclaw plugins info hunter-memory
```

## License

MIT

## Author

Hunter (Ben Foxx)

## Support

- Issues: https://github.com/hunter/openclaw-memory/issues
- Discord: https://discord.com/invite/clawd
