# QuickReceipt – Arabic Hospitality Request System

A Flask-based web application to manage hospitality requests in Arabic (RTL), featuring Gmail API integration and Telegram bot notifications.

---

## ✨ Features

- RTL Arabic form interface (Bootstrap 5)
- Gmail API integration for automatic email delivery
- Telegram bot notifications for request handling
- Automatic PDF generation for responses
- File upload support (attachments per request)
- Egyptian phone number validation
- Dynamic form logic with conditional fields

---

## 🏗️ Project Structure

| File / Folder        | Description |
|----------------------|-------------|
| `main.py`            | App entry point |
| `app.py`             | Main Flask app |
| `gmail_auth.py`      | Gmail API authentication setup |
| `telegram_bot.py`    | Telegram bot handler |
| `utils.py`           | Utility functions |
| `templates/`         | HTML templates |
| `static/`            | CSS and JS files |
| `tokens/`            | Stores Gmail OAuth tokens (ignored in Git) |
| `pdfs/`              | Generated PDF replies |
| `uploads/`           | Uploaded files from forms |

---

## 🧪 Run Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
