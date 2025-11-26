# Download enwik9 for Hutter Prize testing
# enwik9 = first 10^9 bytes of English Wikipedia XML

$url = "https://mattmahoney.net/dc/enwik9.zip"
$zipFile = "C:\HutterLab\data\enwik9.zip"
$extractPath = "C:\HutterLab\data\"

Write-Host "Downloading enwik9 (1 GB compressed)..."
Write-Host "This will take several minutes..."

# Download
try {
    Invoke-WebRequest -Uri $url -OutFile $zipFile -UseBasicParsing
    Write-Host "✅ Download complete!"
    
    # Extract
    Write-Host "Extracting enwik9..."
    Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force
    
    # Verify
    $enwik9 = Get-Item "$extractPath\enwik9"
    Write-Host "✅ Extraction complete!"
    Write-Host "Size: $($enwik9.Length) bytes (expected: 1,000,000,000)"
    
    if ($enwik9.Length -eq 1000000000) {
        Write-Host "✅ Verified! Ready for compression testing!"
    } else {
        Write-Host "⚠️ Warning: Size mismatch. Expected 1 GB exactly."
    }
    
} catch {
    Write-Host "❌ Error: $_"
    Write-Host ""
    Write-Host "Alternative download:"
    Write-Host "1. Visit: http://mattmahoney.net/dc/enwik9.zip"
    Write-Host "2. Download manually"
    Write-Host "3. Extract to C:\HutterLab\data\"
}
