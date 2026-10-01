# Mobile & Android App Guide (Multi-Wi-Fi Solutions)

This folder contains everything needed for running the **Production Report System** on Android phones, tablets, and mobile devices across multiple Wi-Fi networks.

---

## ⚡ The Problem: "I have 5–6 different Wi-Fi networks"

When you move between different Wi-Fi networks (Office, Factory Floor, Warehouse, Home, Mobile Hotspot):
* Every router assigns your laptop a **different IP address** (e.g. `192.168.1.50`, `192.168.0.12`, `10.0.0.104`).
* A mobile app with a **hardcoded IP** will stop working as soon as you change Wi-Fi.

Here are the **4 permanent ways** to solve this issue so you never have to re-configure or struggle with changing IPs:

---

## 🏆 Solution 1: Use the Computer Hostname (Zero Setup, Works Everywhere)

Your laptop has a permanent local network name:
```text
http://DESKTOP-ITTFPI2.local:5050
```

* **Why it works**: Windows automatically advertises its hostname via mDNS (multicast DNS). Modern Android (Android 12+) and all Apple iOS devices resolve `.local` names automatically on whatever Wi-Fi you connect to.
* **How to use**:
  1. Connect your phone to whichever Wi-Fi your laptop is currently using.
  2. Open Chrome, Edge, or Safari on your phone.
  3. Go to: **`http://DESKTOP-ITTFPI2.local:5050`**
  4. You never need to look up or type IP addresses again!

---

## 📱 Solution 2: Instant QR Code Scanner (1-Click Connect)

Whenever you switch to a new Wi-Fi network and want to connect your phone instantly:

1. Double-click **`connect_mobile.bat`** inside this folder (or run `python show_wifi_qr.py`).
2. A QR code appears on your laptop screen containing the exact live Wi-Fi address.
3. Open your mobile phone camera or QR scanner and point it at the screen.
4. Tap the link that pops up on your phone — you are connected immediately!

---

## 🚀 Solution 3: Add to Home Screen (PWA - No APK Needed!)

Once you open the portal in mobile Chrome:

1. Tap the **Three Dots Menu (⋮)** in the top-right corner of Chrome.
2. Select **"Add to Home screen"** or **"Install app"**.
3. A dedicated icon named **"Production Report System"** will appear on your phone's home screen.
4. It opens in **full-screen standalone app mode** (no browser address bar) just like a native app.
5. All reports, PDFs, and Word documents download directly to your phone's storage.

---

## 🛠️ Solution 4: Native Android Studio App (with Dynamic Server Switcher)

Inside `android_studio_project/`, we have provided the full Android Studio native project:
* **Dynamic Server Config**: If the app cannot connect or Wi-Fi changes, it presents a settings dialog:
  * **"Use Laptop Hostname"** button (connects to `DESKTOP-ITTFPI2.local:5050`).
  * **"Auto-Scan Wi-Fi"** button (probes your local subnet to find the running server).
  * Manual Host/Port entry.
* **Native Downloads**: Directly hooks into Android `DownloadManager` for one-tap report downloads.
* **File Uploads**: Supports selecting CAD drawings and Excel files directly from your phone.

To build an updated APK:
1. Open `android_studio_project/` in **Android Studio**.
2. Click **Build -> Build Bundle(s) / APK(s) -> Build APK(s)**.
3. Transfer the generated `.apk` to any Android phone.

---

## 📶 Solution 5: Factory Floor / Zero-Wi-Fi Mode (Windows Mobile Hotspot)

If you are on a factory floor or customer site where **no Wi-Fi router is available**:

1. On your Windows laptop: Go to **Windows Settings -> Network & internet -> Mobile hotspot**.
2. Turn **Mobile hotspot** ON.
3. Connect your Android phone to your laptop's hotspot network.
4. On your phone, open:
   ```text
   http://192.168.137.1:5050
   ```
   *(Windows Hotspot always uses the fixed IP `192.168.137.1`, completely offline without internet!)*

---

## 📂 Folder Contents

```
ANDROID APP/
├── APK/
│   └── ProductionReportApp.apk          # Base distribution build
├── android_studio_project/              # Complete Android Studio Native Source
│   ├── app/src/main/
│   │   ├── java/com/production/reportapp/MainActivity.java
│   │   ├── res/layout/ (activity_main.xml, dialog_server_config.xml)
│   │   └── AndroidManifest.xml
│   ├── build.gradle
│   └── settings.gradle
├── connect_mobile.bat                   # 1-Click launcher to display live QR code & Wi-Fi link
├── show_wifi_qr.py                      # Python auto-detect script for IP and terminal QR code
└── README_MOBILE_GUIDE.md               # This complete guide
```

---

## 🍏 Solution 6: iPhone & iPad iOS Safari PWA ($0 Apple Fee)

Apple charges a mandatory $99–$100 annual fee to put apps on the iOS App Store, plus requires an Apple Mac computer to build `.ipa` binaries. 

You can bypass this completely for **$0 cost** with full native performance using **Safari PWA**:
1. Connect the iPhone/iPad to the company Wi-Fi network.
2. Open **Safari** and navigate to: `http://DESKTOP-ITTFPI2.local:5050` (or scan the QR code).
3. Tap the **Share** icon (the square with an arrow pointing upward at the bottom of Safari).
4. Scroll down and tap **"Add to Home Screen"**.
5. Tap **"Add"** in the top-right corner.
6. The **IPA Reports** app icon appears on the iPhone home screen.
7. Tapping it opens the app in **standalone full-screen mode** — no Safari URL bar, no browser navigation buttons. It looks, feels, and functions identically to an App Store application.

---

## 🔄 Zero-Update Architecture for 100 Employees

Because both the Android APK and the iOS Safari PWA operate as live shells connected to your server:
* **Never redistribute APKs**: When you update report formulas, calibration grids, Word document generators, or styles on your server, all 100 employee phones **automatically receive the new version instantly** on their next tap.
* **No employee manual updates**: Employees never have to download, reinstall, or side-load APK updates.
* **Adaptive Sizing**: The application automatically adjusts to every phone size (360px small Androids, 390px iPhones, 412px Galaxy flagships, 430px iPhone Pro Max, and 768px+ tablets) with zero data misalignment or button overlap.

