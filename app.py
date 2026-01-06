import os
from flask import Flask, request, redirect, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import mimetypes
import traceback
import requests

# ---------- Config ----------
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/grant_uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 25 * 1024 * 1024))

# Mailgun / Admin
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")  # e.g., mg.fordfoundationgrant.com
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")        # e.g., danielhogwarts29@gmail.com

# ---------- Initialize Flask ----------
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "very_secret_key_here")

# ---------- Import & register blueprints ----------
from account.routes import account_bp
app.register_blueprint(account_bp, url_prefix="/account")

# ---------- Serve static files ----------
@app.route("/styles/<path:filename>")
def serve_styles(filename):
    return send_from_directory("styles", filename)

@app.route("/<path:filename>")
def serve_root_files(filename):
    return send_from_directory(".", filename)

# ---------- HTML Routes ----------
@app.route("/")
def home():
    return send_from_directory(".", "Home.html")

@app.route("/apply.html")
def apply():
    return send_from_directory(".", "apply.html")

@app.route("/contact.html")
def contact():
    return send_from_directory(".", "contact.html")

@app.route("/success.html")
def success():
    return send_from_directory(".", "success.html")

@app.route("/contact-success.html")
def contact_success():
    return send_from_directory(".", "contact-success.html")

# ---------- Helper Functions ----------
def save_uploaded_files(files: dict):
    saved = []
    for key, file in files.items():
        if file and file.filename:
            filename = secure_filename(file.filename)
            out_path = UPLOAD_DIR / f"{key}__{filename}"
            file.save(out_path)
            saved.append((key, str(out_path)))
    return saved

def send_email_mailgun(subject, body_text, files):
    if not all([MAILGUN_API_KEY, MAILGUN_DOMAIN, ADMIN_EMAIL]):
        raise RuntimeError("Mailgun environment variables are not fully set")

    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    auth = ("api", MAILGUN_API_KEY)
    data = {
        "from": f"Ford Foundation Grant <postmaster@{MAILGUN_DOMAIN}>",
        "to": ADMIN_EMAIL,
        "subject": subject,
        "text": body_text
    }

    # Prepare files for Mailgun attachments
    files_payload = []
    for key, path in files:
        files_payload.append(("attachment", (Path(path).name, open(path, "rb").read())))

    response = requests.post(url, auth=auth, data=data, files=files_payload)
    if not response.ok:
        raise RuntimeError(f"Mailgun email failed: {response.text}")

def notify_admin(subject, body_text, saved_files):
    try:
        send_email_mailgun(subject, body_text, saved_files)
    except Exception as e:
        print("Mailgun email failed:", e)
        traceback.print_exc()

# ---------- API Endpoints ----------
@app.route("/api/submit-application", methods=["POST"])
def submit_application():
    try:
        form_data = dict(request.form)
        saved_files = save_uploaded_files(request.files)

        body_lines = ["New Application Submission", "------------------------"]
        for k, v in form_data.items():
            body_lines.append(f"{k}: {v}")

        if saved_files:
            body_lines.append("\nUploaded files:")
            for k, p in saved_files:
                body_lines.append(f"{k}: {p}")

        subject = f"New application from {form_data.get('full-name', 'Unknown')}"
        notify_admin(subject, "\n".join(body_lines), saved_files)

        return redirect("/success.html")

    except Exception as e:
        print("Application error:", e)
        traceback.print_exc()
        return jsonify({"ok": False, "error": "Server error"}), 500

@app.route("/api/submit-contact", methods=["POST"])
def submit_contact():
    try:
        form_data = dict(request.form)
        saved_files = save_uploaded_files(request.files)

        body_lines = ["New Contact Submission", "------------------------"]
        for k, v in form_data.items():
            body_lines.append(f"{k}: {v}")

        if saved_files:
            body_lines.append("\nAttachments:")
            for k, p in saved_files:
                body_lines.append(f"{k}: {p}")

        subject = f"Contact form: {form_data.get('name', form_data.get('email','Contact'))}"
        notify_admin(subject, "\n".join(body_lines), saved_files)

        return redirect("/contact-success.html")

    except Exception as e:
        print("Contact error:", e)
        traceback.print_exc()
        return jsonify({"ok": False, "error": "Server error"}), 500

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=False)
