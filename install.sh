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
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if (( $(echo "$PYTHON_VERSION >= 3.12" | bc -l) )); then
        PYTHON_CMD="python3"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: Python 3.12+ required but not found"
    echo "Install: sudo apt install python3.12 python3-pip"
    exit 1
fi

echo "✓ Python found: $($PYTHON_CMD --version)"
echo ""

# Check for required system packages
echo "Checking for required system packages..."

# Check and install pip3 if missing
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing python3-pip and python3-venv..."
    
    if [ "$OS" = "linux" ]; then
        # Try to install with sudo
        if sudo -n true 2>/dev/null; then
            # Passwordless sudo is available
            if sudo apt-get update -qq && sudo apt-get install -y python3-pip python3-venv; then
                echo "✓ pip3 installed successfully"
            else
                echo "ERROR: Failed to install pip3 with sudo"
                echo "Please run manually:"
                echo "  sudo apt-get update && sudo apt-get install -y python3-pip python3-venv"
                echo "Then re-run this installer"
                exit 1
            fi
        else
            # sudo requires password
            echo ""
            echo "sudo password required to install pip3..."
            if sudo apt-get update && sudo apt-get install -y python3-pip python3-venv; then
                echo "✓ pip3 installed successfully"
            else
                echo "ERROR: Failed to install pip3. Please run manually:"
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
$PYTHON_CMD -m pip install -q -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Prompt for memory paths
echo "Enter path to OpenClaw workspace memory directory:"
echo "(Example: ~/.openclaw/workspace/memory)"
read -r MEMORY_PATH

if [ ! -d "$MEMORY_PATH" ]; then
    echo "WARNING: Directory not found: $MEMORY_PATH"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Index memory files
if [ -d "$MEMORY_PATH" ]; then
    echo ""
    echo "Indexing memory files..."
    $PYTHON_CMD cli.py index "$MEMORY_PATH"
    echo "✓ Indexing complete"
else
    echo "Skipping indexing (directory not found)"
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
    echo "OpenClaw config found at: $OPENCLAW_CONFIG"
    echo ""
    echo "Add this to your config (if not already present):"
    echo ""
    cat <<'EOF'
{
  "plugins": {
    "slots": {
      "memory": "hunter-memory"
    },
    "entries": {
      "hunter-memory": {
        "enabled": true,
        "config": {
          "serverUrl": "http://127.0.0.1:8765"
        }
      }
    }
  }
}
EOF
    echo ""
    read -p "Automatically update config? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
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

config['plugins']['slots']['memory'] = 'hunter-memory'
config['plugins']['entries']['hunter-memory'] = {
    'enabled': True,
    'config': {
        'serverUrl': 'http://127.0.0.1:8765'
    }
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print('✓ Config updated')
"
    fi
else
    echo "OpenClaw config not found at: $OPENCLAW_CONFIG"
    echo "You'll need to configure manually after installing OpenClaw"
fi

echo ""

# Optional: Aggressive Compaction
if [ -f "$OPENCLAW_CONFIG" ]; then
    echo "===================================="
    echo "Optional: Aggressive Token Savings"
    echo "===================================="
    echo ""
    echo "With local memory search, you can safely reduce OpenClaw's"
    echo "context buffer (reserveTokensFloor) for additional savings."
    echo ""
    echo "Current setting: 35,000 tokens (default)"
    echo "Recommended: 15,000 tokens (with memory system)"
    echo ""
    echo "Benefits:"
    echo "  - Save 10-20% on Claude API costs"
    echo "  - Faster compaction = snappier responses"
    echo "  - Memory system handles recall instantly"
    echo ""
    echo "Requirements:"
    echo "  - Memory server must be running"
    echo "  - Memory files indexed and accessible"
    echo ""
    read -p "Enable aggressive compaction (15k tokens)? (y/n) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$OPENCLAW_CONFIG" "$OPENCLAW_CONFIG.backup-compaction-$(date +%s)"
        
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

print('✓ Compaction updated to 15,000 tokens')
"
        echo ""
        echo "NOTE: You can revert by restoring the backup:"
        echo "  cp $OPENCLAW_CONFIG.backup-compaction-* $OPENCLAW_CONFIG"
    else
        echo "Skipped - keeping default 35,000 tokens"
        echo ""
        echo "You can change this later in openclaw.json:"
        echo "  agents.defaults.compaction.reserveTokensFloor: 15000"
    fi
fi

echo ""
echo "===================================="
echo "Installation Complete!"
echo "===================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start the memory server:"
echo "   $PYTHON_CMD server.py"
echo ""
echo "2. Restart OpenClaw gateway:"
echo "   openclaw gateway restart"
echo ""
echo "3. Test the system:"
echo "   curl http://127.0.0.1:8765/health"
echo ""
echo "Optional: Set up auto-start (systemd):"
echo "   sudo cp systemd/hunter-memory.service /etc/systemd/system/"
echo "   sudo systemctl enable hunter-memory"
echo "   sudo systemctl start hunter-memory"
echo ""
