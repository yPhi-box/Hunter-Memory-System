# Hunter Memory System - Automated Installer for Windows
# PowerShell version

$ErrorActionPreference = "Stop"

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Hunter Memory System - Installation" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check system requirements
Write-Host "Checking system requirements..." -ForegroundColor Yellow
Write-Host ""

# Check RAM
$totalRAM = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1MB)
Write-Host "  RAM: ${totalRAM}MB"

if ($totalRAM -lt 1024) {
    Write-Host "  WARNING: Less than 1GB RAM detected" -ForegroundColor Red
    Write-Host "  Memory system requires ~500MB. May be slow." -ForegroundColor Red
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") { exit 1 }
} elseif ($totalRAM -lt 2048) {
    Write-Host "  ⚠ 1-2GB RAM: System will work but may be tight" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Sufficient RAM for memory system" -ForegroundColor Green
}

# Check disk space
$drive = (Get-Location).Drive.Name + ":"
$diskFree = [math]::Round((Get-PSDrive $drive).Free / 1MB)
Write-Host "  Disk space: ${diskFree}MB free"

if ($diskFree -lt 500) {
    Write-Host "  ERROR: Less than 500MB disk space" -ForegroundColor Red
    Write-Host "  Installation requires ~500MB (dependencies + database)" -ForegroundColor Red
    exit 1
} elseif ($diskFree -lt 1024) {
    Write-Host "  ⚠ Less than 1GB free: Will work but limited database growth" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Sufficient disk space" -ForegroundColor Green
}

Write-Host ""

