# Generating AI Avatars for New Mock Users

This document explains how to generate AI-powered avatar images for the 20 new mock users (users 21-40).

## Prerequisites

You need a **Google Gemini API key** to generate images. Get one from:
https://aistudio.google.com/app/apikey

## Setup

1. Add your Gemini API key to the backend `.env` file:

```bash
cd backend
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

Or manually edit `backend/.env` and add:
```
GEMINI_API_KEY=your_api_key_here
```

## Generate All New User Avatars (Recommended)

Run the provided bash script to generate avatars for all 20 new users at once:

```bash
cd backend
./generate_new_user_avatars.sh
```

This will generate one avatar image for each of these users:
- mock_dror (Dror - speech disorder, music teacher)
- mock_neta (Neta - wheelchair athlete)
- mock_itai (Itai - OCD advocate)
- mock_hila (Hila - epilepsy warrior)
- mock_yuval (Yuval - dyspraxia advocate)
- mock_sarit (Sarit - MS warrior)
- mock_asaf (Asaf - prosthetic leg athlete)
- mock_ruti (Ruti - Crohn's disease)
- mock_adi (Adi - bipolar advocate)
- mock_omri (Omri - Tourette's syndrome)
- mock_dana (Dana - fibromyalgia advocate)
- mock_shai (Shai - visual processing disorder)
- mock_shani (Shani - colostomy bag user)
- mock_lior (Lior - schizophrenia advocate)
- mock_gal (Gal - spinal injury)
- mock_uri (Uri - hearing aids user)
- mock_maya2 (Maya - eating disorder recovery)
- mock_barak (Barak - low vision artist)
- mock_chen (Chen - sensory processing disorder)
- mock_nir (Nir - ALS early stage)

## Generate Individual User Avatars

To generate an avatar for a specific user:

```bash
cd backend
source venv/bin/activate
python manage.py generate_painted_avatars --user mock_dror
```

Replace `mock_dror` with any username.

## Generate Multiple Images per User

To generate multiple avatar variations per user:

```bash
python manage.py generate_painted_avatars --user mock_dror --count 3
```

## Test First (Dry Run)

To see the prompts without generating images:

```bash
python manage.py generate_painted_avatars --user mock_dror --dry-run
```

## Output

Generated images are saved to:
```
backend/static/painted_avatars/{username}/avatar_1.png
```

The images are automatically:
- Resized to 320x320 pixels
- Optimized for file size (typically 60-80% reduction)
- Cropped to focus on the face area
- Styled as realistic, candid photographs

## Troubleshooting

### "GEMINI_API_KEY is not set"
Add the API key to your `.env` file as described above.

### Images look wrong
Try regenerating with the `--overwrite` flag:
```bash
python manage.py generate_painted_avatars --user mock_dror --overwrite
```

### Generation fails
Check your API quota at: https://aistudio.google.com/

## What's Generated

The AI creates realistic portrait photos based on:
- Age-appropriate facial features
- Gender and appearance details
- Disability characteristics (when visible)
- Hebrew cultural context
- Israeli settings and backgrounds
- Authentic, non-model-like appearance
- Natural lighting and casual photography style
