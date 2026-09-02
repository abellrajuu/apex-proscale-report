# Infinite loop to keep the ADB reverse tunnel alive
while ($true) {
    # Suppress output to avoid spamming the log
    & .\platform-tools\adb.exe reverse tcp:5000 tcp:5000 2>$null
    Start-Sleep -Seconds 3
}
