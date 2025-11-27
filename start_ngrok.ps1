# Start ngrok tunnel for Arabic Writer app

Write-Host "Starting ngrok tunnel on port 5000..." -ForegroundColor Green

# Check if ngrok is installed
if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: ngrok is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Download from: https://ngrok.com/download" -ForegroundColor Yellow
    exit 1
}

# Load environment variables
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.+)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim("'`"")
            [Environment]::SetEnvironmentVariable($name, $value, 'Process')
        }
    }
}

# Configure ngrok with authtoken
$authtoken = $env:NGROK_AUTHTOKEN
if ($authtoken -and $authtoken -ne '364EL8m5URpqG3IPmJskCUSl4o1_YzWAEr4sbXZ2bRZeqZvQ') {
    Write-Host "Configuring ngrok with authtoken..." -ForegroundColor Cyan
    ngrok config add-authtoken $authtoken
} else {
    Write-Host "WARNING: NGROK_AUTHTOKEN not set in .env file" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Your ngrok URL: https://colt-water-podgily.ngrok-free.dev" -ForegroundColor Green
Write-Host "Update Auth0 with these URLs:" -ForegroundColor Cyan
Write-Host "  - Allowed Callback URLs: https://colt-water-podgily.ngrok-free.dev/callback" -ForegroundColor Yellow
Write-Host "  - Allowed Logout URLs: https://colt-water-podgily.ngrok-free.dev" -ForegroundColor Yellow
Write-Host "  - Allowed Web Origins: https://colt-water-podgily.ngrok-free.dev" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start ngrok with your static domain
ngrok http --url=colt-water-podgily.ngrok-free.dev 5000
