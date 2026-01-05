# app.py
import os
from flask import Flask, request, redirect, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import mimetypes
import traceback
import base64

# ---------- Config ----------
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_VERIFIED_SENDER = os.environ.get("SENDGRID_VERIFIED_SENDER")
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/grant_uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 25 * 1024 * 1024))

# ---------- Initialize ----------
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "very_secret_key_here")

# ---------- Import & register blueprints ----------
from account.routes import account_bp
app.register_blueprint(account_bp, url_prefix="/account")

# ---------- Serve static files ----------
@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory(".", path)

@app.route("/")
def index():
    return send_from_directory(".", "Home.html")

# ---------- Helper Functions ----------
def save_uploaded_files(files: dict):
    """Save uploaded files and return list of (fieldname, path)"""
    saved = []
    for key, file in files.items():
        if file and file.filename:
            filename = secure_filename(file.filename)
            out_path = UPLOAD_DIR / f"{key}__{filename}"
            file.save(out_path)
            saved.append((key, str(out_path)))
    return saved

def send_email_via_sendgrid(to_email, subject, body_text, files):
    """Send email using SendGrid API with attachments"""
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Attachment

    if not SENDGRID_API_KEY or not SENDGRID_VERIFIED_SENDER:
        raise RuntimeError("SendGrid API key or verified sender missing")

    message = Mail(
        from_email=SENDGRID_VERIFIED_SENDER,
        to_emails=to_email,
        subject=subject,
        plain_text_content=body_text
    )

    for key, path in files:
        with open(path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        attachment = Attachment(
            file_content=encoded,
            file_type=mimetypes.guess_type(path)[0] or "application/octet-stream",
            file_name=Path(path).name,
            disposition="attachment"
        )
        message.add_attachment(attachment)

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)

def notify_admin(subject, body_text, saved_files):
    """Send email to admin via SendGrid"""
    try:
        send_email_via_sendgrid(ADMIN_EMAIL, subject, body_text, saved_files)
    except Exception as e:
        print("SendGrid email failed:", e)
        traceback.print_exc()

# ---------- API Endpoints ----------
@app.route("/api/submit-application", methods=["POST"])
def submit_application():
    try:
        form_data = {k: v for k, v in request.form.items()}
        saved_files = save_uploaded_files(request.files)

        body_lines = ["New Application Submission", "------------------------"]
        for k, v in form_data.items():
            body_lines.append(f"{k}: {v}")

        if saved_files:
            body_lines.append("\nUploaded files:")
            for k, p in saved_files:
                body_lines.append(f"{k}: {p}")

        subject = f"New application from {form_data.get('full_name', 'Unknown')}"
        notify_admin(subject, "\n".join(body_lines), saved_files)

        return redirect("/success.html")

    except Exception as e:
        print("Application error:", e)
        traceback.print_exc()
        return jsonify({"ok": False, "error": "Server error"}), 500

@app.route("/api/submit-contact", methods=["POST"])
def submit_contact():
    try:
        form_data = {k: v for k, v in request.form.items()}
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
    app.run(debug=True)
