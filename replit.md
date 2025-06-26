# Overview

This is a Flask-based hospitality request management system designed for Arabic users. The application allows users to submit hospitality requests through a web form, sends email notifications via Gmail API, and provides Telegram bot integration for request approval/rejection workflows.

# System Architecture

## Frontend Architecture
- **Framework**: HTML5 with Bootstrap 5 RTL (Right-to-Left) for Arabic language support
- **Styling**: Custom CSS with Cairo Google Font for Arabic typography
- **JavaScript**: Vanilla JavaScript for form validation, date handling, and dynamic form elements
- **UI Components**: Responsive design with Bootstrap components, Font Awesome icons, and custom RTL styling

## Backend Architecture
- **Framework**: Flask (Python web framework)
- **Server**: Gunicorn WSGI server with autoscale deployment
- **File Structure**: Modular approach with separate files for utilities, Gmail authentication, and Telegram bot functionality
- **Session Management**: Flask sessions with configurable secret key

## Authentication & External Integrations
- **Gmail Integration**: Google Gmail API with OAuth2 authentication for sending emails
- **Telegram Bot**: Python Telegram Bot library for administrative notifications and approval workflows
- **File Storage**: Local file system for PDFs, tokens, and uploads

# Key Components

## Core Flask Application (`app.py`)
- Main Flask application with route handlers
- Form submission processing and validation
- Email generation and sending via Gmail API
- File upload handling and PDF generation
- Integration with Telegram bot for notifications

## Gmail Authentication (`gmail_auth.py`)
- OAuth2 credential management for Gmail API
- Token refresh and validation
- Credential loading and error handling

## Telegram Bot (`telegram_bot.py`)
- Asynchronous Telegram bot for administrative functions
- Command handlers for `/start`, `/help`, `/pending`, `/approve`, `/reject`
- Admin-only access controls
- Integration with pending requests system

## Utilities (`utils.py`)
- Egyptian phone number validation
- HTML email template generation
- Phone number formatting functions
- Date and time utilities

## Frontend Components
- **HTML Template**: RTL Arabic form with Bootstrap styling
- **CSS Styling**: Custom Arabic typography and responsive design
- **JavaScript**: Form validation, date handling, and dynamic form fields

# Data Flow

1. **Request Submission**:
   - User fills Arabic RTL form with hospitality request details
   - Form data validated on client-side (dates, phone numbers)
   - Server-side validation and processing
   - PDF generation with request details

2. **Email Notification**:
   - HTML email template generated with Arabic content
   - Gmail API sends email to configured recipient
   - PDF attachment included with request details

3. **Telegram Integration**:
   - Bot notifies administrators of new requests
   - Admins can approve/reject via Telegram commands
   - Status updates sent back to users

4. **File Management**:
   - PDFs stored in `pdfs/` directory
   - OAuth tokens stored in `tokens/` directory
   - File uploads handled in `uploads/` directory

# External Dependencies

## Python Packages
- **Flask**: Web framework and routing
- **Google APIs**: Gmail integration (`google-api-python-client`, `google-auth`)
- **Telegram Bot**: `python-telegram-bot` for bot functionality
- **PDF Generation**: `fpdf` for creating PDF documents
- **HTTP Requests**: `requests` for external API calls
- **Server**: `gunicorn` for production deployment

## External Services
- **Gmail API**: Email sending capabilities
- **Telegram Bot API**: Administrative notifications and approvals
- **Google Fonts**: Cairo font for Arabic typography
- **Bootstrap CDN**: CSS framework and RTL support
- **Font Awesome**: Icon library

# Deployment Strategy

## Replit Configuration
- **Environment**: Python 3.11 with Nix package management
- **Packages**: OpenSSL and PostgreSQL included in Nix configuration
- **Deployment**: Autoscale deployment target with Gunicorn
- **Port**: Application runs on port 5000 with auto-reload in development

## Environment Variables
- `SESSION_SECRET`: Flask session security
- `SENDER_EMAIL`: Gmail sender account
- `RECIPIENT_EMAIL`: Request recipient email
- `TELEGRAM_BOT_TOKEN`: Telegram bot authentication

## File Structure
```
├── app.py                 # Main Flask application
├── gmail_auth.py         # Gmail API authentication
├── telegram_bot.py       # Telegram bot handlers
├── utils.py              # Utility functions
├── index.html            # Main form template
├── static/
│   ├── css/style.css     # Custom styling
│   └── js/script.js      # Client-side JavaScript
├── pdfs/                 # Generated PDF storage
├── tokens/               # OAuth token storage
└── uploads/              # File upload storage
```

# Changelog

```
Changelog:
- June 20, 2025. Initial setup
```

# User Preferences

```
Preferred communication style: Simple, everyday language.
```