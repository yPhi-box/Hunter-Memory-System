# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-09

### Added
- Initial release
- Local memory system using sentence-transformers + SQLite
- Hybrid semantic + keyword + temporal search
- Zero API costs for memory searches
- FastAPI HTTP server
- OpenClaw plugin integration
- Automated installers for Linux/Mac/Windows
- File watcher for auto-reindex
- CLI tools for indexing and search
- Optional aggressive compaction setting (saves 10-20% on API costs)
- Cross-platform support (Windows, Linux, Mac)
- Comprehensive documentation

### Features
- 13,615+ chunks indexed in test environment
- <100ms search response time
- ~500MB RAM usage
- Single SQLite database file (portable)
- Automatic backups during config changes
- System requirements checker in installer

### Tested On
- Windows 11 (2 CPU, 12GB RAM) ✓
- Ubuntu 24.04 (1 CPU, 2GB RAM) ✓

[1.0.0]: https://github.com/yourusername/hunter-memory-system/releases/tag/v1.0.0
