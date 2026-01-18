"""
Generate mock profile images using the OpenAI API and save them to the repo.

Usage:
  python manage.py generate_mock_profile_images --count 3 --overwrite
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from profiles.management.commands.seed_mock_users import MOCK_USERS, MOCK_USER_PREFIX


DISABILITY_TAG_TO_DESC: dict[str, str] = {
    "wheelchairUser": "wheelchair user",
    "blind": "blind person",
    "deaf": "deaf person",
    "autism": "autistic person",
    "neurodivergent": "neurodivergent person",
    "chronicIllness": "person living with chronic illness",
    "adhd": "person with ADHD",
    "anxiety": "person with anxiety",
    "depression": "person living with depression",
}

SCENE_VARIATIONS: list[str] = [
    "outdoor portrait in natural light, soft background bokeh",
    "casual indoor portrait in a cozy cafe, warm lighting",
    "lifestyle portrait in a park, golden hour light",
]


def _make_seed(username: str, offset: int = 0) -> int:
    digest = hashlib.sha256(username.encode("utf-8")).hexdigest()
    base = int(digest[:8], 16)
    return base + offset


def _build_prompt(user_data: dict[str, Any], scene_hint: str) -> str:
    age = user_data.get("age", 28)
    gender = user_data.get("gender", "person")
    tags = user_data.get("tags", [])
    disability_descs = [DISABILITY_TAG_TO_DESC.get(t) for t in tags if t in DISABILITY_TAG_TO_DESC]
    disability_phrase = ""
    if disability_descs:
        disability_phrase = " and ".join(disability_descs)
    else:
        disability_phrase = "person with a visible unique style"

    return (
        f"Photorealistic portrait of a {age}-year-old {gender} {disability_phrase}. "
        f"{scene_hint}. "
        "Same person across all images in this set, consistent facial features and hair. "
        "Modern, friendly, approachable, authentic. "
        "High quality, realistic skin texture, natural lighting, DSLR look."
    )


class Command(BaseCommand):
    help = "Generate mock profile images with OpenAI and store them in the repo."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--count", type=int, default=3, help="Images per profile")
        parser.add_argument("--overwrite", action="store_true", help="Overwrite existing images")

    def handle(self, *args: Any, **options: Any) -> None:
        api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
        if not api_key:
            self.stderr.write("OPENAI_API_KEY is not set. Add it to your environment.")
            return

        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        base_dir = Path(settings.BASE_DIR) / "static" / "mock_profiles"
        base_dir.mkdir(parents=True, exist_ok=True)

        count: int = int(options["count"])
        overwrite: bool = bool(options["overwrite"])

        for user_data in MOCK_USERS:
            username = user_data["username"]
            if not username.startswith(MOCK_USER_PREFIX):
                continue
            user_dir = base_dir / username
            user_dir.mkdir(parents=True, exist_ok=True)

            for idx in range(count):
                out_path = user_dir / f"{idx + 1}.png"
                if out_path.exists() and not overwrite:
                    continue

                scene_hint = SCENE_VARIATIONS[idx % len(SCENE_VARIATIONS)]
                prompt = _build_prompt(user_data, scene_hint)
                seed = _make_seed(username, idx)

                result = client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                    seed=seed,
                    response_format="b64_json",
                )

                b64 = result.data[0].b64_json
                image_bytes = base64.b64decode(b64)
                out_path.write_bytes(image_bytes)

                self.stdout.write(f"Generated {out_path}")
