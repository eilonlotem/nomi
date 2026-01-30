"""
Generate painted avatar images for mock users using Google Gemini API.

Creates artistic, stylized portraits based on user profile details.

Usage:
  python manage.py generate_painted_avatars --test    # Test with 1 user
  python manage.py generate_painted_avatars           # All users
  python manage.py generate_painted_avatars --user mock_maya  # Specific user
"""
from __future__ import annotations

import base64
import os
from io import BytesIO
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image

from profiles.management.commands.seed_mock_users import MOCK_USERS, MOCK_USER_PREFIX


# Gemini API key - check env first, then settings
def get_gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "") or getattr(settings, "GEMINI_API_KEY", "")


# Mapping disability tags to visual descriptors for art generation
DISABILITY_TAG_VISUAL_HINTS: dict[str, str] = {
    "wheelchairUser": "sitting in a sleek modern wheelchair",
    "mobility": "using mobility aids with confidence",
    "blindLowVision": "with closed eyes or stylized sunglasses, serene expression",
    "deafHoh": "with visible hearing aids or cochlear implants",
    "autism": "",  # No visual representation needed
    "neurodivergent": "",  # No visual representation needed
    "chronicIllness": "",  # Invisible, no visual representation
    "invisible": "",  # Invisible disability
    "mentalHealth": "",  # No visual representation
    "cognitive": "",  # No visual representation
    "speechLanguage": "",  # No visual representation
    "acquired": "",  # No visual representation
    "caregiver": "",  # No visual representation
}

# Hair color/style variations for diversity
HAIR_STYLES: list[dict[str, str]] = [
    {"color": "dark brown", "style": "long wavy"},
    {"color": "black", "style": "short and neat"},
    {"color": "auburn", "style": "medium length curly"},
    {"color": "blonde", "style": "shoulder-length straight"},
    {"color": "dark", "style": "cropped modern"},
    {"color": "light brown", "style": "long straight"},
    {"color": "black", "style": "natural curls"},
    {"color": "reddish-brown", "style": "pixie cut"},
    {"color": "brown", "style": "styled back"},
    {"color": "dark brown", "style": "braided"},
    {"color": "black", "style": "buzz cut"},
    {"color": "caramel", "style": "flowing waves"},
    {"color": "salt and pepper", "style": "short professional"},
    {"color": "jet black", "style": "long and sleek"},
    {"color": "chestnut", "style": "messy casual"},
    {"color": "brown with highlights", "style": "layered"},
    {"color": "dark curly", "style": "natural afro"},
    {"color": "sandy blonde", "style": "textured"},
    {"color": "deep brown", "style": "slicked back"},
    {"color": "mahogany", "style": "bob cut"},
]

# Clothing style variations
CLOTHING_STYLES: list[str] = [
    "casual white t-shirt",
    "denim button-up shirt",
    "cozy knit sweater in earth tones",
    "smart casual blazer over dark top",
    "colorful patterned blouse",
    "simple black turtleneck",
    "relaxed flannel shirt",
    "elegant silk blouse",
    "sporty athletic wear",
    "bohemian flowy top",
    "classic striped shirt",
    "vibrant colored hoodie",
    "professional button-down",
    "vintage band t-shirt",
    "warm cardigan",
    "trendy crop top with jacket",
    "comfortable henley shirt",
    "artistic graphic tee",
    "sleek fitted polo",
    "casual linen shirt",
]

# Background scene variations - more diverse
SCENE_VARIATIONS: list[str] = [
    "cozy Tel Aviv cafe with exposed brick and warm string lights",
    "lush green park in Jerusalem with dappled sunlight through trees",
    "modern art gallery with white walls and abstract paintings",
    "Mediterranean beach at golden hour with soft waves",
    "rooftop bar overlooking city skyline at dusk",
    "quiet library corner with wooden bookshelves",
    "vibrant market street with colorful stalls blurred behind",
    "sleek modern office with large windows",
    "rustic vineyard with rolling hills",
    "urban graffiti wall with artistic murals",
    "peaceful botanical garden with flowers",
    "industrial loft space with exposed beams",
    "seaside promenade with palm trees",
    "mountain hiking trail with scenic view",
    "cozy home living room with warm lighting",
    "trendy coffee shop with neon signs",
    "sunny outdoor terrace with plants",
    "historic stone building courtyard",
    "minimalist studio with natural light",
    "busy city street with motion blur background",
]

