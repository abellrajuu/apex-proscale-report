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
import docx_generator
import database

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "apex_proscale_enterprise_key_2026")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE_DIR, "TESTING OUTPUTS")
APKS_DIR = os.path.join(BASE_DIR, "apks")

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
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = '*'
    return response

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# --- Authorization Decorators ---
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
    "/": "index.html",
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
            user = session.get("user", {"username": "tech", "role": "Technician"})
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
            session["user"] = user
            return redirect(url_for("portal"))
        else:
            return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

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

        # 3. OPTIONAL COPY TO NETWORK SHARE (IF REACHABLE)
        try:
            os.makedirs(NETWORK_SCREENSHOTS_DIR, exist_ok=True)
            net_filepath = os.path.join(NETWORK_SCREENSHOTS_DIR, filename)
            shutil.copy(live_filepath, net_filepath)
        except Exception as net_err:
            print("Network drive copy skipped:", net_err)

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
def manage_users():
    if request.method == "POST":
        data = request.json or {}
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        full_name = data.get("full_name", "").strip()
        role = data.get("role", "Technician").strip()

        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password required"}), 400

        try:
            user_id = database.create_user(username, password, full_name, role)
            return jsonify({"status": "success", "user_id": user_id, "message": "User created successfully"})
        except Exception as e:
            return jsonify({"status": "error", "message": f"User creation failed: {str(e)}"}), 400

    users = database.get_all_users()
    return jsonify({"status": "success", "users": users})

# --- System Version & Heartbeat API ---


@app.route("/api/extract-ga", methods=["POST"])
def extract_ga_drawing():
    try:
        if "ga_file" not in request.files:
            data = request.json or {}
            filepath = data.get("filepath", "")
            if not filepath or not os.path.exists(filepath):
                return jsonify({"status": "error", "message": "No GA file uploaded or valid filepath provided."}), 400
            fname = os.path.basename(filepath)
        else:
            file = request.files["ga_file"]
            if file.filename == "":
                return jsonify({"status": "error", "message": "No file selected."}), 400
            
            fname = file.filename
            upload_dir = os.path.join(EXPORTS_DIR, "ga_uploads")
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, fname)
            file.save(filepath)

        # 1. FAST CACHE CHECK (< 10ms)
        json_dir = r"C:\Users\abell\OneDrive\Desktop\GA_EXTRACTION_OUTPUTS\json_reports"
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
                import GA_EXTRACTION
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
            "bulk_density": clean_val(raw_specs.get("bulk_density"), "")
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
def submit_record():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON payload provided"}), 400

        report_type = data.get("report_type", "belt_scale")
        
        # Use session user if available, fallback to data payload, then fallback to Unknown User
        session_user = session.get('user', {}).get('username')
        user_name = session_user or data.get("user_name", "Unknown User")
        user_name = user_name.strip()
        
        job_no = data.get("job_no", "JOB-001").strip()
        customer = data.get("customer", "N/A").strip()
        conveyor_no = data.get("conveyor_no", "N/A").strip()
        capacity = data.get("capacity", "N/A").strip()

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

        # Append resolution units dynamically as requested
        if data.get("res_l"):
            data["res_l"] = f"{data['res_l']} Kg/m"
        if data.get("res_s"):
            data["res_s"] = f"{data['res_s']} m/s"
        if data.get("res_r"):
            data["res_r"] = f"{data['res_r']} TPH"
        if data.get("res_t"):
            data["res_t"] = f"{data['res_t']} Tonnes"

        # Hardcode act_4 and act_5 units so they don't have to be in the UI
        if report_type == 'belt_scale':
            data['act_4'] = 'Kg/m'
            data['act_5'] = 'm/s'

        docx_filename = f"{human_type} - {safe_job} - {safe_user}.docx"
        pdf_filename = f"{human_type} - {safe_job} - {safe_user}.pdf"
        output_path = os.path.join(EXPORTS_DIR, docx_filename)

        # Generate DOCX and PDF
        docx_generator.generate_docx_record(data, output_path)

        # Save to SQLite Database
        record_id = database.save_record(user_name, job_no, customer, conveyor_no, capacity, data, docx_filename)

        return jsonify({
            "status": "success",
            "message": "Report submitted and document generated successfully!",
            "record_id": record_id,
            "docx_filename": docx_filename,
            "pdf_filename": pdf_filename,
            "pdf_download_url": f"/download/{urllib.parse.quote(pdf_filename)}",
            "docx_download_url": f"/download/{urllib.parse.quote(docx_filename)}"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/records", methods=["GET"])
def list_records():
    records = database.get_all_records()
    return jsonify({"status": "success", "records": records})

@app.route("/api/records/<int:record_id>", methods=["GET"])
def get_record(record_id):
    rec = database.get_record_by_id(record_id)
    if rec:
        return jsonify({"status": "success", "record": rec})
    return jsonify({"status": "error", "message": "Record not found"}), 404

@app.route("/api/clear_records", methods=["POST"])
@admin_required
def clear_records():
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, "production_reports.db"))
        conn.execute("DELETE FROM records")
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "All records cleared."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/download/<path:filename>")
def download_file(filename):
    safe_name = os.path.basename(filename)
    if not safe_name:
        return jsonify({"status": "error", "message": "Invalid filename"}), 400

    # Check apks/ directory first for mobile app binaries
    if os.path.exists(os.path.join(APKS_DIR, safe_name)):
        return send_from_directory(APKS_DIR, safe_name, as_attachment=True)
    # Check EXPORTS_DIR / TESTING OUTPUTS
    if os.path.exists(os.path.join(EXPORTS_DIR, safe_name)):
        return send_from_directory(EXPORTS_DIR, safe_name, as_attachment=True)
    # Fallback to root directory
    if os.path.exists(os.path.join(BASE_DIR, safe_name)):
        return send_from_directory(BASE_DIR, safe_name, as_attachment=True)
    return jsonify({"status": "error", "message": "File not found"}), 404

if __name__ == "__main__":
    ip = get_local_ip()
    port = 5000
    print("\n========================================================")
    print("  PRODUCTION TEST REPORT")
    print(f"  - Laptop (Local):   http://localhost:{port}")
    print(f"  - Mobile (Wi-Fi):   http://{ip}:{port}")
    print("========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
