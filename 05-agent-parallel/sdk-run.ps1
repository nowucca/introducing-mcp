Write-Host "Running MCP example with SDK..."
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
python -m mcp.cli run --stdio --command "python client/client.py" server/server.py
