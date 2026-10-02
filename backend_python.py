import sys
import os
import urllib.parse
import socket
import sqlite3
import base64
import json
import shutil
import re
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
from werkzeug.utils import secure_filename
import report_generator_python as docx_generator
import database_python as database

import secrets
from datetime import datetime, timedelta

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

EXPORTS_DIR = os.path.join(BASE_DIR, "backend_report_outputs")
STATIC_DIR = os.path.join(BASE_DIR, "frontend_static_assets")
APKS_DIR = os.path.join(BASE_DIR, "frontend_mobile_apks")

# Persistent dynamic secret key
def _load_or_generate_secret_key():
    env_key = os.environ.get("FLASK_SECRET_KEY")
    if env_key:
        return env_key
    key_file = os.path.join(BASE_DIR, ".flask_secret_key")
    if os.path.exists(key_file):
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                key = f.read().strip()
                if key:
                    return key
        except Exception:
            pass
    new_key = secrets.token_hex(32)
    try:
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(new_key)
    except Exception:
        pass
    return new_key

app = Flask(__name__, template_folder='frontend_html_templates', static_folder='frontend_static_assets', static_url_path='/static')
app.secret_key = _load_or_generate_secret_key()
try:
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
except Exception:
    pass

# Sane session lifetime configured via .env (default: 30 days)
session_days = int(os.environ.get("SESSION_LIFETIME_DAYS", "30"))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=session_days)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() in ("true", "1")
app.config['SESSION_COOKIE_NAME'] = 'production_report_session'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit
app.jinja_env.auto_reload = True

# Login rate limiting tracker (5 attempts per 5 minutes per IP)
_login_failed_attempts = {}
_LOGIN_MAX_FAILURES = 5
_LOGIN_LOCKOUT_SECONDS = 300

def _is_ip_rate_limited(ip):
    now = datetime.now()
    attempts = _login_failed_attempts.get(ip, [])
    cutoff = now - timedelta(seconds=_LOGIN_LOCKOUT_SECONDS)
    valid_attempts = [t for t in attempts if t > cutoff]
    _login_failed_attempts[ip] = valid_attempts
    return len(valid_attempts) >= _LOGIN_MAX_FAILURES

def _record_login_failure(ip):
    now = datetime.now()
    if ip not in _login_failed_attempts:
        _login_failed_attempts[ip] = []
    _login_failed_attempts[ip].append(now)

def _reset_login_failures(ip):
    _login_failed_attempts.pop(ip, None)

# Save screenshots and live testing bugs to local TESTING OUTPUTS directory with network fallback
LOCAL_LIVE_TESTING_DIR = os.path.join(EXPORTS_DIR, "LIVE TESTING")
LOCAL_SCREENSHOTS_DIR = os.path.join(EXPORTS_DIR, "SCREENSHOTS")

if os.path.exists("/home/samba/shares/prdndata"):
    NETWORK_BUGS_DIR          = "/home/samba/shares/prdndata/ABEL/SOFTWARE BUGS/TEST REPORT"
    NETWORK_SCREENSHOTS_DIR   = os.path.join(NETWORK_BUGS_DIR, "SCREENSHOTS")
    NETWORK_LIVE_TESTING_DIR  = os.path.join(NETWORK_BUGS_DIR, "LIVE TESTING")
    NETWORK_FINAL_DWG_DIR     = "/home/samba/shares/Final DWG"
    NETWORK_TEST_REPORT_DIR   = "/home/samba/shares/prdndata/ABEL/TEST REPORT TESTING"
else:
    NETWORK_BUGS_DIR          = r"\\192.168.100.248\prdndata\ABEL\SOFTWARE BUGS\TEST REPORT"
    NETWORK_SCREENSHOTS_DIR   = os.path.join(NETWORK_BUGS_DIR, "SCREENSHOTS")
    NETWORK_LIVE_TESTING_DIR  = os.path.join(NETWORK_BUGS_DIR, "LIVE TESTING")
    # Primary job data source — the "Final DWG" share on the file server
    NETWORK_FINAL_DWG_DIR     = r"\\192.168.100.248\Final DWG"
    # Secondary fallback (old testing folder, kept for backward compat)
    NETWORK_TEST_REPORT_DIR   = r"\\192.168.100.248\prdndata\ABEL\TEST REPORT TESTING"

# ── Network share credential helper ──────────────────────────────────────────
# Credentials are loaded from .env (never committed to git).
# If set, the backend mounts the share automatically on first use.
def _load_network_credentials():
    """Return (username, password) from .env file, or (None, None) if not set."""
    env_file = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_file):
        return None, None
    creds = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip().strip('"').strip("'")
    return creds.get("NETWORK_USER"), creds.get("NETWORK_PASS")

def _ensure_share_mounted(share_path=NETWORK_FINAL_DWG_DIR):
    """
    Try to access the share. If it fails, attempt to mount it using stored credentials.
    Returns True if the share is accessible, False otherwise.
    """
    if os.path.exists(share_path):
        return True
    user, pwd = _load_network_credentials()
    if not user or not pwd:
        return False
    try:
        import subprocess
        if not share_path.startswith(r"\\"):
            return False
        result = subprocess.run(
            ["net", "use", share_path, f"/user:{user}", pwd, "/persistent:no"],
            capture_output=True, text=True, timeout=5
        )
        return os.path.exists(share_path)
    except Exception:
        return False

os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(APKS_DIR, exist_ok=True)
# Network directories will be created lazily when a screenshot is captured to prevent slow app startup
database.init_db()

@app.before_request
def handle_before_request():
    session.permanent = True

    # Enforce strict CSRF / Origin validation on state-changing requests
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")
        expected_host = request.host.lower()

        if origin:
            parsed = urllib.parse.urlparse(origin)
            if parsed.netloc and parsed.netloc.lower() != expected_host:
                return jsonify({"status": "error", "message": "CSRF origin validation failed"}), 403
        elif referer:
            parsed = urllib.parse.urlparse(referer)
            if parsed.netloc and parsed.netloc.lower() != expected_host:
                return jsonify({"status": "error", "message": "CSRF referer validation failed"}), 403
        else:
            # If neither Origin nor Referer is provided on state-changing requests with an active session,
            # require a custom application header (e.g. X-Requested-With, X-App-Client, or Authorization)
            custom_header = (
                request.headers.get("X-Requested-With")
                or request.headers.get("X-App-Client")
                or request.headers.get("Authorization")
            )
            # Allow unauthenticated login POST without custom header
            is_login = request.path == "/login"
            if not custom_header and session.get("user") and not is_login:
                return jsonify({"status": "error", "message": "CSRF protection: state-changing request missing origin verification"}), 403

