# === Flask Configuration ===
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1


# === Database Configuration ===

DB_USERNAME=local

DB_PASSWORD=admin

DB_NAME=postgres


# === Email / SendGrid Configuration ===

# Secret API key used for authentication with SendGrid's SMTP service
SENDGRID_API_KEY="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"

# Default email address used in the "From" field for outgoing application emails
MAIL_DEFAULT_SENDER=testinggreencampus@outlook.com


# === Feature Flags / Background Tasks ===
# Enables or disables APScheduler background job execution
SCHEDULER_ENABLED=False

# If True, the scheduled job (e.g. discount email) runs immediately on startup
SCHEDULER_TEST_NOW=False

# Enables or disables the background IoT data simulation thread
IOT_SIMULATOR_ACTIVE=False

