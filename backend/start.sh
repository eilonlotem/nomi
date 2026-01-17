#!/bin/bash
set -e

echo "🚀 Starting Nomi backend..."

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Seed initial data (disability tags, interests)
echo "🌱 Seeding initial data..."
python manage.py seed_data

# Seed mock users (idempotent - won't create duplicates)
echo "👥 Seeding mock users..."
python manage.py seed_mock_users

echo "✅ Database setup complete!"

# Start gunicorn
echo "🌐 Starting gunicorn server on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
