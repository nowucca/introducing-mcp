# PowerShell script to run the SDK implementation
$env:IMPLEMENTATION = "sdk"
& "$PSScriptRoot/docker-run.ps1"
