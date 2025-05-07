# === Flask Configuration ===
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1


# === Database Configuration ===

DB_USERNAME=postgres
# Username used to connect to the PostgreSQL database

DB_PASSWORD=admin
# Password used for the database connection

DB_NAME=postgres
# Name of the PostgreSQL database to connect to


# === Email / SendGrid Configuration ===

SENDGRID_API_KEY="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"
# Secret API key used for authentication with SendGrid's SMTP service

MAIL_DEFAULT_SENDER=testinggreencampus@outlook.com
# Default email address used in the "From" field for outgoing application emails


# === Feature Flags / Background Tasks ===

SCHEDULER_ENABLED=False
# Enables or disables APScheduler background job execution

SCHEDULER_TEST_NOW=False
# If True, the scheduled job (e.g. discount email) runs immediately on startup

IOT_SIMULATOR_ACTIVE=False
# Enables or disables the background IoT data simulation thread
