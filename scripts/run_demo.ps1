# PowerShell helper to run the demo and open the generated report
# Usage: run from repository root

$env:PYTHONPATH = (Get-Location).Path
python demo_presentation_clean.py
if (Test-Path demo_report.md) {
    Start-Process -FilePath demo_report.md
} else {
    Write-Host "demo_report.md not found"
}
