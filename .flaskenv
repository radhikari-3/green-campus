# === Flask Configuration ===
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1


# === Database Configuration ===

DB_USERNAME=<REPLACE_ME>

DB_PASSWORD=<REPLACE_ME>

DB_NAME=<REPLACE_ME>


# === Email / SendGrid Configuration ===

# Secret API key used for authentication with SendGrid's SMTP service
SENDGRID_API_KEY=<REPLACE_ME>

# Default email address used in the "From" field for outgoing application emails
MAIL_DEFAULT_SENDER=<REPLACE_ME>


# === Feature Flags / Background Tasks ===
# Enables or disables APScheduler background job execution
SCHEDULER_ENABLED=False

# If True, the scheduled job (e.g. discount email) runs immediately on startup
SCHEDULER_TEST_NOW=False

# Enables or disables the background IoT data simulation thread
IOT_SIMULATOR_ACTIVE=False

