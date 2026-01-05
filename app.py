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
    """Serve CSS files from styles folder"""
    return send_from_directory("styles", filename)

@app.route("/<path:filename>")
def serve_root_files(filename):
    """Serve JS, images, or any other file in root folder"""
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

def send_email_via_sendgrid(to_email, subject, body_text, files):
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
    try:
        send_email_via_sendgrid(ADMIN_EMAIL, subject, body_text, saved_files)
    except Exception as e:
        print("SendGrid email failed:", e)
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
