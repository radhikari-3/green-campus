# === Flask Configuration ===

FLASK_APP=run.py               # Entry point for the Flask application
FLASK_ENV=development          # Environment mode: use 'production' for deployment
FLASK_DEBUG=1                  # Enables debug mode (auto-reload, detailed error pages)


# === Database Configuration ===

DB_USERNAME=postgres           # Database username for connecting to PostgreSQL
DB_PASSWORD=admin              # Password for the PostgreSQL user
DB_NAME=postgres               # Name of the target PostgreSQL database


# === Email / SendGrid Configuration ===

SENDGRID_API_KEY="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"
# API key for authenticating with the SendGrid email delivery service

MAIL_DEFAULT_SENDER=testinggreencampus@outlook.com
# Default sender address for all outgoing emails
