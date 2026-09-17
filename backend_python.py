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

app = Flask(__name__, template_folder='frontend_html_templates', static_folder='frontend_static_assets', static_url_path='/static')
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "test_report_production_secure_secret_key_2026"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE_DIR, "backend_report_outputs")
APKS_DIR = os.path.join(BASE_DIR, "frontend_mobile_apks")

# Save screenshots and live testing bugs to local TESTING OUTPUTS directory with network fallback
LOCAL_LIVE_TESTING_DIR = os.path.join(EXPORTS_DIR, "LIVE TESTING")
LOCAL_SCREENSHOTS_DIR = os.path.join(EXPORTS_DIR, "SCREENSHOTS")

NETWORK_BUGS_DIR = r"\\192.168.100.248\prdndata\ABEL\SOFTWARE BUGS\TEST REPORT"
NETWORK_SCREENSHOTS_DIR = os.path.join(NETWORK_BUGS_DIR, "SCREENSHOTS")
NETWORK_LIVE_TESTING_DIR = os.path.join(NETWORK_BUGS_DIR, "LIVE TESTING")

os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(APKS_DIR, exist_ok=True)
# Network directories will be created lazily when a screenshot is captured to prevent slow app startup
database.init_db()

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
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

    "/job-traveller-card": "job_traveller_card.html",
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
    "/inprocess-register": "inprocess.html",
    "/inprocess": "inprocess.html",
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

