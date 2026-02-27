#Run only when python and all libraries are installed
# Directory
Write-Host "Current Directory:"
$cwd = Get-Location
Write-Host $cwd

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
$venvPath = ".\venv\Scripts\Activate.ps1"

# Check if the file exists
if (Test-Path $venvPath) {
    Write-Host "Found virtual environment. Activating..." -ForegroundColor Green
    & $venvPath   # Run the activation script
} else {
    Write-Host "Virtual environment not found at $venvPath" -ForegroundColor Red
}
streamlit run main.py