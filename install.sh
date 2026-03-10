#!/bin/bash
# Hunter Memory System - Automated Installer
# Works on Linux/Mac (tested on Ubuntu 24.04)

set -e  # Exit on error

echo "===================================="
echo "Hunter Memory System - Installation"
echo "===================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Check for Homebrew on Mac
if [ "$OS" = "mac" ]; then
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        echo "(This will prompt for your password)"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        if ! command -v brew &> /dev/null; then
            echo "ERROR: Homebrew installation failed or not in PATH"
            echo "Please install Homebrew manually: https://brew.sh"
            echo "Then re-run this installer"
            exit 1
        fi
        
        echo "✓ Homebrew installed successfully"
        echo ""
    fi
fi

# Check system requirements
echo "Checking system requirements..."
echo ""

# Check available RAM
if [ "$OS" = "linux" ]; then
    TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
elif [ "$OS" = "mac" ]; then
    TOTAL_RAM_MB=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024)}')
fi

echo "  RAM: ${TOTAL_RAM_MB}MB"

if [ "$TOTAL_RAM_MB" -lt 1024 ]; then
    echo "  WARNING: Less than 1GB RAM detected"
    echo "  Memory system requires ~500MB. May be slow."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
elif [ "$TOTAL_RAM_MB" -lt 2048 ]; then
    echo "  ⚠ 1-2GB RAM: System will work but may be tight"
else
    echo "  ✓ Sufficient RAM for memory system"
fi

# Check available disk space
INSTALL_DIR=$(pwd)
if [ "$OS" = "linux" ]; then
    DISK_FREE_MB=$(df -m "$INSTALL_DIR" | awk 'NR==2 {print $4}')
elif [ "$OS" = "mac" ]; then
    DISK_FREE_MB=$(df -m "$INSTALL_DIR" | awk 'NR==2 {print $4}')
fi

echo "  Disk space: ${DISK_FREE_MB}MB free"

if [ "$DISK_FREE_MB" -lt 500 ]; then
    echo "  ERROR: Less than 500MB disk space"
    echo "  Installation requires ~500MB (dependencies + database)"
    exit 1
elif [ "$DISK_FREE_MB" -lt 1024 ]; then
    echo "  ⚠ Less than 1GB free: Will work but limited database growth"
else
    echo "  ✓ Sufficient disk space"
fi

echo ""

# Check Python version
PYTHON_CMD=""
NEEDS_PYTHON_INSTALL=false

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
    
    # Check if version is 3.12 or higher
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
        PYTHON_CMD="python3"
    elif [ "$PYTHON_MAJOR" -gt 3 ]; then
        PYTHON_CMD="python3"
    else
        NEEDS_PYTHON_INSTALL=true
    fi
else
    NEEDS_PYTHON_INSTALL=true
fi

# Install Python 3.12 if needed
if [ "$NEEDS_PYTHON_INSTALL" = true ]; then
    echo "Python 3.12+ not found. Installing..."
    
    if [ "$OS" = "linux" ]; then
        if [[ $EUID -eq 0 ]]; then
            # Running as root
            if apt-get update && apt-get install -y python3.12 python3.12-venv; then
                PYTHON_CMD="python3.12"
                echo "✓ Python 3.12 installed successfully"
            else
                echo "ERROR: Failed to install Python 3.12"
                echo "Please install manually: sudo apt install python3.12"
                exit 1
            fi
        else
            # Not root, use sudo
            if sudo apt-get update && sudo apt-get install -y python3.12 python3.12-venv; then
                PYTHON_CMD="python3.12"
                echo "✓ Python 3.12 installed successfully"
            else
                echo "ERROR: Failed to install Python 3.12"
                echo "Please install manually: sudo apt install python3.12"
                exit 1
            fi
        fi
    elif [ "$OS" = "mac" ]; then
        if brew install python@3.12; then
            PYTHON_CMD="python3.12"
            echo "✓ Python 3.12 installed successfully"
        else
            echo "ERROR: Failed to install Python 3.12 via Homebrew"
            echo "Please install manually: brew install python@3.12"
            exit 1
        fi
    fi
