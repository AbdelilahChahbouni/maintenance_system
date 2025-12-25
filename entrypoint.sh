#!/bin/bash
set -e

# Initialize migrations folder if it doesn't exist
if [ ! -d "migrations" ]; then
    echo "Initializing migrations..."
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
else
    echo "Running migrations..."
    flask db upgrade
fi

# Create admin user
echo "Creating/Checking admin user..."
python create_admin.py

# Start the application with Gunicorn
echo "Starting Flask app with Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 run:app
