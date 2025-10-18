# app.py
import os
from flask import Flask, request, redirect, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import mimetypes
import traceback
import smtplib
from email.message import EmailMessage

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
    SENDGRID_AVAILABLE = True
except Exception:
    SENDGRID_AVAILABLE = False

# ---------- Config ----------
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/grant_uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 25 * 1024 * 1024))

# ---------- Initialize ----------
app = Flask(__name__, static_folder="")  # Serve current folder as static
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ---------- Serve Static Files ----------
@app.route("/<path:path>")
def serve_file(path):
    return send_from_directory(".", path)

@app.route("/")
def index():
    return send_from_directory(".", "Home.html")

## ---------- Helpers ----------
def save_uploaded_files(files: dict):
    saved = []
    for key, file in files.items():
        if file and file.filename:
            filename = secure_filename(file.filename)
            out_path = UPLOAD_DIR / f"{key}__{filename}"
            file.save(out_path)
            saved.append((key, str(out_path)))
    return saved

def send_email_via_sendgrid(subject, plain_text, files):
    """Send email using SendGrid from verified sender to ADMIN_EMAIL."""
    if not SENDGRID_AVAILABLE or not SENDGRID_API_KEY:
        raise RuntimeError("SendGrid not available or API key missing")

    message = Mail(
        from_email="support@fordfoundationgrant.com",  # Verified sender
        to_emails=ADMIN_EMAIL,                         # Use env variable
        subject=subject,
        plain_text_content=plain_text
    )

    import base64
    for key, path in files:
        with open(path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        attachment = Attachment(
            FileContent(encoded),
            FileName(Path(path).name),
            FileType(mimetypes.guess_type(path)[0] or "application/octet-stream"),
            Disposition("attachment")
        )
        message.add_attachment(attachment)

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    return sg.send(message)


def send_email_via_smtp(to_email, subject, plain_text, files):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(plain_text)

    for key, path in files:
        with open(path, "rb") as f:
            data = f.read()
        content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
        maintype, subtype = content_type.split("/", 1) if "/" in content_type else ("application", "octet-stream")
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=Path(path).name)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(msg)


def notify_admin(subject, body_text, saved_files):
    try:
        if SENDGRID_AVAILABLE and SENDGRID_API_KEY:
            send_email_via_sendgrid(subject, body_text, saved_files)
        else:
            # fallback to SMTP if needed
            send_email_via_smtp(ADMIN_EMAIL, subject, body_text, saved_files)
    except Exception as e:
        print("Email send failed:", e)
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

# ---------- Run Server ----------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