@app.errorhandler(413)
def request_entity_too_large(error):
    if request.is_json or request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "File exceeds maximum permitted size (50MB)"}), 413
    return "File exceeds maximum permitted size (50MB)", 413

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    response.cache_control.max_age = 0
    return response

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip and not ip.startswith("127."):
                return ip
        except Exception:
            pass
        return "127.0.0.1"

def is_network_share_reachable(ip="192.168.100.248", port=445, timeout=0.2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        res = s.connect_ex((ip, port))
        s.close()
        return res == 0
    except Exception:
        return False

# --- Authorization Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if not user:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"status": "error", "message": "Authentication required"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        if not user or user.get("role") != "Admin":
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"status": "error", "message": "Admin authorization required"}), 403
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# --- Main Navigation & System Routes ---
SYSTEM_ROUTES = {
    "/": "portal.html",
    "/portal": "portal.html",

    # Documentation routes hidden for now per request:
    # "/job-traveller-card": "job_traveller_card.html",
    # "/inprocess-register": "inprocess.html",
    # "/inprocess": "inprocess.html",

    "/belt-scale": "belt_scale.html",
    "/batching-system": "batching_system.html",
    "/remote-indicator": "remote_indicator.html",
    "/digital-indicator": "digital_indicator.html",
    "/weigh-feeder": "weigh_feeder.html",
    "/crane-scale": "crane_scale.html",
    "/signal-conditioner": "signal_conditioner.html",
    "/trip-safe": "trip_safe.html",
    "/vibration-switch": "vibration_switch.html",
    "/acc-mv": "acc_mv.html",
    "/acc-charge": "acc_charge.html",
    "/vibration-meter": "vibration_meter.html",
    "/charge-amplifier": "charge_amplifier.html",
    "/odd-system": "odd_system.html",
    "/dd-system": "dd_system.html",
    "/loss-in-weigh-feeder": "loss_in_weigh_feeder.html",
    "/misc-report": "misc_report.html",
}

for route_path, template_name in SYSTEM_ROUTES.items():
    def make_view(tmpl):
        def view():
            user = session.get("user")
            if not user:
                return redirect(url_for("login"))
            return render_template(tmpl, user=user)
        return view
    endpoint = route_path.replace("/", "").replace("-", "_") or "index"
    app.add_url_rule(route_path, endpoint=endpoint, view_func=make_view(template_name))

@app.route("/admin/portal")
@admin_required
def admin_portal():
    user = session.get("user")
    return render_template("admin_users.html", user=user)

# --- PWA & Mobile App Routes ---
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(STATIC_DIR, "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/manifest.json")
def pwa_manifest():
    return send_from_directory(STATIC_DIR, "manifest.json", mimetype="application/manifest+json")

@app.route("/service-worker.js")
@app.route("/sw.js")
def pwa_service_worker():
    resp = send_from_directory(STATIC_DIR, "service-worker.js", mimetype="application/javascript")
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp

@app.route("/app")
@app.route("/app/")
@app.route("/app//")
def mobile_app_entry():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return redirect(url_for("portal"))

# --- Authentication Routes ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ip = request.remote_addr or "127.0.0.1"
        if _is_ip_rate_limited(ip):
            return render_template("login.html", error="Too many failed login attempts. Please wait 5 minutes before trying again."), 429

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = database.verify_user(username, password)
        if user:
            _reset_login_failures(ip)
            session.permanent = True
            session["user"] = user
            role = user.get("role")
            if role == "Admin":
                return redirect("/admin/portal")
            elif role in ["Verifying Engineer", "HOD"]:
                return redirect('/review-dashboard')
            return redirect(url_for("portal"))
        else:
            _record_login_failure(ip)
            return render_template("login.html", error="Invalid username or password"), 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/download-app")
def download_app():
    candidates = [
        os.path.join(BASE_DIR, "ANDROID APP", "APK", "ProductionReportApp.apk"),
        os.path.join(BASE_DIR, "ProductionReportApp.apk"),
        os.path.join(BASE_DIR, "frontend_mobile_apks", "ProductionReportApp.apk")
    ]
    for apk_path in candidates:
        if os.path.exists(apk_path):
            return send_from_directory(os.path.dirname(apk_path), os.path.basename(apk_path), as_attachment=True)
    return jsonify({"status": "error", "message": "APK file not found"}), 404

@app.route("/service-worker.js")
def service_worker():
    return send_from_directory(STATIC_DIR, "service-worker.js", mimetype="application/javascript")

