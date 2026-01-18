#!/bin/bash
set -e

echo "🚀 Starting Nomi backend..."

# Run tests
echo "🧪 Running tests..."
python manage.py test matching --verbosity=1
echo "✅ Tests passed!"

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Seed initial data (disability tags, interests)
echo "🌱 Seeding initial data..."
python manage.py seed_data

# Seed mock users (idempotent - won't create duplicates)
echo "👥 Seeding mock users..."
python manage.py seed_mock_users

# Skip mock matches - matches are created through the real swipe flow

echo "👤 Creating admin user..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='nomi_admin').exists():
    User.objects.create_superuser('nomi_admin', 'admin@nomi.app', 'admin123')
    print('  ➕ Created admin user')
else:
    u = User.objects.get(username='nomi_admin')
    u.set_password('admin123')
    u.is_staff = True
    u.is_superuser = True
    u.is_active = True
    u.save()
    print('  🔄 Reset admin password')
"

echo "✅ Database setup complete!"

# Start gunicorn
echo "🌐 Starting gunicorn server on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --log-file -
