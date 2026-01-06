import os
import smtplib
import traceback
import mimetypes
from pathlib import Path
from email.message import EmailMessage
from flask import Flask, request, redirect, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# =========================================================
# CONFIG
# =========================================================
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/grant_uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 25 * 1024 * 1024))

# =========================================================
# FLASK INIT
# =========================================================
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "very_secret_key_here")

# =========================================================
# BLUEPRINTS
# =========================================================
from account.routes import account_bp
app.register_blueprint(account_bp, url_prefix="/account")

# =========================================================
# STATIC FILE ROUTES
# =========================================================
@app.route("/styles/<path:filename>")
def serve_styles(filename):
    return send_from_directory("styles", filename)

@app.route("/<path:filename>")
def serve_root_files(filename):
    return send_from_directory(".", filename)

# =========================================================
# HTML ROUTES
# =========================================================
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

# =========================================================
# HELPERS
# =========================================================
def save_uploaded_files(files):
    saved = []
    for key, file in files.items():
        if file and file.filename:
            filename = secure_filename(file.filename)
            path = UPLOAD_DIR / f"{key}__{filename}"
            file.save(path)
            saved.append((key, str(path)))
    return saved


def send_email_smtp(subject, body_text, attachments):
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, ADMIN_EMAIL]):
        raise RuntimeError("SMTP environment variables are not fully set")

    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = ADMIN_EMAIL
    msg["Subject"] = subject
    msg.set_content(body_text)

    for _, path in attachments:
        with open(path, "rb") as f:
            data = f.read()
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type:
            maintype, subtype = mime_type.split("/", 1)
        else:
            maintype, subtype = "application", "octet-stream"

        msg.add_attachment(
            data,
            maintype=maintype,
            subtype=subtype,
            filename=Path(path).name
        )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def notify_admin(subject, body_text, saved_files):
    try:
        send_email_smtp(subject, body_text, saved_files)
    except Exception as e:
        print("SMTP email failed:", e)
        traceback.print_exc()

# =========================================================
# API ENDPOINTS
# =========================================================
@app.route("/api/submit-application", methods=["POST"])
def submit_application():
    try:
        form_data = dict(request.form)
        saved_files = save_uploaded_files(request.files)

        body = ["New Application Submission", "------------------------"]
        for k, v in form_data.items():
            body.append(f"{k}: {v}")

        if saved_files:
            body.append("\nUploaded files:")
            for k, p in saved_files:
                body.append(f"{k}: {p}")

        subject = f"New application from {form_data.get('full-name', 'Unknown')}"
        notify_admin(subject, "\n".join(body), saved_files)

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

        body = ["New Contact Submission", "------------------------"]
        for k, v in form_data.items():
            body.append(f"{k}: {v}")

        subject = f"Contact form: {form_data.get('name', form_data.get('email', 'Contact'))}"
        notify_admin(subject, "\n".join(body), saved_files)

        return redirect("/contact-success.html")

    except Exception as e:
        print("Contact error:", e)
        traceback.print_exc()
        return jsonify({"ok": False, "error": "Server error"}), 500

# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    app.run(debug=False)