# --- Authentication Routes ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = database.verify_user(username, password)
        if user:
            session.permanent = True
            session["user"] = user
            role = user.get("role")
            if role == "Admin":
                return redirect("/admin/portal")
            elif role in ["Verifying Engineer", "HOD"]:
                return redirect('/review-dashboard')
            return redirect(url_for("portal"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/download-app")
def download_app():
    apk_path = os.path.join(BASE_DIR, "ProductionReportApp.apk")
    if os.path.exists(apk_path):
        return send_from_directory(BASE_DIR, "ProductionReportApp.apk", as_attachment=True)
    return jsonify({"status": "error", "message": "APK file not found"}), 404

# --- Live In-Browser Screenshot & Rule Capture API ---
@app.route("/api/capture_screenshot", methods=["POST"])
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
        rule_entry = (
            f"\n\n### Screenshot Rule Directive [{ts}]\n"
            f"- **Live Screenshot**: [`{filename}`](file:///{live_filepath.replace('\\', '/')})\n"
            f"- **Reference Image**: [`{filename}`](file:///{screenshots_filepath.replace('\\', '/')})\n"
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

# --- System Version & Heartbeat API ---


@app.route("/api/extract-ga", methods=["POST"])
def extract_ga_drawing():
    try:
        if "ga_file" not in request.files:
            data = request.json or {}
            filepath = data.get("filepath", "")
            if not filepath or not os.path.exists(filepath):
                return jsonify({"status": "error", "message": "No GA file uploaded or valid filepath provided."}), 400
            
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
            "sensor_model": clean_val(raw_specs.get("sensor_model"), ""),
            "jbox_model1": clean_val(raw_specs.get("jbox_model"), ""),
            "remote_model": clean_val(raw_specs.get("remote_display_model"), "")
        }

        return jsonify({
            "status": "success",
            "message": f"Successfully extracted parameters from {fname}",
            "filename": fname,
            "extracted": extracted,
            "raw_specs": raw_specs
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/fetch-job-data", methods=["GET"])
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

    # 1. Search for matching DWG file in JOB NO DATA folder
    dwg_candidates = [
        os.path.join(data_dir, f"{clean_job_no}.dwg"),
        os.path.join(data_dir, f"{raw_job_no}.dwg"),
        os.path.join(data_dir, f"GA {clean_job_no}.dwg")
    ]

    # Wildcard search as fallback
    if not any(os.path.exists(p) for p in dwg_candidates):
        import glob
        matches = glob.glob(os.path.join(data_dir, f"*{clean_job_no}*.dwg"))
        if matches:
            dwg_candidates.insert(0, matches[0])
        else:
            # Secondary fallback: find any .dwg file in JOB NO DATA
            all_dwgs = glob.glob(os.path.join(data_dir, "*.dwg"))
            if all_dwgs:
                dwg_candidates.append(all_dwgs[0])

    dwg_path = None
    for cand in dwg_candidates:
        if os.path.exists(cand):
            dwg_path = cand
            break

    if dwg_path:
        try:
            sys.path.insert(0, BASE_DIR)
            import data_extraction_python as GA_EXTRACTION
            raw_specs = GA_EXTRACTION.deep_extract_dwg(dwg_path)

            def clean_val(val):
                return str(val).strip() if val is not None else ""

            kv = raw_specs.get("extracted_key_values", {})

            # Alias normalization across CAD keys and UI Form field IDs
            indicator_val = clean_val(kv.get("indicator_model") or kv.get("indicator") or kv.get("bs_model") or raw_specs.get("indicator_model") or raw_specs.get("indicator"))
            sensor_val = clean_val(kv.get("sensor_model") or kv.get("load_cell") or kv.get("lc_model") or raw_specs.get("sensor_model") or raw_specs.get("load_cell"))
            jbox_val = clean_val(kv.get("jbox_model") or kv.get("junction_box") or kv.get("jbox_model1") or raw_specs.get("jbox_model") or raw_specs.get("junction_box"))
            speed_val = clean_val(kv.get("belt_speed") or kv.get("speed") or raw_specs.get("belt_speed") or raw_specs.get("speed"))
            capacity_val = clean_val(kv.get("capacity") or kv.get("rated_capacity") or raw_specs.get("rated_capacity") or raw_specs.get("capacity"))
            remote_val = clean_val(kv.get("remote_display") or kv.get("remote_model") or kv.get("remote_display_model") or raw_specs.get("remote_display"))

            extracted = {
                "job_no": f"JOB-{clean_job_no}",
                "customer": clean_val(kv.get("customer") or raw_specs.get("customer")),
                "capacity": capacity_val,
                "rated_capacity": capacity_val,
                "material": clean_val(kv.get("material") or raw_specs.get("material")),
                "conveyor_no": clean_val(kv.get("conveyor_no") or kv.get("conveyor_tag") or raw_specs.get("conveyor_tag")),
                "belt_speed": speed_val,
                "speed": speed_val,
                "belt_width": clean_val(kv.get("belt_width") or raw_specs.get("belt_width")),
                "troughing_angle": clean_val(kv.get("troughing_angle") or raw_specs.get("troughing_angle")),
                "idler_spacing": clean_val(kv.get("idler_spacing") or raw_specs.get("idler_spacing")),
                "lc_capacity": clean_val(kv.get("load_cell_capacity") or raw_specs.get("load_cell_capacity")),
                "lc_make": clean_val(kv.get("load_cell_make") or raw_specs.get("load_cell_make")),
                "lc_qty": clean_val(kv.get("load_cell_qty") or raw_specs.get("load_cell_qty")),
                "bs_model": indicator_val,
                "indicator_model": indicator_val,
                "indicator": indicator_val,
                "sensor_model": sensor_val,
                "lc_model": sensor_val,
                "load_cell": sensor_val,
                "jbox_model1": jbox_val,
                "jbox_model": jbox_val,
                "junction_box": jbox_val,
                "remote_model": remote_val,
                "remote_display": remote_val,
                "remote_display_model": remote_val
            }
            # Include all dynamically parsed key-values as well
            for k, v in kv.items():
                if k not in extracted and v:
                    extracted[k] = clean_val(v)

            return jsonify({
                "status": "success",
                "source": "dwg",
                "extracted": extracted,
                "raw_specs": raw_specs,
                "filename": os.path.basename(dwg_path)
            })
        except Exception as e:
            return jsonify({"status": "error", "message": f"DWG extraction failed: {str(e)}"}), 500


    # 2. Search for EXCEL as fallback if DWG not found
    excel_candidates = [
        os.path.join(data_dir, f"{clean_job_no}.xlsx"),
        os.path.join(data_dir, f"{raw_job_no}.xlsx")
    ]
    excel_path = next((p for p in excel_candidates if os.path.exists(p)), None)
    if excel_path:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(excel_path, data_only=True)
            ws = wb.active
            data = {}
            for row in ws.iter_rows(values_only=True):
                if row and len(row) > 0 and row[0] is not None:
                    key = str(row[0]).strip().upper()
                    val = row[1] if len(row) > 1 and row[1] is not None else ""
                    data[key] = str(val).strip()
            return jsonify({"status": "success", "source": "excel", "data": data, "filename": os.path.basename(excel_path)})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Excel read failed: {str(e)}"}), 500

    return jsonify({"status": "error", "message": f"No DWG file ({clean_job_no}.dwg) found in JOB NO DATA folder."}), 404


@app.route("/api/fetch-job-excel", methods=["GET"])
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

        # Generate DOCX and PDF (reload module dynamically so code updates take effect immediately)
        import importlib
        importlib.reload(docx_generator)
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
def review_dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template("review_dashboard.html", user=user)

@app.route('/api/pending-reviews')
def get_pending_reviews():
    user = session.get("user")
    if not user:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    role = user.get("role")
    records = database.get_pending_records(role)
    return jsonify({"status": "success", "records": records})

@app.route('/api/approve/<int:record_id>', methods=['POST'])
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
        import importlib
        importlib.reload(docx_generator)
        output_path = os.path.join(EXPORTS_DIR, docx_filename)
        docx_generator.generate_docx_record(data_dict, output_path)
        return jsonify({"status": "success", "message": "Approved and signed successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    ip = get_local_ip()
    port = 5050
    print("\n========================================================")
    print("  PRODUCTION TEST REPORT")
    print(f"  - Laptop (Local):   http://localhost:{port}")
    print(f"  - Mobile (Wi-Fi):   http://{ip}:{port}")
    print("========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
