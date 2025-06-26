from flask import Flask, request, render_template, jsonify, flash, redirect, url_for
import os
import json
import base64
import datetime
import uuid
import requests
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from fpdf import FPDF
import logging
import re
from utils import build_html_email, validate_egyptian_phone
from gmail_auth import load_gmail_creds

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-default-secret-key")

# Configuration
EMAIL_A = os.environ.get("SENDER_EMAIL", "saher.sharaf68@gmail.com")
EMAIL_B = os.environ.get("RECIPIENT_EMAIL", "basemgalal96@gmail.com")
GMAIL_TOKEN_PATH = "tokens/token_saher.sharaf68@gmail.com.pickle"
PENDING_FILE = "pending_replies.json"
TELEGRAM_BOT_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN", "8050331002:AAGTmnGjeUSAH6bkiWQYbuXwyBjxO0CwZEI")
TELEGRAM_USERS_MAP = "telegram_users.json"

# Create necessary directories
os.makedirs("pdfs", exist_ok=True)
os.makedirs("tokens", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)


@app.route("/")
def index():
    """Render the main hospitality request form"""
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def handle_submission():
    """Handle form submission and send email"""
    try:
        # Extract form data
        owner = request.form.get("owner", "").strip()
        membership = request.form.get("membership", "").strip()
        bookings = request.form.getlist("booking")
        from_date = request.form.get("fromDate", "").strip()
        to_date = request.form.get("toDate", "").strip()
        guests = request.form.getlist("guest")
        notes = request.form.get("notes", "").strip()
        telegram = request.form.get("telegram", "").strip()
        uploaded_file = request.files.get("file")

        # Clean and validate data
        bookings = [b.strip() for b in bookings if b.strip()]
        guests = [g.strip() for g in guests if g.strip()]

        # Validate required fields
        if not owner:
            flash("اسم المالك مطلوب", "error")
            return redirect(url_for("index"))

        if not membership:
            flash("رقم العضوية مطلوب", "error")
            return redirect(url_for("index"))

        if not telegram or not validate_egyptian_phone(telegram):
            flash(
                "رقم التليجرام غير صحيح. يجب أن يبدأ بـ 01 ويتكون من 10-11 رقم",
                "error")
            return redirect(url_for("index"))

        if not from_date or not to_date:
            flash("تواريخ الإقامة مطلوبة", "error")
            return redirect(url_for("index"))

        # Prepare email content
        subject = 'طلب استضافة'
        request_data = {
            "owner": owner,
            "membership": membership,
            "bookings": " | ".join(bookings) if bookings else "غير محدد",
            "from_date": from_date,
            "to_date": to_date,
            "guests": " | ".join(guests) if guests else "غير محدد",
            "notes": notes if notes else "لا توجد ملاحظات",
            "telegram": telegram
        }

        html_body = build_html_email(request_data)

        # Load Gmail credentials and send email
        try:
            creds = load_gmail_creds()
            service = build("gmail", "v1", credentials=creds)

            # Create email message
            message = MIMEMultipart()
            message["to"] = EMAIL_B
            message["from"] = EMAIL_A
            message["subject"] = subject
            message.attach(MIMEText(html_body, "html"))

            # Handle file attachment
            if uploaded_file and uploaded_file.filename:
                try:
                    file_content = uploaded_file.read()
                    part = MIMEApplication(file_content,
                                           Name=uploaded_file.filename)
                    part[
                        "Content-Disposition"] = f'attachment; filename="{uploaded_file.filename}"'
                    message.attach(part)

                    # Save uploaded file
                    upload_path = os.path.join(
                        "uploads", f"{uuid.uuid4()}_{uploaded_file.filename}")
                    with open(upload_path, "wb") as f:
                        f.write(file_content)

                except Exception as e:
                    logging.error(f"Error handling file upload: {e}")
                    flash("حدث خطأ في رفع الملف", "error")
                    return redirect(url_for("index"))

            # Send email
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(userId="me", body={
                "raw": raw
            }).execute()

            # Save to pending requests
            save_pending_request({
                "id":
                str(uuid.uuid4()),
                "timestamp":
                datetime.datetime.utcnow().isoformat(),
                "subject":
                subject,
                "telegram":
                telegram,
                "owner":
                owner,
                "membership":
                membership,
                "guests":
                " | ".join(guests) if guests else "غير محدد",
                "bookings":
                " | ".join(bookings) if bookings else "غير محدد",
                "from_date":
                from_date,
                "to_date":
                to_date,
                "notes":
                notes if notes else "لا توجد ملاحظات",
                "status":
                "pending"
            })

            # Generate PDF record
            generate_pdf_record(request_data)

            flash("تم إرسال الطلب بنجاح! سيتم التواصل معك قريباً.", "success")
            return redirect(url_for("index"))

        except Exception as e:
            logging.error(f"Gmail API error: {e}")
            flash(
                "حدث خطأ في إرسال البريد الإلكتروني. يرجى المحاولة مرة أخرى.",
                "error")
            return redirect(url_for("index"))

    except Exception as e:
        logging.error(f"General error in handle_submission: {e}")
        flash(f"حدث خطأ غير متوقع: {str(e)}", "error")
        return redirect(url_for("index"))


def save_pending_request(entry):
    """Save pending request to JSON file"""
    try:
        data = []
        if os.path.exists(PENDING_FILE):
            with open(PENDING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        data.append(entry)

        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        logging.error(f"Error saving pending request: {e}")


def generate_pdf_record(request_data):
    """Generate PDF record of the request"""
    try:
        pdf = FPDF()
        pdf.add_page()

        # Note: FPDF doesn't handle Arabic well by default
        # This is a basic implementation
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Hospitality Request Record", ln=True, align="C")
        pdf.ln(10)

        # Add request details (in English for PDF compatibility)
        pdf.cell(0, 10, f"Owner: {request_data['owner']}", ln=True)
        pdf.cell(0, 10, f"Membership: {request_data['membership']}", ln=True)
        pdf.cell(0, 10, f"Bookings: {request_data['bookings']}", ln=True)
        pdf.cell(0, 10, f"From Date: {request_data['from_date']}", ln=True)
        pdf.cell(0, 10, f"To Date: {request_data['to_date']}", ln=True)
        pdf.cell(0, 10, f"Guests: {request_data['guests']}", ln=True)
        pdf.cell(0, 10, f"Telegram: {request_data['telegram']}", ln=True)
        pdf.cell(0, 10, f"Notes: {request_data['notes']}", ln=True)

        # Save PDF
        pdf_filename = f"request_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join("pdfs", pdf_filename)
        pdf.output(pdf_path)

        logging.info(f"PDF record generated: {pdf_path}")

    except Exception as e:
        logging.error(f"Error generating PDF: {e}")


@app.route("/pending")
def view_pending():
    """View pending requests (admin function)"""
    try:
        data = []
        if os.path.exists(PENDING_FILE):
            with open(PENDING_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