# Lighting variations
LIGHTING_STYLES: list[str] = [
    "soft golden hour sunlight",
    "warm ambient indoor lighting",
    "bright natural daylight",
    "moody evening light with bokeh",
    "soft overcast diffused light",
    "dramatic side lighting",
    "backlit with rim lighting",
    "studio-quality soft box lighting",
    "candlelit warm glow",
    "cool blue hour twilight",
]


def _get_user_index(username: str) -> int:
    """Get a consistent index for a user based on their username."""
    import hashlib
    hash_val = int(hashlib.md5(username.encode()).hexdigest(), 16)
    return hash_val


def _build_realistic_prompt(user_data: dict[str, Any], style_idx: int = 0) -> str:
    """Build a detailed prompt for generating a realistic avatar photo."""
    
    username = user_data.get("username", "user")
    age = user_data.get("age", 28)
    gender = user_data.get("gender", "person")
    name = user_data.get("display_name", user_data.get("first_name", "Person"))
    bio = user_data.get("bio", "")
    city = user_data.get("city", "")
    tags = user_data.get("tags", [])
    interests = user_data.get("interests", [])
    mood = user_data.get("mood", "open")
    
    # Get consistent random-like index for this user
    user_idx = _get_user_index(username)
    
    # Gender descriptions
    gender_map = {
        "male": "man",
        "female": "woman",
        "nonbinary": "non-binary person",
        "other": "person",
    }
    gender_desc = gender_map.get(gender, "person")
    
    # Get unique appearance for this user
    hair = HAIR_STYLES[user_idx % len(HAIR_STYLES)]
    
    # Add age-appropriate hair characteristics
    hair_color = hair['color']
    if age >= 40:
        # Add some graying for older ages
        if age >= 50:
            hair_color = f"{hair['color']} with noticeable gray streaks"
        elif age >= 45:
            hair_color = f"{hair['color']} with some gray strands"
    
    hair_desc = f"{hair_color} {hair['style']} hair"
    
    clothing = CLOTHING_STYLES[user_idx % len(CLOTHING_STYLES)]
    scene = SCENE_VARIATIONS[user_idx % len(SCENE_VARIATIONS)]
    lighting = LIGHTING_STYLES[user_idx % len(LIGHTING_STYLES)]
    
    # Collect visual hints from disability tags
    visual_hints = []
    for tag in tags:
        hint = DISABILITY_TAG_VISUAL_HINTS.get(tag, "")
        if hint:
            visual_hints.append(hint)
    
    disability_visual = ", ".join(visual_hints) if visual_hints else ""
    
    # Mood to expression mapping
    mood_expressions = {
        "lowEnergy": "relaxed, calm expression with a gentle soft smile",
        "open": "warm, genuine smile with friendly approachable eyes",
        "chatty": "bright, engaging smile with lively animated expression",
        "adventurous": "confident, radiant grin with sparkle in eyes",
    }
    expression = mood_expressions.get(mood, "natural warm smile")
    
    # Skin tone variety based on user index
    skin_tones = [
        "olive Mediterranean skin tone",
        "fair skin with light freckles",
        "warm brown skin tone",
        "light tan complexion",
        "deep brown skin tone",
        "pale with rosy cheeks",
        "golden tan skin",
        "dark complexion",
        "light olive skin",
        "medium brown skin tone",
    ]
    skin_tone = skin_tones[user_idx % len(skin_tones)]
    
    # Age-specific visual characteristics
    def get_age_descriptors(age: int) -> str:
        """Get age-appropriate visual descriptors."""
        if age < 22:
            return "youthful appearance, smooth skin, very young adult features"
        elif age < 26:
            return "young adult appearance, fresh-faced, early twenties look"
        elif age < 30:
            return "mid-twenties appearance, youthful but mature features"
        elif age < 35:
            return "early thirties appearance, mature adult features, slight fine lines around eyes"
        elif age < 40:
            return "mid-thirties appearance, mature features, visible character lines"
        elif age < 45:
            return "late thirties to early forties appearance, mature features, some visible aging"
        elif age < 50:
            return "mid-forties appearance, mature features, visible age lines"
        elif age < 55:
            return "late forties to early fifties appearance, mature features, clear age signs"
        else:
            return "fifties appearance, mature features, visible aging"
    
    age_descriptors = get_age_descriptors(age)
    
    # Build the prompt with all unique elements - emphasize authentic everyday look and age
    prompt_parts = [
        f"Candid realistic photograph of a {age}-year-old Israeli {gender_desc}",
        f"appearing exactly {age} years old with {age_descriptors}",
        f"with {hair_desc} and {skin_tone}",
        f"wearing {clothing}",
    ]
    
    if disability_visual:
        prompt_parts.append(disability_visual)
    
    prompt_parts.extend([
        f"{expression}",
        f"Setting: {scene}",
        f"Lighting: {lighting}",
        f"IMPORTANT: The person must look exactly {age} years old - age-appropriate facial features, skin texture, and overall appearance",
        "Everyday person, NOT a model, natural imperfections like asymmetry and skin texture",
        "Real person you might meet on the street, authentic and relatable",
        "Upper body portrait, face clearly visible, amateur smartphone photo quality",
        "Slight imperfections, natural look, not overly polished or airbrushed",
    ])
    
    return ". ".join(prompt_parts) + "."


