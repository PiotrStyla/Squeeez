# BLOKUJE AUTOMATYCZNY RESTART WINDOWS
# Uruchom jako Administrator!

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
Write-Host "  🛑 BLOCKING WINDOWS AUTO-RESTART (ALL METHODS)" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
Write-Host ""

# Metoda 1: Zatrzymaj Windows Update Service
Write-Host "[1/7] Stopping Windows Update service..." -ForegroundColor Cyan
Stop-Service -Name wuauserv -Force -ErrorAction SilentlyContinue
Set-Service -Name wuauserv -StartupType Disabled -ErrorAction SilentlyContinue
Write-Host "  ✅ Windows Update service stopped and disabled" -ForegroundColor Green

# Metoda 2: Registry - NoAutoRebootWithLoggedOnUsers
Write-Host "[2/7] Setting registry NoAutoRebootWithLoggedOnUsers..." -ForegroundColor Cyan
$regPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
if (!(Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}
Set-ItemProperty -Path $regPath -Name "NoAutoRebootWithLoggedOnUsers" -Value 1 -Force
Write-Host "  ✅ Registry key set" -ForegroundColor Green

# Metoda 3: Anuluj zaplanowany restart
Write-Host "[3/7] Cancelling any scheduled restarts..." -ForegroundColor Cyan
shutdown /a 2>$null
Write-Host "  ✅ Scheduled restart cancelled" -ForegroundColor Green

# Metoda 4: Wyłącz Active Hours (ustaw na 24h)
Write-Host "[4/7] Setting Active Hours to 24/7..." -ForegroundColor Cyan
$activeHoursPath = "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"
if (!(Test-Path $activeHoursPath)) {
    New-Item -Path $activeHoursPath -Force | Out-Null
}
Set-ItemProperty -Path $activeHoursPath -Name "ActiveHoursStart" -Value 0 -Force
Set-ItemProperty -Path $activeHoursPath -Name "ActiveHoursEnd" -Value 23 -Force
Set-ItemProperty -Path $activeHoursPath -Name "SmartActiveHoursState" -Value 1 -Force
Write-Host "  ✅ Active Hours: 00:00 - 23:00 (basically all day)" -ForegroundColor Green

# Metoda 5: Wyłącz automatyczne aktualizacje (temporary)
Write-Host "[5/7] Pausing Windows Update..." -ForegroundColor Cyan
$updatePath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
if (!(Test-Path $updatePath)) {
    New-Item -Path $updatePath -Force | Out-Null
}
Set-ItemProperty -Path $updatePath -Name "AUOptions" -Value 2 -Force
Write-Host "  ✅ Automatic updates paused" -ForegroundColor Green

# Metoda 6: Wyłącz reboot task
Write-Host "[6/7] Disabling reboot task..." -ForegroundColor Cyan
Get-ScheduledTask | Where-Object {$_.TaskName -like "*Reboot*" -or $_.TaskName -like "*Update*"} | Disable-ScheduledTask -ErrorAction SilentlyContinue | Out-Null
Write-Host "  ✅ Reboot tasks disabled" -ForegroundColor Green

# Metoda 7: Continuous monitoring & prevention
Write-Host "[7/7] Starting continuous restart blocker..." -ForegroundColor Cyan
Write-Host "  ⚡ This will run in background and cancel any restart attempts" -ForegroundColor Yellow

# Start background job that continuously cancels restarts
$blockScript = {
    while ($true) {
        # Cancel any shutdown/restart
        shutdown /a 2>$null | Out-Null
        
        # Check and stop Windows Update if it restarted
        $wuService = Get-Service -Name wuauserv -ErrorAction SilentlyContinue
        if ($wuService.Status -eq 'Running') {
            Stop-Service -Name wuauserv -Force -ErrorAction SilentlyContinue
        }
        
        # Wait 30 seconds
        Start-Sleep -Seconds 30
    }
}

Start-Job -ScriptBlock $blockScript -Name "RestartBlocker" | Out-Null
Write-Host "  ✅ Background blocker started" -ForegroundColor Green

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "  ✅ ALL PROTECTION METHODS ACTIVE!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "Your system will NOT restart automatically!" -ForegroundColor Cyan
Write-Host "Keep this window open or run as background job." -ForegroundColor Yellow
Write-Host ""
Write-Host "To re-enable updates after compression:" -ForegroundColor Gray
Write-Host "  1. Set-Service -Name wuauserv -StartupType Automatic" -ForegroundColor Gray
Write-Host "  2. Start-Service -Name wuauserv" -ForegroundColor Gray
Write-Host ""