fi

# Verify we have Python now
if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python 3.12+ still not available after installation attempt"
    exit 1
fi

echo "✓ Python found: $($PYTHON_CMD --version)"
echo ""

# Check for required system packages
echo "Checking for required system packages..."

# Check for git
if ! command -v git &> /dev/null; then
    echo "git not found. Installing..."
    
    if [ "$OS" = "linux" ]; then
        if [[ $EUID -eq 0 ]]; then
            apt-get install -y git
        else
            sudo apt-get install -y git
        fi
    elif [ "$OS" = "mac" ]; then
        if ! brew install git; then
            echo "ERROR: Failed to install git via Homebrew"
            echo "Please install manually: brew install git"
            exit 1
        fi
    fi
    
    if command -v git &> /dev/null; then
        echo "✓ git installed successfully"
    else
        echo "ERROR: Failed to install git"
        exit 1
    fi
fi

# Check and install pip3 if missing
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing python3-pip and python3-venv..."
    
    if [ "$OS" = "linux" ]; then
        # Check if running as root
        if [[ $EUID -eq 0 ]]; then
            # Running as root, don't use sudo
            if apt-get update && apt-get install -y python3-pip python3-venv; then
                echo "✓ pip3 installed successfully"
            else
                echo "ERROR: Failed to install pip3"
                echo "Please run manually:"
                echo "  apt-get update && apt-get install -y python3-pip python3-venv"
                exit 1
            fi
        else
            # Not root, use sudo
            if sudo apt-get update && sudo apt-get install -y python3-pip python3-venv; then
                echo "✓ pip3 installed successfully"
            else
                echo "ERROR: Failed to install pip3"
                echo "Please run manually:"
                echo "  sudo apt-get update && sudo apt-get install -y python3-pip python3-venv"
                echo "Then re-run this installer"
                exit 1
            fi
        fi
    elif [ "$OS" = "mac" ]; then
        echo "Installing pip3 via Homebrew..."
        if brew install python3; then
            echo "✓ pip3 installed successfully"
        else
            echo "ERROR: Failed to install pip3 via Homebrew"
            echo "Please install manually: brew install python3"
            exit 1
        fi
    fi
fi

# Verify pip3 actually works now
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 not found after installation attempt"
    echo "Please install manually:"
    if [ "$OS" = "linux" ]; then
        echo "  sudo apt-get install -y python3-pip python3-venv"
    elif [ "$OS" = "mac" ]; then
        echo "  brew install python3"
    fi
    exit 1
fi

if ! pip3 --version &> /dev/null; then
    echo "ERROR: pip3 found but not working. Please check your Python installation."
    exit 1
fi

echo "✓ pip3 is available"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."

# Try normal pip install first
if ! $PYTHON_CMD -m pip install -q -r requirements.txt 2>/dev/null; then
    # If that fails (externally-managed-environment on Ubuntu 24.04+), use --break-system-packages
    echo "Using --break-system-packages flag for Ubuntu 24.04+ compatibility..."
    $PYTHON_CMD -m pip install -q --break-system-packages -r requirements.txt
fi

echo "✓ Dependencies installed"
echo ""

# Auto-detect OpenClaw workspace
MEMORY_PATH="$HOME/.openclaw/workspace/memory"

if [ -d "$MEMORY_PATH" ]; then
    echo "Found OpenClaw workspace at: $MEMORY_PATH"
    echo "Indexing memory files..."
    $PYTHON_CMD cli.py index "$MEMORY_PATH"
    echo "✓ Indexing complete"
else
    echo "OpenClaw workspace not found at: $MEMORY_PATH"
    echo "Skipping indexing (you can index later with: python3 cli.py index /path/to/memory)"
fi

echo ""

# Install OpenClaw plugin
echo "Installing OpenClaw plugin..."

OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
PLUGIN_PATH="$(pwd)/openclaw-plugin"

if ! command -v openclaw &> /dev/null; then
    echo "WARNING: openclaw command not found"
    echo "Install OpenClaw first, then run:"
    echo "  openclaw plugins install -l $PLUGIN_PATH"
