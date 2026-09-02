import os, subprocess, zipfile, shutil

USER_PROFILE = os.environ.get("USERPROFILE", r"C:\Users\abell")
SDK_DIR = os.path.join(USER_PROFILE, r"AppData\Local\Android\Sdk")
BUILD_TOOLS = os.path.join(SDK_DIR, "build-tools", "34.0.0")
PLATFORM_JAR = os.path.join(SDK_DIR, "platforms", "android-34", "android.jar")
JAVA_HOME = r"C:\Program Files\Microsoft\jdk-17.0.20.101-hotspot"
JAVAC = os.path.join(JAVA_HOME, "bin", "javac.exe")

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(PROJECT_DIR, "android_app")
BUILD_DIR = os.path.join(APP_DIR, "build_out")
os.makedirs(BUILD_DIR, exist_ok=True)

env = os.environ.copy()
env["JAVA_HOME"] = JAVA_HOME
env["PATH"] = os.path.join(JAVA_HOME, "bin") + ";" + env["PATH"]
env["_JAVA_OPTIONS"] = "-Xmx2048m -Xms64m -XX:+UseSerialGC"

# 1. Create Java MainActivity
java_src_dir = os.path.join(BUILD_DIR, "src", "com", "production", "reportapp")
os.makedirs(java_src_dir, exist_ok=True)

java_code = """package com.production.reportapp;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebSettings;
import android.app.DownloadManager;
import android.net.Uri;
import android.os.Environment;
import android.webkit.CookieManager;
import android.webkit.URLUtil;
import android.webkit.DownloadListener;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setUseWideViewPort(false);
        settings.setLoadWithOverviewMode(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setAllowFileAccess(true);
        settings.setDatabaseEnabled(true);
        webView.setHorizontalScrollBarEnabled(true);
        webView.setVerticalScrollBarEnabled(true);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                view.loadUrl(url);
                return true;
            }
        });

        webView.setDownloadListener(new DownloadListener() {
            @Override
            public void onDownloadStart(String url, String userAgent, String contentDisposition, String mimetype, long contentLength) {
                DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
                request.setMimeType(mimetype);
                String cookies = CookieManager.getInstance().getCookie(url);
                request.addRequestHeader("cookie", cookies);
                request.addRequestHeader("User-Agent", userAgent);
                request.setTitle(URLUtil.guessFileName(url, contentDisposition, mimetype));
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, URLUtil.guessFileName(url, contentDisposition, mimetype));

                DownloadManager dm = (DownloadManager) getSystemService(DOWNLOAD_SERVICE);
                dm.enqueue(request);
            }
        });

        webView.loadUrl("http://10.199.141.77:5000/portal");
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
"""

with open(os.path.join(java_src_dir, "MainActivity.java"), "w", encoding="utf-8") as f:
    f.write(java_code)

print("1. Java source created!")

# 2. Compile Java file to .class
classes_dir = os.path.join(BUILD_DIR, "classes")
os.makedirs(classes_dir, exist_ok=True)

javac_cmd = [
    JAVAC,
    "-cp", PLATFORM_JAR,
    "-d", classes_dir,
    os.path.join(java_src_dir, "MainActivity.java")
]

print("2. Compiling Java source...")
res = subprocess.run(javac_cmd, capture_output=True, text=True, env=env)
if res.returncode != 0:
    print("Javac failed:", res.stderr)
    exit(1)

# 3. Convert .class to classes.dex using d8
d8_bat = os.path.join(BUILD_TOOLS, "d8.bat")
class_files = []
for root_dir, _, files in os.walk(classes_dir):
    for file in files:
        if file.endswith(".class"):
            class_files.append(os.path.join(root_dir, file))

d8_cmd = [
    d8_bat,
    "--classpath", PLATFORM_JAR,
    "--output", BUILD_DIR,
] + class_files

print("3. Converting .class to classes.dex with d8...")
res = subprocess.run(d8_cmd, capture_output=True, text=True, shell=True, env=env)
if res.returncode != 0:
    print("d8 failed:", res.stderr)
    exit(1)

# 4. Standalone AndroidManifest.xml
manifest_path = os.path.join(BUILD_DIR, "AndroidManifest.xml")
manifest_xml = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.production.reportapp">

    <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="34" />

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:label="Production Report Hub"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.DeviceDefault.NoActionBar"
        android:usesCleartextTraffic="true">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
"""

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(manifest_xml)

aapt2_exe = os.path.join(BUILD_TOOLS, "aapt2.exe")
unsigned_apk = os.path.join(PROJECT_DIR, "ProductionReportApp_unsigned.apk")

aapt2_cmd = [
    aapt2_exe, "link",
    "-I", PLATFORM_JAR,
    "--min-sdk-version", "26",
    "--target-sdk-version", "34",
    "--manifest", manifest_path,
    "-o", unsigned_apk
]

print("4. Packaging resources with aapt2...")
res = subprocess.run(aapt2_cmd, capture_output=True, text=True, env=env)
if res.returncode != 0:
    print("aapt2 failed:", res.stderr)
    exit(1)

# 5. Add classes.dex into unsigned APK
dex_file = os.path.join(BUILD_DIR, "classes.dex")
with zipfile.ZipFile(unsigned_apk, 'a') as z:
    z.write(dex_file, "classes.dex")

print("5. Added classes.dex into APK!")

# 6. Generate Keystore & Sign APK
ks_file = os.path.join(BUILD_DIR, "debug.keystore")
keytool_exe = os.path.join(JAVA_HOME, "bin", "keytool.exe")

if not os.path.exists(ks_file):
    kt_cmd = [
        keytool_exe, "-genkeypair",
        "-keystore", ks_file,
        "-storepass", "android",
        "-alias", "androiddebugkey",
        "-keypass", "android",
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-dname", "CN=Android Debug,O=Android,C=US"
    ]
    subprocess.run(kt_cmd, capture_output=True, text=True, env=env)

final_apk = os.path.join(PROJECT_DIR, "ProductionReportApp.apk")
apksigner_bat = os.path.join(BUILD_TOOLS, "apksigner.bat")

sign_cmd = [
    apksigner_bat, "sign",
    "--ks", ks_file,
    "--ks-pass", "pass:android",
    "--key-pass", "pass:android",
    "--out", final_apk,
    unsigned_apk
]

print("6. Signing APK with apksigner...")
res = subprocess.run(sign_cmd, capture_output=True, text=True, shell=True, env=env)

if os.path.exists(final_apk):
    print("\n=======================================================")
    print("SUCCESS: REAL APK COMPILED SUCCESSFULLY!")
    print("Location:", final_apk)
    print("Size:", os.path.getsize(final_apk), "bytes")
    print("=======================================================")
else:
    print("Sign failed:", res.stderr)


