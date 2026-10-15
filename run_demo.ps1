$ErrorActionPreference = 'Stop'

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Error 'Install Ollama from https://ollama.com/download, then reopen PowerShell and run this script again.'
    exit 1
}

py -m pip install -e '.[agent]'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

ollama pull qwen3:1.7b
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

py app.py