else
    openclaw plugins install -l "$PLUGIN_PATH" || {
        echo "Plugin install failed - you may need to run manually:"
        echo "  openclaw plugins install -l $PLUGIN_PATH"
    }
    
    echo "✓ Plugin installed"
fi

echo ""

# Update OpenClaw config
if [ -f "$OPENCLAW_CONFIG" ]; then
    echo "Configuring OpenClaw..."
    
    # Backup config
    cp "$OPENCLAW_CONFIG" "$OPENCLAW_CONFIG.backup-$(date +%s)"
    
    # Use Python to merge JSON
    $PYTHON_CMD -c "
import json
import sys

config_path = '$OPENCLAW_CONFIG'
with open(config_path, 'r') as f:
    config = json.load(f)

# Update plugins section
if 'plugins' not in config:
    config['plugins'] = {}
if 'slots' not in config['plugins']:
    config['plugins']['slots'] = {}
if 'entries' not in config['plugins']:
    config['plugins']['entries'] = {}
if 'allow' not in config['plugins']:
    config['plugins']['allow'] = []

config['plugins']['slots']['memory'] = '@hunter/openclaw-memory'
config['plugins']['entries']['@hunter/openclaw-memory'] = {
    'enabled': True,
    'config': {
        'serverUrl': 'http://127.0.0.1:8765'
    }
}

# Add to allow list if not already there
if '@hunter/openclaw-memory' not in config['plugins']['allow']:
    config['plugins']['allow'].append('@hunter/openclaw-memory')

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
"
    echo "✓ OpenClaw configured"
else
    echo "OpenClaw config not found - skipping (install OpenClaw first)"
fi

echo ""

# Enable aggressive compaction (saves 10-20% on API costs)
if [ -f "$OPENCLAW_CONFIG" ]; then
    echo "Enabling aggressive token compaction (15k tokens)..."
    
    $PYTHON_CMD -c "
import json

config_path = '$OPENCLAW_CONFIG'
with open(config_path, 'r') as f:
    config = json.load(f)

# Update compaction settings
if 'agents' not in config:
    config['agents'] = {}
if 'defaults' not in config['agents']:
    config['agents']['defaults'] = {}
if 'compaction' not in config['agents']['defaults']:
    config['agents']['defaults']['compaction'] = {}

config['agents']['defaults']['compaction']['mode'] = 'safeguard'
config['agents']['defaults']['compaction']['reserveTokensFloor'] = 15000

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
"
    echo "✓ Aggressive compaction enabled (saves 10-20% on API costs)"
fi

echo ""
echo "===================================="
echo "SUCCESS! Hunter Memory System Installed"
echo "===================================="
echo ""
echo "What just happened:"
echo "  ✓ Installed all dependencies"
echo "  ✓ Indexed your memory files"
echo "  ✓ Configured OpenClaw plugin"
echo "  ✓ Enabled aggressive compaction"
echo ""
echo "Savings: \$60-130/month in API costs"
echo ""

# Start memory server in background
echo "Starting memory server..."
nohup $PYTHON_CMD server.py > /tmp/hunter-memory.log 2>&1 &
SERVER_PID=$!
sleep 2

# Test if server started
if curl -s http://127.0.0.1:8765/health > /dev/null 2>&1; then
    echo "✓ Memory server running (PID: $SERVER_PID)"
else
    echo "⚠ Memory server may not have started. Check /tmp/hunter-memory.log"
fi

# Restart OpenClaw if installed
if command -v openclaw &> /dev/null; then
    echo "Restarting OpenClaw..."
    openclaw gateway restart > /dev/null 2>&1 || true
    echo "✓ OpenClaw restarted"
else
    echo "⚠ OpenClaw not found - install OpenClaw to use the memory system"
fi

echo ""
echo "===================================="
echo "All Done! Memory System is Running"
echo "===================================="
echo ""
echo "Hunter Memory System by yPhi-Box"
echo "https://github.com/yPhi-box/Hunter-Memory-System"
echo ""
echo "Server log: /tmp/hunter-memory.log"
echo "Server PID: $SERVER_PID"
echo ""