# Check Python
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1 | Out-String
        if ($version -match "Python 3\.1[2-9]" -or $version -match "Python 3\.[2-9][0-9]") {
            $pythonCmd = $cmd
            Write-Host "✓ Python found: $version" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "ERROR: Python 3.12+ required but not found" -ForegroundColor Red
    Write-Host "Install from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check for pip
Write-Host "Checking for pip..." -ForegroundColor Yellow

try {
    & $pythonCmd -m pip --version 2>&1 | Out-Null
    Write-Host "✓ pip is available" -ForegroundColor Green
} catch {
    Write-Host "ERROR: pip not found. Installing pip..." -ForegroundColor Red
    try {
        & $pythonCmd -m ensurepip --upgrade
        Write-Host "✓ pip installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install pip. Please install manually:" -ForegroundColor Red
        Write-Host "  python -m ensurepip --upgrade" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& $pythonCmd -m pip install -q -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Prompt for memory paths
Write-Host "Enter path to OpenClaw workspace memory directory:" -ForegroundColor Cyan
Write-Host "(Example: C:\Users\YourName\.openclaw\workspace\memory)" -ForegroundColor Gray
$memoryPath = Read-Host

if (-not (Test-Path $memoryPath)) {
    Write-Host "WARNING: Directory not found: $memoryPath" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") { exit 1 }
}

# Index memory files
if (Test-Path $memoryPath) {
    Write-Host ""
    Write-Host "Indexing memory files..." -ForegroundColor Yellow
    & $pythonCmd cli.py index $memoryPath
    Write-Host "✓ Indexing complete" -ForegroundColor Green
} else {
    Write-Host "Skipping indexing (directory not found)" -ForegroundColor Yellow
}

Write-Host ""

# Install OpenClaw plugin
Write-Host "Installing OpenClaw plugin..." -ForegroundColor Yellow

$pluginPath = Join-Path (Get-Location) "openclaw-plugin"
$openclawConfig = Join-Path $env:USERPROFILE ".openclaw\openclaw.json"

try {
    openclaw plugins install -l $pluginPath
    Write-Host "✓ Plugin installed" -ForegroundColor Green
} catch {
    Write-Host "WARNING: openclaw command not found or plugin install failed" -ForegroundColor Yellow
    Write-Host "Install OpenClaw first, then run:" -ForegroundColor Yellow
    Write-Host "  openclaw plugins install -l $pluginPath" -ForegroundColor Gray
}

Write-Host ""

# Update OpenClaw config
if (Test-Path $openclawConfig) {
    Write-Host "OpenClaw config found at: $openclawConfig" -ForegroundColor Green
    Write-Host ""
    Write-Host "Add this to your config (if not already present):" -ForegroundColor Cyan
    Write-Host ""
    Write-Host @"
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
"@ -ForegroundColor Gray
    Write-Host ""
    $update = Read-Host "Automatically update config? (y/n)"
    
    if ($update -eq "y") {
        # Backup config
        $backupPath = "$openclawConfig.backup-$(Get-Date -Format 'yyyyMMddHHmmss')"
        Copy-Item $openclawConfig $backupPath
        
        # Update config
        $config = Get-Content $openclawConfig | ConvertFrom-Json
        
        if (-not $config.plugins) { $config | Add-Member -NotePropertyName plugins -NotePropertyValue @{} }
        if (-not $config.plugins.slots) { $config.plugins | Add-Member -NotePropertyName slots -NotePropertyValue @{} }
        if (-not $config.plugins.entries) { $config.plugins | Add-Member -NotePropertyName entries -NotePropertyValue @{} }
        
        $config.plugins.slots.memory = "hunter-memory"
        $config.plugins.entries."hunter-memory" = @{
            enabled = $true
            config = @{
                serverUrl = "http://127.0.0.1:8765"
            }
        }
        
        $config | ConvertTo-Json -Depth 10 | Set-Content $openclawConfig
        Write-Host "✓ Config updated" -ForegroundColor Green
    }
} else {
    Write-Host "OpenClaw config not found at: $openclawConfig" -ForegroundColor Yellow
    Write-Host "You'll need to configure manually after installing OpenClaw" -ForegroundColor Yellow
}

Write-Host ""

# Optional: Aggressive Compaction
if (Test-Path $openclawConfig) {
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host "Optional: Aggressive Token Savings" -ForegroundColor Cyan
    Write-Host "====================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "With local memory search, you can safely reduce OpenClaw's"
    Write-Host "context buffer (reserveTokensFloor) for additional savings."
    Write-Host ""
    Write-Host "Current setting: 35,000 tokens (default)"
    Write-Host "Recommended: 15,000 tokens (with memory system)"
    Write-Host ""
    Write-Host "Benefits:" -ForegroundColor Green
    Write-Host "  - Save 10-20% on Claude API costs"
    Write-Host "  - Faster compaction = snappier responses"
    Write-Host "  - Memory system handles recall instantly"
    Write-Host ""
    Write-Host "Requirements:" -ForegroundColor Yellow
    Write-Host "  - Memory server must be running"
    Write-Host "  - Memory files indexed and accessible"
    Write-Host ""
    $compaction = Read-Host "Enable aggressive compaction (15k tokens)? (y/n)"
    
    if ($compaction -eq "y") {
        $backupPath = "$openclawConfig.backup-compaction-$(Get-Date -Format 'yyyyMMddHHmmss')"
        Copy-Item $openclawConfig $backupPath
        
        $config = Get-Content $openclawConfig | ConvertFrom-Json
        
        if (-not $config.agents) { $config | Add-Member -NotePropertyName agents -NotePropertyValue @{} }
        if (-not $config.agents.defaults) { $config.agents | Add-Member -NotePropertyName defaults -NotePropertyValue @{} }
        if (-not $config.agents.defaults.compaction) { $config.agents.defaults | Add-Member -NotePropertyName compaction -NotePropertyValue @{} }
        
        $config.agents.defaults.compaction.mode = "safeguard"
        $config.agents.defaults.compaction.reserveTokensFloor = 15000
        
        $config | ConvertTo-Json -Depth 10 | Set-Content $openclawConfig
        Write-Host "✓ Compaction updated to 15,000 tokens" -ForegroundColor Green
        Write-Host ""
        Write-Host "NOTE: You can revert by restoring the backup:" -ForegroundColor Gray
        Write-Host "  Copy-Item $backupPath $openclawConfig" -ForegroundColor Gray
    } else {
        Write-Host "Skipped - keeping default 35,000 tokens" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "You can change this later in openclaw.json:" -ForegroundColor Gray
        Write-Host "  agents.defaults.compaction.reserveTokensFloor: 15000" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Start the memory server:" -ForegroundColor White
Write-Host "   $pythonCmd server.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Restart OpenClaw gateway:" -ForegroundColor White
Write-Host "   openclaw gateway restart" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Test the system:" -ForegroundColor White
Write-Host "   Invoke-WebRequest http://127.0.0.1:8765/health" -ForegroundColor Gray
Write-Host ""
Write-Host "Optional: Set up auto-start (Task Scheduler):" -ForegroundColor White
Write-Host "   See README.md for instructions" -ForegroundColor Gray
Write-Host ""