# --- Live In-Browser Screenshot & Rule Capture API ---
@app.route("/api/capture_screenshot", methods=["POST"])
@login_required
def capture_screenshot():
    try:
        data = request.json or {}
        image_data = data.get("image_data", "")
        note = data.get("note", "").strip()
        page_url = data.get("page_url", "/portal").strip()

        if not image_data or "," not in image_data:
            return jsonify({"status": "error", "message": "Invalid image payload"}), 400

        # Extract base64 content
        header, b64_str = image_data.split(",", 1)
        image_bytes = base64.b64decode(b64_str)

        # 1. SAVE LOCAL FIRST (Guaranteed to succeed)
        os.makedirs(LOCAL_SCREENSHOTS_DIR, exist_ok=True)
        os.makedirs(LOCAL_LIVE_TESTING_DIR, exist_ok=True)
        
        clean_page = secure_filename(page_url.replace("/", "_").strip("_") or "home")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"SCREENSHOT_{clean_page}_{ts}.png"
        live_filepath = os.path.join(LOCAL_LIVE_TESTING_DIR, filename)

        with open(live_filepath, "wb") as f:
            f.write(image_bytes)

        # Save metadata JSON to LOCAL_LIVE_TESTING_DIR
        meta_filename = f"SCREENSHOT_{clean_page}_{ts}.json"
        meta_filepath = os.path.join(LOCAL_LIVE_TESTING_DIR, meta_filename)
        meta_payload = {
            "filename": filename,
            "page_url": page_url,
            "note": note,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "live_filepath": live_filepath
        }
        with open(meta_filepath, "w", encoding="utf-8") as f:
            json.dump(meta_payload, f, indent=2)

        # 2. COPY TO LOCAL SCREENSHOTS DIRECTORY
        screenshots_filepath = os.path.join(LOCAL_SCREENSHOTS_DIR, filename)
        shutil.copy(live_filepath, screenshots_filepath)

        # 3. OPTIONAL NON-BLOCKING COPY TO NETWORK SHARE (IF REACHABLE)
        def _bg_net_copy(src_path, fname):
            try:
                # Fast socket check to prevent thread blocking if host is offline
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.0)
                res = s.connect_ex(("192.168.100.248", 445))
                s.close()
                if res == 0 and os.path.exists(r"\\192.168.100.248\prdndata"):
                    os.makedirs(NETWORK_SCREENSHOTS_DIR, exist_ok=True)
                    shutil.copy(src_path, os.path.join(NETWORK_SCREENSHOTS_DIR, fname))
            except Exception as net_err:
                pass

        import threading
        threading.Thread(target=_bg_net_copy, args=(live_filepath, filename), daemon=True).start()

        # 4. UPDATE RULES.MD WITH STRUCTURED DIRECTIVE RECORD
        rules_path = os.path.join(BASE_DIR, "RULES.md")
        lf_link = live_filepath.replace('\\', '/')
        rf_link = screenshots_filepath.replace('\\', '/')
        rule_entry = (
            f"\n\n### Screenshot Rule Directive [{ts}]\n"
            f"- **Live Screenshot**: [`{filename}`](file:///{lf_link})\n"
            f"- **Reference Image**: [`{filename}`](file:///{rf_link})\n"
            f"- **Page URL**: `{page_url}`\n"
            f"- **User Feedback Directive**: {note or 'No custom text directive provided'}\n"
        )
        with open(rules_path, "a", encoding="utf-8") as f:
            f.write(rule_entry)

        return jsonify({
            "status": "success",
            "message": "Saved screenshot bug directive successfully!",
            "filename": filename,
            "live_filepath": live_filepath,
            "screenshot_url": f"/screenshots/{filename}"
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/screenshots/<path:filename>")
@login_required
def serve_screenshot(filename):
    safe_name = secure_filename(filename)
    if os.path.exists(os.path.join(LOCAL_SCREENSHOTS_DIR, safe_name)):
        return send_from_directory(LOCAL_SCREENSHOTS_DIR, safe_name)
    if os.path.exists(os.path.join(LOCAL_LIVE_TESTING_DIR, safe_name)):
        return send_from_directory(LOCAL_LIVE_TESTING_DIR, safe_name)
    return jsonify({"status": "error", "message": "Screenshot not found"}), 404

# --- User Management REST API ---
@app.route("/api/users", methods=["GET", "POST"])
@admin_required
def manage_users():
    if request.method == "POST":
        data = request.json or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        full_name = data.get("full_name", "").strip() or username
        role = data.get("role", "Production Engineer").strip()

        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password required"}), 400

        try:
            user_id = database.create_user(username, password, full_name, role)
            return jsonify({"status": "success", "user_id": user_id, "message": "User created successfully"})
        except ValueError as ve:
            return jsonify({"status": "error", "message": str(ve)}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": f"User creation failed: {str(e)}"}), 400

    users = database.get_all_users()
    return jsonify({"status": "success", "users": users})

@app.route("/api/users/<int:user_id>/role", methods=["POST"])
@admin_required
def update_user_role_route(user_id):
    data = request.json or {}
    new_role = data.get("role", "").strip()
    if not new_role:
        return jsonify({"status": "error", "message": "Role is required"}), 400
    try:
        database.update_user_role(user_id, new_role)
        return jsonify({"status": "success", "message": f"User role updated to {new_role}"})
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user_route(user_id):
    try:
        database.delete_user(user_id)
        return jsonify({"status": "success", "message": "User deleted successfully"})
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def map_system_dict(d, default_job=""):
    def clean_val(val):
        return str(val).strip() if val is not None else ""

    norm_d = {}
    for k, v in d.items():
        norm_k = re.sub(r'[^a-zA-Z0-9]+', '_', k).strip('_').lower()
        norm_d[norm_k] = clean_val(v)

    def find_val(aliases, fallback_keywords=None):
        for a in aliases:
            if a in norm_d and norm_d[a]:
                return norm_d[a]
        if fallback_keywords:
            for k, v in norm_d.items():
                if v and all(kw in k for kw in fallback_keywords):
                    return v
        return ""

    job = find_val(["job_no", "job", "job_order_no", "order_no", "job_order"], fallback_keywords=["job"]) or default_job
    cust = find_val(["customer_name", "customer", "client_name", "client", "buyer"], fallback_keywords=["custom"]) or find_val([], fallback_keywords=["client"])
    cap = find_val(["capacity", "rated_capacity", "cap"], fallback_keywords=["capac"])
    raw_tag = find_val(["tag_no", "tag", "tag_num", "equipment_tag"], fallback_keywords=["tag"])
    tracking_val = find_val(["tracking_no", "tracking", "track_no", "track_num", "tracking_id"], fallback_keywords=["track"])
    crane_val = find_val(["crane_id", "crane_no", "crane_tag", "crane_num", "crane"], fallback_keywords=["crane"])
    hoist_val = find_val(["hoist_id", "hoist_no", "hoist"], fallback_keywords=["hoist"])
    system_val = find_val(["system", "system_no", "system_tag", "conveyor_no", "conveyor_name", "conveyor_tag"], fallback_keywords=["convey"]) or norm_d.get("system") or ""
    primary_id = crane_val or hoist_val or tracking_val or system_val or raw_tag
    conv = system_val or primary_id
    tag_val = raw_tag if raw_tag else primary_id

    b_load = find_val(["belt_load", "load", "design_load"], fallback_keywords=["belt", "load"]) or norm_d.get("belt_load") or norm_d.get("load") or ""
    b_speed = find_val(["belt_speed", "speed"], fallback_keywords=["speed"])
    ao_out = find_val(["no_of_analogue_output", "no_of_analog_output", "num_outputs", "analog_outputs", "analogue_outputs"], fallback_keywords=["analog"]) or find_val([], fallback_keywords=["output"])

    ind_model = find_val(["indicator_model", "indicator_modle", "digital_indicator_model", "model", "controller_model"], fallback_keywords=["indicat"]) or find_val([], fallback_keywords=["modle"]) or find_val([], fallback_keywords=["model"])
    rem_model = find_val(["remote_model", "remote", "remote_indicator_model", "remote_display_model"], fallback_keywords=["remote"])
    lc_model = find_val(["load_cell_model", "load_cell", "sensor_model", "lc_model", "loadcell_model"], fallback_keywords=["cell"]) or find_val([], fallback_keywords=["load"])

    res = {
        "job_no": f"JOB-{job}" if job and not job.upper().startswith("JOB-") else job,
        "customer": cust,
        "customer_name": cust,
        "capacity": cap,
        "conveyor_no": conv,
        "conveyor_tag": conv,
        "tag_no": tag_val,
        "crane_id": crane_val or primary_id,
        "tracking_no": tracking_val or primary_id,
        "equipment_id": primary_id,
        "bs_model": ind_model,
        "di_model": ind_model,
        "indicator_model": ind_model,
        "sc_model": find_val(["signal_conditioner_model", "sc_model"], fallback_keywords=["conditioner"]) or ind_model,
        "version": find_val(["s_w_version", "version", "sw_version", "software_version"], fallback_keywords=["version"]),
        "sw_version": find_val(["s_w_version", "version", "sw_version", "software_version"], fallback_keywords=["version"]),
        "remote_model": rem_model,
        "remote_display_model": rem_model,
        "sensor_model": lc_model,
        "load_cell_model": lc_model,
        "lc_model": lc_model,
        "tacho_model": find_val(["speed_sensor_model", "tacho_model", "speed_sensor"], fallback_keywords=["tacho"]) or find_val([], fallback_keywords=["speed", "sensor"]),
        "angle_sensor_model": find_val(["angle_sensor_model", "angle_sensor"], fallback_keywords=["angle"]),
        "jbox_model": find_val(["junction_box_1_model", "junction_box_model", "jbox_model1", "jbox_model"], fallback_keywords=["junction", "1"]) or find_val([], fallback_keywords=["jbox"]),
        "jbox_model1": find_val(["junction_box_1_model", "junction_box_model", "jbox_model1"], fallback_keywords=["junction", "1"]) or find_val([], fallback_keywords=["jbox"]),
        "jbox_model2": find_val(["junction_box_2_model", "jbox_model2"], fallback_keywords=["junction", "2"]),
        "jbox_model3": find_val(["junction_box_3_model", "jbox_model3"], fallback_keywords=["junction", "3"]),
        "jbox_serial3": find_val(["junction_box_3_serial_no", "jbox_serial3"], fallback_keywords=["serial"]),
        "belt_load": b_load,
        "belt_speed": b_speed,
        "spec_4": b_load,
        "act_4": b_load,
        "spec_5": b_speed,
        "act_5": b_speed,
        "num_outputs": ao_out,
        "calib_mode": find_val(["calibration_mode", "calib_mode", "calib_type"], fallback_keywords=["calib"]),
        "calib_type": find_val(["calibration_mode", "calib_mode", "calib_type"], fallback_keywords=["calib"]),
        "lc_system": find_val(["no_of_load_cells", "no_of_load_cell", "lc_system"], fallback_keywords=["load", "cells"]),
        "span": find_val(["span"], fallback_keywords=["span"]),
        "tare": find_val(["tare"], fallback_keywords=["tare"]),
        "exc_v": find_val(["excitation_voltage", "exc_v"], fallback_keywords=["excit"]),
        "output_type": find_val(["output_type"], fallback_keywords=["output"])
    }
    return res


@app.route("/api/extract-ga", methods=["POST"])
@login_required
def extract_ga_drawing():
    try:
        ALLOWED_GA_EXTS = {".dwg", ".dxf", ".pdf"}
        if "ga_file" not in request.files:
            data = request.get_json(silent=True) or {}
            filepath = data.get("filepath", "")
            if not filepath or not os.path.exists(filepath):
                return jsonify({"status": "error", "message": "No GA file uploaded or valid filepath provided."}), 400
            
            ext = os.path.splitext(filepath)[1].lower()
            if ext not in ALLOWED_GA_EXTS:
                return jsonify({"status": "error", "message": "Invalid file type. Only .dwg, .dxf, and .pdf files are permitted."}), 400

            # Containment check: restrict filepath to EXPORTS_DIR or user Desktop
            abs_fp = os.path.abspath(filepath)
            desktop_dir = os.path.abspath(os.path.join(os.path.expanduser("~"), "Desktop"))
            exports_dir_abs = os.path.abspath(EXPORTS_DIR)
            if not (abs_fp.startswith(exports_dir_abs) or abs_fp.startswith(desktop_dir)):
                return jsonify({"status": "error", "message": "Access denied: File path outside authorized directories."}), 403
            fname = os.path.basename(filepath)
        else:
            file = request.files["ga_file"]
            if file.filename == "":
                return jsonify({"status": "error", "message": "No file selected."}), 400
            
            fname = secure_filename(file.filename)
            if not fname:
                return jsonify({"status": "error", "message": "Invalid filename."}), 400

            ext = os.path.splitext(fname)[1].lower()
            if ext not in ALLOWED_GA_EXTS:
                return jsonify({"status": "error", "message": "Invalid file type. Only .dwg, .dxf, and .pdf files are permitted."}), 400

            upload_dir = os.path.join(EXPORTS_DIR, "ga_uploads")
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, fname)
            file.save(filepath)

        # 1. FAST CACHE CHECK (< 10ms)
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        json_dir = os.path.join(desktop_dir, "GA_EXTRACTION_OUTPUTS", "json_reports")
        base_name = os.path.splitext(fname)[0]
        cached_json_path = os.path.join(json_dir, f"{base_name}_COMPLETE_DATA.json")

        raw_specs = {}
        if os.path.exists(cached_json_path):
            try:
                with open(cached_json_path, 'r', encoding='utf-8') as jf:
                    cached_data = json.load(jf)
                    raw_specs = cached_data.get("extracted_operating_parameters", {})
                    print(f"[FAST GA CACHE HIT] Loaded specs for {fname} in <10ms!")
            except Exception as e:
                print("Cache load note:", e)

        # 2. IF NOT CACHED, RUN FAST GA_EXTRACTION
        if not raw_specs:
            sys.path.insert(0, BASE_DIR)
            try:
                import data_extraction_python as GA_EXTRACTION
                raw_specs = GA_EXTRACTION.deep_extract_dwg(filepath)
            except Exception as ex:
                raw_specs = {}

        job_match = re.search(r'(SY\d+|\d{4,})', fname, re.IGNORECASE)
        job_no = job_match.group(1) if job_match else fname.split('.')[0]

        def clean_val(val, suffix_to_remove=""):
            if not val: return ""
            s = str(val).strip()
            if suffix_to_remove:
                s = s.replace(suffix_to_remove, "").strip()
            return s

        extracted = {
            "job_no": f"JOB-{job_no}",
            "customer": clean_val(raw_specs.get("customer"), ""),
            "capacity": clean_val(raw_specs.get("rated_capacity"), ""),
            "material": clean_val(raw_specs.get("material"), ""),
            "conveyor_no": clean_val(raw_specs.get("conveyor_tag"), ""),
            "belt_speed": clean_val(raw_specs.get("belt_speed"), "m/s"),
            "belt_width": clean_val(raw_specs.get("belt_width"), "mm"),
            "troughing_angle": clean_val(raw_specs.get("troughing_angle"), "Degrees"),
            "idler_spacing": clean_val(raw_specs.get("idler_spacing"), "mm"),
            "lc_capacity": clean_val(raw_specs.get("load_cell_capacity"), ""),
            "lc_make": clean_val(raw_specs.get("load_cell_make"), ""),
            "lc_qty": clean_val(raw_specs.get("load_cell_qty"), ""),
            "tacho_make": clean_val(raw_specs.get("speed_sensor_make"), ""),
            "tacho_type": clean_val(raw_specs.get("speed_sensor_type"), ""),
            "accuracy": clean_val(raw_specs.get("accuracy"), ""),
            "bulk_density": clean_val(raw_specs.get("bulk_density"), ""),
            "bs_model": clean_val(raw_specs.get("indicator_model"), ""),
            "di_model": clean_val(raw_specs.get("indicator_model"), ""),
            "sc_model": clean_val(raw_specs.get("indicator_model"), ""),
            "sensor_model": clean_val(raw_specs.get("sensor_model"), ""),
            "jbox_model1": clean_val(raw_specs.get("jbox_model"), ""),
            "remote_model": clean_val(raw_specs.get("remote_display_model"), "")
        }

        raw_multi = raw_specs.get("multi_systems", {})
        multi_systems_mapped = {}
        for sys_name, sys_dict in raw_multi.items():
            multi_systems_mapped[sys_name] = map_system_dict(sys_dict, default_job=job_no)

        if multi_systems_mapped:
            first_sys = next(iter(multi_systems_mapped.keys()))
            extracted = multi_systems_mapped[first_sys]

        resp_payload = {
            "status": "success",
            "message": f"Successfully extracted parameters from {fname}",
            "filename": fname,
            "extracted": extracted,
            "raw_specs": raw_specs
        }
        if multi_systems_mapped:
            resp_payload["has_multiple_systems"] = True
            resp_payload["multi_systems"] = multi_systems_mapped
            resp_payload["system_names"] = list(multi_systems_mapped.keys())

        return jsonify(resp_payload)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/fetch-job-data", methods=["GET"])
@login_required
def fetch_job_data():
    raw_job_no = request.args.get("job_no", "").strip()
    if not raw_job_no:
        return jsonify({"status": "error", "message": "Job No is required"}), 400

    clean_job_no = re.sub(r'^(JOB[-_]?)', '', raw_job_no, flags=re.IGNORECASE).strip().upper()
    clean_job_no = re.sub(r'[^a-zA-Z0-9_\-]', '', clean_job_no)
    if not clean_job_no:
        return jsonify({"status": "error", "message": "Invalid Job No"}), 400
    data_dir = os.path.join(BASE_DIR, "backend_job_no_data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

    import glob

    # ── Search order: network Final DWG share → local folder → network testing folder ──
    dwg_candidates = []

    # 1a. Network "Final DWG" share (primary source — where production data lives)
    network_dwg_shares = []
    if is_network_share_reachable() and _ensure_share_mounted(NETWORK_FINAL_DWG_DIR):
        network_dwg_shares.append(NETWORK_FINAL_DWG_DIR)
    if os.path.exists(r"Z:\Final DWG"):
        network_dwg_shares.append(r"Z:\Final DWG")
    elif os.path.exists("Z:\\"):
        network_dwg_shares.append("Z:\\")

    for base_share in network_dwg_shares:
        # Check subdirectories matching job_no (e.g. \\192.168.100.248\Final DWG\SY1498\)
        candidate_subdirs = [
            os.path.join(base_share, clean_job_no),
            os.path.join(base_share, raw_job_no),
            os.path.join(base_share, f"GA {clean_job_no}"),
        ]
        try:
            for entry in os.scandir(base_share):
                if entry.is_dir() and clean_job_no.lower() in entry.name.lower():
                    if entry.path not in candidate_subdirs:
                        candidate_subdirs.append(entry.path)
        except Exception:
            pass

        for c_dir in candidate_subdirs:
            if os.path.isdir(c_dir):
                folder_dwgs = glob.glob(os.path.join(c_dir, "*.dwg"))
                if folder_dwgs:
                    folder_dwgs.sort(key=os.path.getmtime, reverse=True)
                    for f_dwg in folder_dwgs:
                        if f_dwg not in dwg_candidates:
                            dwg_candidates.append(f_dwg)

        # Check root of the share & TEMPLATES
        search_dirs = [base_share]
        templates_dir = os.path.join(base_share, "TEMPLATES")
        if os.path.exists(templates_dir):
            search_dirs.append(templates_dir)

        for s_dir in search_dirs:
            patterns = [
                os.path.join(s_dir, f"{clean_job_no}.dwg"),
                os.path.join(s_dir, f"GA {clean_job_no}.dwg"),
                os.path.join(s_dir, f"{raw_job_no}.dwg"),
            ]
            for p in patterns:
                if os.path.exists(p) and p not in dwg_candidates:
                    dwg_candidates.append(p)
                    break
            if not dwg_candidates:
                net_matches = glob.glob(os.path.join(s_dir, f"*{clean_job_no}*.dwg"))
                if net_matches:
                    net_matches.sort(key=os.path.getmtime, reverse=True)
                    dwg_candidates.append(net_matches[0])

    # 1b. Local backend_job_no_data and Desktop folder
    desktop_dir = os.path.abspath(os.path.join(os.path.expanduser("~"), "Desktop"))
    local_search_dirs = [data_dir, desktop_dir]
    for l_dir in local_search_dirs:
        for fname in [f"{clean_job_no}.dwg", f"GA {clean_job_no}.dwg", f"{raw_job_no}.dwg"]:
            p = os.path.join(l_dir, fname)
            if os.path.exists(p) and p not in dwg_candidates:
                dwg_candidates.append(p)
    if not dwg_candidates:
        for l_dir in local_search_dirs:
            local_matches = glob.glob(os.path.join(l_dir, f"*{clean_job_no}*.dwg"))
            if local_matches:
                local_matches.sort(key=os.path.getmtime, reverse=True)
                dwg_candidates.append(local_matches[0])
                break

    # 1c. Network test report share fallback
    if is_network_share_reachable():
        for fname in [f"{clean_job_no}.dwg", f"GA {clean_job_no}.dwg", f"{raw_job_no}.dwg"]:
            net_dwg = os.path.join(NETWORK_TEST_REPORT_DIR, fname)
            if os.path.exists(net_dwg) and net_dwg not in dwg_candidates:
                dwg_candidates.append(net_dwg)
        if not dwg_candidates:
            net_test_matches = glob.glob(os.path.join(NETWORK_TEST_REPORT_DIR, f"*{clean_job_no}*.dwg"))
            if net_test_matches:
                net_test_matches.sort(key=os.path.getmtime, reverse=True)
                dwg_candidates.append(net_test_matches[0])

    dwg_path = next((c for c in dwg_candidates if os.path.exists(c)), None)

    if dwg_path:
        try:
            sys.path.insert(0, BASE_DIR)
            import data_extraction_python as GA_EXTRACTION
            raw_specs = GA_EXTRACTION.deep_extract_dwg(dwg_path)

            kv = raw_specs.get("extracted_key_values", {})
            raw_multi = raw_specs.get("multi_systems", {})

            # Check if drawing has multi-system table (e.g. SYSTEM 1, SYSTEM 2, ...)
            multi_systems_mapped = {}
            for sys_name, sys_dict in raw_multi.items():
                multi_systems_mapped[sys_name] = map_system_dict(sys_dict)

            # Default extracted is either SYSTEM 1 (if available) or the single-table specs
            if multi_systems_mapped:
                first_sys = next(iter(multi_systems_mapped.keys()))
                extracted = multi_systems_mapped[first_sys]
            else:
                extracted = map_system_dict(kv)

            resp_payload = {
                "status": "success",
                "source": "dwg",
                "extracted": extracted,
                "raw_specs": raw_specs,
                "filename": os.path.basename(dwg_path)
            }
            if multi_systems_mapped:
                resp_payload["has_multiple_systems"] = True
                resp_payload["multi_systems"] = multi_systems_mapped
                resp_payload["system_names"] = list(multi_systems_mapped.keys())

            return jsonify(resp_payload)
        except Exception as e:
            return jsonify({"status": "error", "message": f"DWG extraction failed: {str(e)}"}), 500


    # 2. Search for EXCEL as fallback if DWG not found
    excel_candidates = []

    # Check Final DWG share first (xlsx files may also live there or in job subfolder)
    for base_share in network_dwg_shares:
        candidate_subdirs = [
            os.path.join(base_share, clean_job_no),
            os.path.join(base_share, raw_job_no),
            os.path.join(base_share, f"GA {clean_job_no}"),
        ]
        try:
            for entry in os.scandir(base_share):
                if entry.is_dir() and clean_job_no.lower() in entry.name.lower():
                    if entry.path not in candidate_subdirs:
                        candidate_subdirs.append(entry.path)
        except Exception:
            pass

        for c_dir in candidate_subdirs:
            if os.path.isdir(c_dir):
                folder_xls = glob.glob(os.path.join(c_dir, "*.xlsx")) + glob.glob(os.path.join(c_dir, "*.xls"))
                if folder_xls:
                    folder_xls.sort(key=os.path.getmtime, reverse=True)
                    for f_xl in folder_xls:
                        if f_xl not in excel_candidates:
                            excel_candidates.append(f_xl)

        for fname in [f"{clean_job_no}.xlsx", f"{raw_job_no}.xlsx"]:
            p = os.path.join(base_share, fname)
            if os.path.exists(p) and p not in excel_candidates:
                excel_candidates.append(p)
        if not excel_candidates:
            xl_matches = glob.glob(os.path.join(base_share, f"*{clean_job_no}*.xlsx"))
            if xl_matches:
                xl_matches.sort(key=os.path.getmtime, reverse=True)
                excel_candidates.append(xl_matches[0])

    # Local folder
    for fname in [f"{clean_job_no}.xlsx", f"{raw_job_no}.xlsx"]:
        p = os.path.join(data_dir, fname)
        if os.path.exists(p) and p not in excel_candidates:
            excel_candidates.append(p)

    # Old testing network share fallback
    if is_network_share_reachable():
        net_xlsx = os.path.join(NETWORK_TEST_REPORT_DIR, f"{clean_job_no}.xlsx")
        if os.path.exists(net_xlsx) and net_xlsx not in excel_candidates:
            try:
                local_copy = os.path.join(data_dir, f"{clean_job_no}.xlsx")
                shutil.copy2(net_xlsx, local_copy)
                excel_candidates.insert(0, local_copy)
            except Exception:
                excel_candidates.append(net_xlsx)

    excel_path = next((p for p in excel_candidates if os.path.exists(p)), None)

    if excel_path:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(excel_path, data_only=True)
            
            def clean_val_xl(val):
                return str(val).strip() if val is not None else ""

            def match_system_header(raw_header):
                if not raw_header: return None
                h = str(raw_header).rstrip(':').strip()
                m = re.match(r'^(SYSTEM|SYS\.?|CONVEYOR|CONV\.?|CV\.?|UNIT|STREAM)\s*(?:NO\.?|NUM\.?|NUMBER|#|[-_:])?\s*(\d+|[IVXLCDM]+)$', h, re.IGNORECASE)
                if m:
                    num_str = m.group(2)
                    return f"SYSTEM {num_str.upper()}"
                return None

            # Check if multiple sheets named SYSTEM 1, system no 1, SYS-1... exist
            multi_excel = {}
            for sname in wb.sheetnames:
                canon_name = match_system_header(sname)
                if canon_name:
                    ws = wb[sname]
                    sheet_data = {}
                    for row in ws.iter_rows(values_only=True):
                        if row and len(row) > 0 and row[0] is not None:
                            sheet_data[str(row[0]).strip().upper()] = clean_val_xl(row[1] if len(row) > 1 else "")
                    if sheet_data:
                        multi_excel[canon_name] = sheet_data

            # Check if active sheet has multi-system columns (e.g. Header row: PARAMETER, system no 1, SYS-2...)
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            if not multi_excel and rows:
                header = [clean_val_xl(c) for c in rows[0]] if rows[0] else []
                sys_col_indices = {}
                for idx, col_h in enumerate(header):
                    canon_name = match_system_header(col_h)
                    if canon_name:
                        sys_col_indices[canon_name] = idx

                # Fallback: if header row has simple numbers 1, 2, 3... across columns
                if not sys_col_indices and len(header) >= 3:
                    candidate_nums = {}
                    for idx in range(1, len(header)):
                        val = header[idx].strip()
                        if val.isdigit():
                            candidate_nums[f"SYSTEM {int(val)}"] = idx
                    if len(candidate_nums) >= 2:
                        sys_col_indices = candidate_nums

                if sys_col_indices:
                    for sname, col_idx in sys_col_indices.items():
                        s_data = {}
                        for r in rows[1:]:
                            if r and len(r) > 0 and r[0] is not None:
                                k = str(r[0]).strip().upper()
                                v = clean_val_xl(r[col_idx]) if col_idx < len(r) else ""
                                s_data[k] = v
                        multi_excel[sname] = s_data

            if multi_excel:
                multi_systems_mapped = {}
                for sys_name, sys_dict in multi_excel.items():
                    multi_systems_mapped[sys_name] = map_system_dict(sys_dict)
                first_sys = next(iter(multi_systems_mapped.keys()))
                return jsonify({
                    "status": "success",
                    "source": "excel",
                    "has_multiple_systems": True,
                    "multi_systems": multi_systems_mapped,
                    "system_names": list(multi_systems_mapped.keys()),
                    "extracted": multi_systems_mapped[first_sys],
                    "filename": os.path.basename(excel_path)
                })

            # Single system 2-column Excel
            data = {}
            for row in rows:
                if row and len(row) > 0 and row[0] is not None:
                    key = str(row[0]).strip().upper()
                    val = row[1] if len(row) > 1 and row[1] is not None else ""
                    data[key] = str(val).strip()

            extracted = map_system_dict(data)
            return jsonify({
                "status": "success",
                "source": "excel",
                "data": data,
                "extracted": extracted,
                "filename": os.path.basename(excel_path)
            })
        except Exception as e:
            return jsonify({"status": "error", "message": f"Excel read failed: {str(e)}"}), 500

    return jsonify({"status": "error", "message": f"No DWG file ({clean_job_no}.dwg) found in JOB NO DATA folder."}), 404


@app.route("/api/fetch-job-excel", methods=["GET"])
@login_required
def fetch_job_excel():
    raw_job_no = request.args.get("job_no", "").strip()
    if not raw_job_no:
        return jsonify({"status": "error", "message": "Job No is required"}), 400

    job_no = re.sub(r'[^a-zA-Z0-9_\-]', '', raw_job_no)
    if not job_no:
        return jsonify({"status": "error", "message": "Invalid Job No"}), 400
        
    excel_dir = os.path.join(BASE_DIR, "backend_job_no_data")
    if not os.path.exists(excel_dir):
        os.makedirs(excel_dir, exist_ok=True)
        
    filepath = os.path.join(excel_dir, f"{job_no}.xlsx")
    if not os.path.exists(filepath):
        return jsonify({"status": "error", "message": f"Excel file {job_no}.xlsx not found in JOB NO DATA folder."}), 404
        
    try:
        import openpyxl
        wb = openpyxl.load_workbook(filepath, data_only=True)
        ws = wb.active
        data = {}
        for row in ws.iter_rows(values_only=True):
            if row and len(row) > 0 and row[0] is not None:
                key = str(row[0]).strip().upper()
                val = row[1] if len(row) > 1 and row[1] is not None else ""
                data[key] = str(val).strip()
                
        return jsonify({
            "status": "success",
            "message": f"Successfully loaded data for {job_no}",
            "job_no": job_no,
            "data": data
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to parse Excel file: {str(e)}"}), 500


@app.route("/api/version", methods=["GET"])
def get_version():
    return jsonify({
        "status": "online",
        "app": "PRODUCTION TEST REPORT",
        "version": "3.1.3",
        "build_version": "2026.08.31",
        "timestamp": datetime.now().isoformat()
    })

# --- Report Submission & Retrieval REST API ---
@app.route("/api/submit", methods=["POST"])
@login_required
def submit_record():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload provided"}), 400

        report_type = data.get("report_type", "belt_scale")
        
        # Use session user if available, fallback to data payload, then fallback to Unknown User
        user_info = session.get('user', {})
        user_name = user_info.get('full_name') or user_info.get('username') or data.get("user_name", "Unknown User")
        user_name = user_name.strip()
        
        job_no = data.get("job_no", "JOB-001").strip()
        customer = data.get("customer", "N/A").strip()
        conveyor_no = data.get("conveyor_no", "N/A").strip()
        capacity = data.get("capacity", "N/A").strip()

        # Auto-fill testing metadata
        data["tested_by"] = user_name
        data["date"] = datetime.now().strftime("%d-%b-%Y")

        safe_job = re.sub(r'[<>:"/\|?*]', '', job_no).strip() or "JOB-001"
        safe_user = re.sub(r'[<>:"/\|?*]', '', user_name).strip() or "Tech"
        
        type_map = {
            "job_traveller_card": "Job Traveller Card",
            "belt_scale": "Belt Scale",
            "batching_system": "Batching System",
            "remote_indicator": "Remote Indicator",
            "digital_indicator": "Digital Indicator",
            "weigh_feeder": "Weigh Feeder",
            "crane_scale": "Crane Scale",
            "signal_conditioner": "Signal Conditioner",
            "trip_safe": "Trip Safe",
            "vibration_switch": "Vibration Switch",
            "acc_mv": "ACC mV",
            "acc_charge": "ACC Charge",
            "vibration_meter": "Vibration Meter",
            "charge_amplifier": "Charge Amplifier",
            "inprocess_register": "Inprocess Register",
            "inprocess": "Inprocess",
            "misc_report": "Misc Report",
            "misc": "Misc Report",
            "odd_system": "ODD System",
            "dd_system": "DD System",
            "work_instructions": "Work Instructions",
            "performance_index": "Performance Index",
            "performance_delay_analysis": "Performance Delay Analysis",
            "performance_delay": "Performance Delay Analysis",
            "equipment_list": "Equipment List",
            "loss_in_weigh_feeder": "Loss in Weigh Feeder",
        }
        human_type = type_map.get(report_type, "Report")

        # Keep resolution values and measured parameters clean without appending unit strings
        # Units are defined in the template column headers

        docx_filename = f"{human_type} - {safe_job} - {safe_user}.docx"
        pdf_filename = f"{human_type} - {safe_job} - {safe_user}.pdf"
        output_path = os.path.join(EXPORTS_DIR, docx_filename)

        # Generate DOCX and PDF
        docx_generator.generate_docx_record(data, output_path)

        # Save to SQLite Database
        record_id = database.save_record(user_name, job_no, customer, conveyor_no, capacity, data, docx_filename)

        pdf_path = os.path.join(EXPORTS_DIR, pdf_filename)
        resp = {
            "status": "success",
            "message": "Report submitted and document generated successfully!",
            "record_id": record_id,
            "docx_filename": docx_filename,
            "docx_download_url": f"/download/{urllib.parse.quote(docx_filename)}"
        }
        if os.path.exists(pdf_path):
            resp["pdf_filename"] = pdf_filename
            resp["pdf_download_url"] = f"/download/{urllib.parse.quote(pdf_filename)}"

        return jsonify(resp)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/records", methods=["GET"])
@login_required
def list_records():
    records = database.get_all_records()
    return jsonify({"status": "success", "records": records})

@app.route("/api/records/<int:record_id>", methods=["GET"])
@login_required
def get_record(record_id):
    rec = database.get_record_by_id(record_id)
    if rec:
        return jsonify({"status": "success", "record": rec})
    return jsonify({"status": "error", "message": "Record not found"}), 404

@app.route("/api/clear_records", methods=["POST"])
@admin_required
def clear_records():
    try:
        conn = database.get_db_connection()
        try:
            conn.execute("DELETE FROM records")
            conn.commit()
        finally:
            conn.close()
        return jsonify({"status": "success", "message": "All records cleared."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/download/<path:filename>")
def download_file(filename):
    safe_name = os.path.basename(filename)
    if not safe_name:
        return jsonify({"status": "error", "message": "Invalid filename"}), 400

    # Whitelist allowed downloadable extensions
    ext = os.path.splitext(safe_name)[1].lower()
    allowed_exts = {".pdf", ".docx", ".apk", ".png", ".json"}
    if ext not in allowed_exts:
        return jsonify({"status": "error", "message": "Access denied: File type not permitted for download."}), 403

    # Require authenticated session for all downloads except .apk installer
    if ext != ".apk" and not session.get("user"):
        if request.is_json or request.path.startswith("/api/"):
            return jsonify({"status": "error", "message": "Authentication required to download files"}), 401
        return redirect(url_for("login"))

    # Check apks/ directory first for mobile app binaries (download attachment)
    if os.path.exists(os.path.join(APKS_DIR, safe_name)):
        return send_from_directory(APKS_DIR, safe_name, as_attachment=True)
    # Check EXPORTS_DIR / TESTING OUTPUTS
    if os.path.exists(os.path.join(EXPORTS_DIR, safe_name)):
        return send_from_directory(EXPORTS_DIR, safe_name, as_attachment=True, download_name=safe_name)
    
    # Check EXPORTS_DIR subdirectories (e.g. LIVE TESTING, SCREENSHOTS, ga_uploads)
    for sub in ["LIVE TESTING", "SCREENSHOTS", "ga_uploads"]:
        sub_dir = os.path.join(EXPORTS_DIR, sub)
        if os.path.exists(os.path.join(sub_dir, safe_name)):
            return send_from_directory(sub_dir, safe_name, as_attachment=True, download_name=safe_name)

    return jsonify({"status": "error", "message": "File not found"}), 404

# --- Multi-Role Workflow Endpoints ---

@app.route('/review-dashboard')
@login_required
def review_dashboard():
    user = session.get("user")
    return render_template("review_dashboard.html", user=user)

@app.route('/api/pending-reviews')
@login_required
def get_pending_reviews():
    user = session.get("user")
    role = user.get("role")
    records = database.get_pending_records(role)
    return jsonify({"status": "success", "records": records})

@app.route('/api/approve/<int:record_id>', methods=['POST'])
@login_required
def approve_report(record_id):
    user = session.get("user")
    if not user:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    role = user.get("role")
    if role not in ["Verifying Engineer", "HOD", "Admin"]:
        return jsonify({"status": "error", "message": "Invalid Role for Approval"}), 403
        
    result = database.update_record_approval(record_id, user.get("full_name"), role)
    if not result:
        return jsonify({"status": "error", "message": "Record not found"}), 404
        
    data_dict, docx_filename = result
    
    try:
        # Re-generate the PDF with the new signatures
        output_path = os.path.join(EXPORTS_DIR, docx_filename)
        docx_generator.generate_docx_record(data_dict, output_path)
        return jsonify({"status": "success", "message": "Approved and signed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    ip = get_local_ip()
    port = 5000
    print("\n========================================================")
    print("  PRODUCTION TEST REPORT")
    print(f"  - Laptop (Local):        http://localhost:{port}")
    print(f"  - Mobile (Current IP):   http://{ip}:{port}")
    print(f"  - Mobile (Any Wi-Fi):    http://DESKTOP-ITTFPI2.local:{port}")
    print("========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
