#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
echo "Attempting to connect to: $SQLALCHEMY_DATABASE_URI"

# Add more verbose output to the connection attempts
until PGPASSWORD=farmtasks psql -h localhost -U farmtasks -d farmtasks_db -p 5433 -c '\l' 2>/dev/null; do
  echo "`date` - Still waiting for postgres... (db host: localhost, user: farmtasks, database: farmtasks_db)"
  sleep 2
done

echo "PostgreSQL is up - executing command"

# Test database connection
echo "Testing database connection..."
PGPASSWORD=farmtasks psql -h localhost -U farmtasks -d farmtasks_db -p 5433 -c "SELECT 1" || {
    echo "Failed to execute test query"
    exit 1
}

# Initialize database with error handling
echo "Initializing database..."
if python -m app.init_db; then
    echo "Database initialization successful"
else
    echo "Database initialization failed"
    exit 1
fi

# Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:5000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    "run:app" 