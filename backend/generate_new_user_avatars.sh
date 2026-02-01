#!/bin/bash
# Generate AI avatars for the 20 new mock users (mock_dror through mock_nir)

echo "🎨 Generating AI avatars for 20 new mock users..."
echo "⚠️  Make sure GEMINI_API_KEY is set in your .env file"
echo ""

# List of the 20 new users
NEW_USERS=(
    "mock_dror"
    "mock_neta"
    "mock_itai"
    "mock_hila"
    "mock_yuval"
    "mock_sarit"
    "mock_asaf"
    "mock_ruti"
    "mock_adi"
    "mock_omri"
    "mock_dana"
    "mock_shai"
    "mock_shani"
    "mock_lior"
    "mock_gal"
    "mock_uri"
    "mock_maya2"
    "mock_barak"
    "mock_chen"
    "mock_nir"
)

# Activate virtual environment
source venv/bin/activate

# Generate avatar for each new user
for user in "${NEW_USERS[@]}"; do
    echo "Generating avatar for: $user"
    python manage.py generate_painted_avatars --user "$user"
    echo ""
done

echo "✅ Done! All avatars generated."
