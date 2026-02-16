# Battery and Compression Monitor
# Checks every 5 minutes if battery is low or compression stopped

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  🔋⚙️ BATTERY & COMPRESSION MONITOR STARTED" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Monitoring compression PID: 3184" -ForegroundColor White
Write-Host "Check interval: 5 minutes" -ForegroundColor White
Write-Host "Battery warning threshold: 30%" -ForegroundColor White
Write-Host "Critical threshold: 15%" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
Write-Host ""

$compressionPID = 3184
$logFile = "C:\HutterLab\monitor_log.txt"

# Create log header
"Monitor started: $(Get-Date)" | Out-File $logFile
"" | Out-File $logFile -Append

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # Check battery
    $battery = Get-WmiObject Win32_Battery -ErrorAction SilentlyContinue
    
    if ($battery) {
        $chargeLevel = $battery.EstimatedChargeRemaining
        $isPluggedIn = ($battery.BatteryStatus -eq 2)
        
        # Status line
        $status = "[$timestamp] Battery: $chargeLevel% | Plugged: $(if($isPluggedIn){'YES'}else{'NO'})"
        
        # Check compression process
        $proc = Get-Process -Id $compressionPID -ErrorAction SilentlyContinue
        
        if ($proc) {
            $cpuMinutes = [math]::Round($proc.CPU/60, 1)
            $memoryMB = [math]::Round($proc.WorkingSet/1MB, 1)
            $status += " | Compression: ✅ (CPU: ${cpuMinutes}m, RAM: ${memoryMB}MB)"
        } else {
            $status += " | Compression: ❌ STOPPED!"
            Write-Host ""
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
            Write-Host "  ❌ CRITICAL: COMPRESSION STOPPED!" -ForegroundColor Red
            Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Red
            Write-Host ""
            [console]::beep(1000,500)
            [console]::beep(1000,500)
            [console]::beep(1000,500)
        }
        
        # Log to file
        $status | Out-File $logFile -Append
        
        # Color-coded output based on battery level
        $color = "Green"
        $alert = ""
        
        if (-not $isPluggedIn) {
            $color = "Red"
            $alert = " ⚠️ NOT PLUGGED IN!"
            [console]::beep(2000,300)
        } elseif ($chargeLevel -lt 15) {
            $color = "Red"
            $alert = " 🚨 CRITICAL!"
            [console]::beep(2000,200)
        } elseif ($chargeLevel -lt 30) {
            $color = "Yellow"
            $alert = " ⚠️ WARNING!"
        }
        
        Write-Host $status$alert -ForegroundColor $color
        
    } else {
        Write-Host "[$timestamp] Unable to read battery status" -ForegroundColor Gray
    }
    
    # Wait 5 minutes
    Start-Sleep -Seconds 300
}
