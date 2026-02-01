#!/bin/bash
# Regenerate AI avatars for the 20 new mock users with improved age and disability accuracy

echo "🎨 Regenerating AI avatars for 20 new mock users with improved prompts..."
echo "⚠️  This will overwrite existing avatars to better show age and disabilities"
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

# Regenerate avatar for each new user with overwrite
for user in "${NEW_USERS[@]}"; do
    echo "Regenerating avatar for: $user"
    python manage.py generate_painted_avatars --user "$user" --overwrite
    echo ""
done

echo "✅ Done! All avatars regenerated with improved age and disability accuracy."
