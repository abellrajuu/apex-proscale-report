# -*- coding: utf-8 -*-
import socket
import os
import qrcode

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def main():
    ip = get_ip()
    port = 5000
    mdns_url = f"http://DESKTOP-ITTFPI2.local:{port}/portal"
    ip_url = f"http://{ip}:{port}/portal"

    print("===================================================================")
    print("       MOBILE & ANDROID WI-FI AUTO-CONNECTOR")
    print("===================================================================")
    print(f"Current Wi-Fi IP Address:   {ip}")
    print(f"Local Hostname URL:        {mdns_url}  (Works on ANY Wi-Fi!)")
    print(f"Direct Wi-Fi IP URL:       {ip_url}")
    print("-------------------------------------------------------------------")
    print("Scan this QR code with your mobile camera to open the Portal:")
    print("")

    qr = qrcode.QRCode(border=1)
    qr.add_data(ip_url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

    print("")
    print("===================================================================")
    print("HOW TO CONNECT ACROSS DIFFERENT WI-FI NETWORKS:")
    print("1. Option A (Easiest): Open your phone camera, scan the QR code above.")
    print(f"2. Option B (Hostname): In phone browser, type: {mdns_url}")
    print("   (Hostname never changes even when you switch between your 5-6 Wi-Fi networks!)")
    print("3. Option C (Hotspot): Turn on Windows Mobile Hotspot and connect phone directly.")
    print("===================================================================")
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
