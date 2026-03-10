# Contributing to Hunter Memory System

Thank you for considering contributing! This project aims to provide a free, local memory system for OpenClaw users.

##  Goals

- Zero API costs for memory searches
- Fast, reliable search (<100ms)
- Easy to install and use
- Cross-platform compatibility
- Privacy-focused (all data local)

##  Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/yPhi-Box/hunter-memory-system.git
   cd hunter-memory-system
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
5. **Make your changes**
6. **Test thoroughly**
   ```bash
   python3 test_system.py
   ```
7. **Submit a pull request**

##  Code Style

**Python:**
- PEP 8 compliant
- Type hints where practical
- Docstrings for public functions
- Keep functions focused and small

**TypeScript (plugin):**
- Follow OpenClaw plugin conventions
- Use `type` over `interface` for consistency
- Document complex logic

**Documentation:**
- Clear, concise language
- Examples for complex features
- Update README if adding features

##  Testing

Before submitting:

1. **Run tests**
   ```bash
   python3 test_system.py
   ```

2. **Test the installer**
   ```bash
   # On a clean system or VM
   ./install.sh  # or install.ps1
   ```

3. **Test cross-platform** (if possible)
   - Windows
   - Linux
   - macOS

4. **Manual testing**
   - Index files
   - Search queries
   - Plugin integration

##  Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** (if exists)
5. **Describe your changes** clearly in the PR description
6. **Link any related issues**

##  Bug Reports

**Good bug reports include:**
- Clear description of the issue
- Steps to reproduce
- Expected behavior
- Actual behavior
- System info (OS, Python version, OpenClaw version)
- Relevant logs or error messages

**Template:**
```markdown
## Description
[Clear description of the bug]

## Steps to Reproduce
1. [First step]
2. [Second step]
3. [And so on...]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., Ubuntu 24.04]
- Python: [e.g., 3.12.3]
- OpenClaw: [e.g., 2026.3.2]

## Logs
[Paste relevant logs here]
```

##  Feature Requests

**Good feature requests include:**
- Clear use case
- Why it's valuable
- Suggested implementation (optional)
- Willingness to contribute (optional)

##  Areas for Contribution

### High Priority
- [ ] Authentication for HTTP server
- [ ] Docker container
- [ ] More comprehensive tests
- [ ] Performance benchmarks
- [ ] Memory usage optimization

### Medium Priority
- [ ] Additional embedding models
- [ ] Web UI for search
- [ ] Better hybrid scoring algorithm
- [ ] Incremental indexing (update only changed files)
- [ ] Database vacuuming/cleanup tools

### Nice to Have
- [ ] Multi-language support
- [ ] Audio/video transcription integration
- [ ] Export/import tools
- [ ] Query history and analytics
- [ ] Integration with other AI assistants

##  Resources

- **OpenClaw Docs:** https://docs.openclaw.ai
- **sentence-transformers:** https://www.sbert.net/
- **sqlite-vec:** https://github.com/asg017/sqlite-vec
- **FastAPI:** https://fastapi.tiangolo.com/

##  Questions?

- Open a [GitHub Discussion](https://github.com/yPhi-Box/hunter-memory-system/discussions)
- Ask in [OpenClaw Discord](https://discord.com/invite/clawd)
- Check existing issues/PRs

##  Code of Conduct

- Be respectful and constructive
- Focus on what's best for the project
- Welcome newcomers
- Assume good intentions
- Help others learn

##  Thank You!

Every contribution makes this project better for the OpenClaw community.


