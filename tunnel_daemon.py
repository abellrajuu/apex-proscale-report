import subprocess
import re
import os
import time
import urllib.request
import qrcode

url_file_local = r"C:\Users\Admin\Desktop\TEST REPORT\CURRENT_MOBILE_URL.txt"
url_file_server = r"\\192.168.100.248\prdndata\ABEL\SFT\TEST REPORT\CURRENT_MOBILE_URL.txt"
qr_file = r"C:\Users\Admin\.gemini\antigravity\brain\fe190a37-1268-4b28-9304-f0bbe08fd04f\live_qr.png"

cmd = [
    r"C:\Windows\System32\OpenSSH\ssh.exe",
    "-R", "80:127.0.0.1:5000",
    "-o", "StrictHostKeyChecking=no",
    "-o", "ServerAliveInterval=30",
    "nokey@localhost.run"
]

while True:
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in proc.stdout:
            match = re.search(r'(https://[a-zA-Z0-9.-]+\.lhr\.life)', line)
            if match:
                url = match.group(1) + "/portal"
                content = f"PRODUCTION REPORT SYSTEM - LIVE MOBILE LINK\n============================================\nURL: {url}\nUpdated: {time.ctime()}\n\nOpen this link on any phone (4G/5G/Wi-Fi).\n"
                print(f"Tunnel URL acquired: {url}", flush=True)
                
                # Write local and server share files
                try:
                    with open(url_file_local, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception:
                    pass
                try:
                    with open(url_file_server, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception:
                    pass
                    
                # Broadcast live URL to ntfy cloud topic for mobile app auto-discovery
                try:
                    req = urllib.request.Request(
                        "https://ntfy.sh/apex_proscale_report_sys_9931",
                        data=url.encode("utf-8"),
                        method="POST"
                    )
                    urllib.request.urlopen(req, timeout=5)
                    print("Broadcasted URL to cloud topic successfully!", flush=True)
                except Exception as e:
                    print(f"Broadcast warning: {e}", flush=True)
                    
                # Generate live QR code image
                try:
                    qr = qrcode.QRCode(box_size=10, border=2)
                    qr.add_data(url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    img.save(qr_file)
                except Exception:
                    pass
        proc.wait()
    except Exception as e:
        print(f"Tunnel error: {e}", flush=True)
    time.sleep(5)