class Command(BaseCommand):
    help = "Generate painted avatar images for mock users using Google Gemini"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--test",
            action="store_true",
            help="Test mode: generate for first user only (Maya)",
        )
        parser.add_argument(
            "--user",
            type=str,
            help="Generate for specific user by username (e.g., mock_maya)",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing images",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=1,
            help="Number of images per user (default: 1)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print prompts without generating images",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        api_key = get_gemini_api_key()
        dry_run = options.get("dry_run", False)
        
        if not api_key and not dry_run:
            self.stderr.write(
                self.style.ERROR("GEMINI_API_KEY is not set. Add it to your .env file or environment.")
            )
            self.stderr.write("Use --dry-run to see the prompts without generating images.")
            return

        # Filter users based on options
        users_to_process = MOCK_USERS
        
        if options.get("test"):
            users_to_process = MOCK_USERS[:1]  # Just Maya
            self.stdout.write(self.style.WARNING("🧪 Test mode: Processing first user only"))
        elif options.get("user"):
            target_user = options["user"]
            users_to_process = [u for u in MOCK_USERS if u["username"] == target_user]
            if not users_to_process:
                self.stderr.write(self.style.ERROR(f"User '{target_user}' not found"))
                return
        
        self.stdout.write(f"🎨 Generating painted avatars for {len(users_to_process)} user(s)...")
        self.stdout.write(f"   Using Gemini API for image generation")
        
        # Setup output directory
        base_dir = Path(settings.BASE_DIR) / "static" / "painted_avatars"
        base_dir.mkdir(parents=True, exist_ok=True)
        
        count = options.get("count", 1)
        overwrite = options.get("overwrite", False)
        
        for user_data in users_to_process:
            username = user_data["username"]
            display_name = user_data.get("display_name", username)
            
            self.stdout.write(f"\n👤 Processing: {display_name} ({username})")
            
            user_dir = base_dir / username
            user_dir.mkdir(parents=True, exist_ok=True)
            
            for idx in range(count):
                out_path = user_dir / f"avatar_{idx + 1}.png"
                
                if out_path.exists() and not overwrite:
                    self.stdout.write(f"   ⏭️  Skipping (exists): {out_path.name}")
                    continue
                
                # Build prompt
                prompt = _build_realistic_prompt(user_data, style_idx=idx)
                
                if dry_run:
                    self.stdout.write(f"\n📝 Prompt for {display_name}:")
                    self.stdout.write(f"   {prompt}\n")
                    continue
                
                # Generate image using Gemini
                self.stdout.write(f"   🖌️  Generating avatar {idx + 1}...")
                
                try:
                    from google import genai
                    from google.genai import types
                    
                    client = genai.Client(api_key=api_key)
                    
                    # Use Gemini 2.0 Flash Exp for image generation
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-exp-image-generation",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_modalities=["IMAGE", "TEXT"],
                        ),
                    )
                    
                    # Extract image from response
                    image_saved = False
                    if response.candidates and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if candidate.content and candidate.content.parts:
                            for part in candidate.content.parts:
                                if part.inline_data is not None and part.inline_data.data:
                                    image_bytes = part.inline_data.data
                                    
                                    # Resize and compress the image
                                    try:
                                        # Open image from bytes
                                        img = Image.open(BytesIO(image_bytes))
                                        
                                        # Resize to 320x320 with crop focusing on upper portion (face area)
                                        # Get original dimensions
                                        orig_width, orig_height = img.size
                                        
                                        # Calculate aspect ratio
                                        aspect_ratio = orig_width / orig_height
                                        
                                        if aspect_ratio < 1.0:  # Portrait (taller than wide)
                                            # Resize to fit width, then crop height from bottom to focus on face
                                            new_width = 320
                                            new_height = int(orig_height * (320 / orig_width))
                                            img_temp = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                            # Crop from top, cutting off bottom portion
                                            img_resized = img_temp.crop((0, 0, 320, 320))
                                        elif aspect_ratio > 1.0:  # Landscape (wider than tall)
                                            # Crop to square focusing on upper-center portion
                                            crop_size = min(orig_width, orig_height)
                                            left = (orig_width - crop_size) // 2
                                            # Shift crop upward to focus on face (top 30% of image)
                                            top = max(0, int((orig_height - crop_size) * 0.3))
                                            right = left + crop_size
                                            bottom = top + crop_size
                                            img_cropped = img.crop((left, top, right, bottom))
                                            img_resized = img_cropped.resize((320, 320), Image.Resampling.LANCZOS)
                                        else:  # Square
                                            # Resize normally for square images
                                            img_resized = img.resize((320, 320), Image.Resampling.LANCZOS)
                                        
                                        # Save with compression
                                        # Optimize=True reduces file size, quality=85 is a good balance
                                        output = BytesIO()
                                        img_resized.save(output, format='PNG', optimize=True, compress_level=6)
                                        optimized_bytes = output.getvalue()
                                        
                                        # Write optimized image
                                        out_path.write_bytes(optimized_bytes)
                                        
                                        # Show file size reduction
                                        original_size = len(image_bytes) / 1024  # KB
                                        optimized_size = len(optimized_bytes) / 1024  # KB
                                        reduction = ((original_size - optimized_size) / original_size) * 100
                                        
                                        self.stdout.write(
                                            self.style.SUCCESS(
                                                f"   ✅ Generated: {out_path} "
                                                f"({optimized_size:.1f}KB, {reduction:.0f}% reduction)"
                                            )
                                        )
                                        image_saved = True
                                    except Exception as resize_error:
                                        # Fallback: save original if resize fails
                                        self.stdout.write(
                                            self.style.WARNING(
                                                f"   ⚠️  Resize failed, saving original: {resize_error}"
                                            )
                                        )
                                        out_path.write_bytes(image_bytes)
                                        image_saved = True
                                    break
                    
                    if not image_saved:
                        self.stderr.write(
                            self.style.WARNING(f"   ⚠️  No image in response")
                        )
                    
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(f"   ❌ Error generating image: {e}")
                    )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(f"\n🎉 Done! Images saved to: {base_dir}")
            )
