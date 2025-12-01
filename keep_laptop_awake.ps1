# Keep laptop awake during PAQ8px compression
# Prevents sleep, hibernation, display off during long test

Write-Host "🔌 CONFIGURING LAPTOP TO STAY AWAKE" -ForegroundColor Cyan
Write-Host ""

# Save current power settings
Write-Host "💾 Saving current power settings..."
$currentPlan = powercfg /getactivescheme
Write-Host "Current plan: $currentPlan"
Write-Host ""

# Set to never sleep while plugged in
Write-Host "⚙️ Setting power options for long compression test..."

# AC (plugged in) settings
powercfg /change monitor-timeout-ac 0      # Never turn off display
powercfg /change disk-timeout-ac 0         # Never turn off disk
powercfg /change standby-timeout-ac 0      # Never sleep
powercfg /change hibernate-timeout-ac 0    # Never hibernate

Write-Host "✅ Display timeout: NEVER (when plugged in)" -ForegroundColor Green
Write-Host "✅ Disk timeout: NEVER (when plugged in)" -ForegroundColor Green
Write-Host "✅ Sleep timeout: NEVER (when plugged in)" -ForegroundColor Green
Write-Host "✅ Hibernate timeout: NEVER (when plugged in)" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Current compression status:" -ForegroundColor Yellow
$paq8 = Get-Process -Name "paq8px-wiki" -ErrorAction SilentlyContinue
if ($paq8) {
    $runtime = (Get-Date) - $paq8.StartTime
    Write-Host "  Process: RUNNING ✅" -ForegroundColor Green
    Write-Host "  Runtime: $($runtime.Hours)h $($runtime.Minutes)m" -ForegroundColor Green
    Write-Host "  Memory: $([math]::Round($paq8.WorkingSet/1MB, 1)) MB" -ForegroundColor Green
    Write-Host "  Expected completion: Friday Nov 29 afternoon" -ForegroundColor Yellow
} else {
    Write-Host "  Process: NOT RUNNING ❌" -ForegroundColor Red
}
Write-Host ""

Write-Host "🔌 IMPORTANT REMINDERS:" -ForegroundColor Cyan
Write-Host "  ✅ Keep laptop PLUGGED IN" -ForegroundColor Green
Write-Host "  ✅ Laptop will NOT sleep while on AC power" -ForegroundColor Green
Write-Host "  ⚠️ If you need to use laptop, compression will slow down" -ForegroundColor Yellow
Write-Host "  ⚠️ Closing lid is OK (if configured to do nothing)" -ForegroundColor Yellow
Write-Host ""

Write-Host "To restore normal power settings after test:" -ForegroundColor Cyan
Write-Host "  powercfg /change monitor-timeout-ac 10" -ForegroundColor White
Write-Host "  powercfg /change standby-timeout-ac 30" -ForegroundColor White
Write-Host ""

Write-Host "✅ Configuration complete! Laptop will stay awake." -ForegroundColor Green
Write-Host "   Compression can continue safely for 40+ hours." -ForegroundColor Green
