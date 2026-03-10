# PowerShell wrapper for memory search
# Usage: .\search.ps1 "query here" [limit]

param(
    [Parameter(Mandatory=$true)]
    [string]$Query,
    
    [Parameter(Mandatory=$false)]
    [int]$Limit = 10
)

$pythonPath = "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"
$scriptPath = Join-Path $PSScriptRoot "search_cli.py"

& $pythonPath $scriptPath $Query $Limit 2>$null
