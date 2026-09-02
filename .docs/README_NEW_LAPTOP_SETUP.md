# IPA Private Limited - APEX ProScale™ Industrial Suite
## New Laptop Quick Setup & Migration Guide

Welcome to your new laptop setup! All application source code, databases, PDF export engines, and Android mobile app build tools have been packaged cleanly into this standalone folder.

---

## 📁 Included Project Files & Structure
* 📄 **`app.py`** - Primary Python Flask Backend Server (Handles auth, API submission, PDF downloads, and routes)
* 🗄️ **`database.py` & `production_reports.db`** - SQLite Database containing authorized user credentials and production test records
* 📑 **`docx_generator.py`** - Native 1-Page PDF & DOCX Calibration Report Engine
* 🎨 **`templates/` & `static/`** - Enterprise Light Blue & Crisp White Web UI (`index.html`, `portal.html`, `login.html`, `admin_users.html`, `style.css`, `app.js`)
* 📱 **`android_app/` & `build_apk.bat`** - Full Android Studio Mobile App project & 1-click APK compiler script (`BeltScaleApp.apk`)
* 🚀 **`run_server.bat`** - 1-Click Server Launcher for Windows
* 📦 **`requirements.txt`** - Required Python Dependencies

---

## 🚀 How to Run on Your New Laptop (3 Simple Steps)

### Step 1: Install Python
Ensure Python 3.10+ (or Python 3.12) is installed on your new laptop.
*(Make sure to check "Add Python to PATH" during installation).*

### Step 2: Double-Click `run_server.bat`
Double-click **`run_server.bat`** inside this folder. It will:
1. Automatically install required dependencies (`pip install -r requirements.txt`).
2. Launch the server and display your new laptop's Wi-Fi IP address.

### Step 3: Access the System
Open your web browser (Chrome / Edge / Brave):
* 💻 **Local Desktop:** `http://localhost:5000`
* 🛡️ **Admin Portal:** `http://localhost:5000/admin/portal`
* 📱 **Mobile & Wi-Fi Devices:** `http://<YOUR_NEW_LAPTOP_IP>:5000`

---

## 🔑 Default Login Credentials
* **System Administrator:** `admin` / `admin`
* **Field Technician:** `tech` / `123`

---

## 🛠️ How to Compile Mobile Android APK (`BeltScaleApp.apk`)
If you want to recompile the mobile app on your new laptop:
1. Ensure Java / Android SDK or Gradle is available.
2. Double-click **`build_apk.bat`**.
3. The new **`BeltScaleApp.apk`** will be generated directly in the folder!

---
*Created for IPA Private Limited - APEX ProScale™ Systems*
