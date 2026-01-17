from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from profiles.models import DisabilityTag, Interest


class Command(BaseCommand):
    help: str = "Seed database with initial disability tags and interests"

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Seeding disability tags...")
        self.seed_disability_tags()

        self.stdout.write("Seeding interests...")
        self.seed_interests()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

    def seed_disability_tags(self) -> None:
        tags: list[dict[str, Any]] = [
            {
                "code": "wheelchairUser",
                "name_en": "Wheelchair User",
                "name_he": "מתנייד בכיסא גלגלים",
                "name_es": "Usuario de silla de ruedas",
                "name_fr": "Utilisateur de fauteuil roulant",
                "name_ar": "مستخدم كرسي متحرك",
                "icon": "♿",
                "order": 1,
            },
            {
                "code": "neurodivergent",
                "name_en": "Neurodivergent",
                "name_he": "נוירו-דיברגנטי",
                "name_es": "Neurodivergente",
                "name_fr": "Neurodivergent",
                "name_ar": "عصبي متباين",
                "icon": "🧠",
                "order": 2,
            },
            {
                "code": "deafHoh",
                "name_en": "Deaf/HOH",
                "name_he": "חירש/כבד שמיעה",
                "name_es": "Sordo/HH",
                "name_fr": "Sourd/Malentendant",
                "name_ar": "أصم/ضعيف السمع",
                "icon": "🦻",
                "order": 3,
            },
            {
                "code": "blindLowVision",
                "name_en": "Blind/Low Vision",
                "name_he": "עיוור/לקוי ראייה",
                "name_es": "Ciego/Baja visión",
                "name_fr": "Aveugle/Malvoyant",
                "name_ar": "أعمى/ضعيف البصر",
                "icon": "👁️",
                "order": 4,
            },
            {
                "code": "chronicIllness",
                "name_en": "Chronic Illness",
                "name_he": "מחלה כרונית",
                "name_es": "Enfermedad crónica",
                "name_fr": "Maladie chronique",
                "name_ar": "مرض مزمن",
                "icon": "💊",
                "order": 5,
            },
            {
                "code": "mentalHealth",
                "name_en": "Mental Health",
                "name_he": "בריאות נפשית",
                "name_es": "Salud mental",
                "name_fr": "Santé mentale",
                "name_ar": "الصحة النفسية",
                "icon": "💚",
                "order": 6,
            },
            {
                "code": "mobility",
                "name_en": "Mobility Difference",
                "name_he": "הבדל ניידות",
                "name_es": "Diferencia de movilidad",
                "name_fr": "Différence de mobilité",
                "name_ar": "اختلاف الحركة",
                "icon": "🚶",
                "order": 7,
            },
            {
                "code": "cognitive",
                "name_en": "Cognitive Difference",
                "name_he": "הבדל קוגניטיבי",
                "name_es": "Diferencia cognitiva",
                "name_fr": "Différence cognitive",
                "name_ar": "اختلاف معرفي",
                "icon": "💭",
                "order": 8,
            },
            {
                "code": "invisible",
                "name_en": "Invisible Disability",
                "name_he": "מוגבלות סמויה",
                "name_es": "Discapacidad invisible",
                "name_fr": "Handicap invisible",
                "name_ar": "إعاقة خفية",
                "icon": "🔮",
                "order": 9,
            },
            {
                "code": "acquired",
                "name_en": "Acquired Disability",
                "name_he": "מוגבלות נרכשת",
                "name_es": "Discapacidad adquirida",
                "name_fr": "Handicap acquis",
                "name_ar": "إعاقة مكتسبة",
                "icon": "⭐",
                "order": 10,
            },
            {
                "code": "caregiver",
                "name_en": "Caregiver/Ally",
                "name_he": "מטפל/בן ברית",
                "name_es": "Cuidador/Aliado",
                "name_fr": "Aidant/Allié",
                "name_ar": "مقدم رعاية/حليف",
                "icon": "🤝",
                "order": 11,
            },
            {
                "code": "autism",
                "name_en": "Autism",
                "name_he": "אוטיזם",
                "name_es": "Autismo",
                "name_fr": "Autisme",
                "name_ar": "التوحد",
                "icon": "♾️",
                "order": 12,
            },
        ]

        for tag_data in tags:
            DisabilityTag.objects.update_or_create(
                code=tag_data["code"], defaults=tag_data
            )

        self.stdout.write(f"  Created/updated {len(tags)} disability tags")

    def seed_interests(self) -> None:
        interests: list[dict[str, str]] = [
            # Creative
            {"name": "Photography", "icon": "📷", "category": "Creative"},
            {"name": "Art", "icon": "🎨", "category": "Creative"},
            {"name": "Music", "icon": "🎵", "category": "Creative"},
            {"name": "Writing", "icon": "✍️", "category": "Creative"},
            {"name": "Painting", "icon": "🖼️", "category": "Creative"},
            # Active
            {"name": "Yoga", "icon": "🧘", "category": "Active"},
            {"name": "Hiking", "icon": "🥾", "category": "Active"},
            {"name": "Swimming", "icon": "🏊", "category": "Active"},
            {"name": "Sports", "icon": "⚽", "category": "Active"},
            {"name": "Dancing", "icon": "💃", "category": "Active"},
            # Entertainment
            {"name": "Gaming", "icon": "🎮", "category": "Entertainment"},
            {"name": "Movies", "icon": "🎬", "category": "Entertainment"},
            {"name": "Reading", "icon": "📚", "category": "Entertainment"},
            {"name": "Sci-Fi", "icon": "🚀", "category": "Entertainment"},
            {"name": "Podcasts", "icon": "🎙️", "category": "Entertainment"},
            # Food & Drink
            {"name": "Cooking", "icon": "👨‍🍳", "category": "Food & Drink"},
            {"name": "Baking", "icon": "🧁", "category": "Food & Drink"},
            {"name": "Coffee", "icon": "☕", "category": "Food & Drink"},
            {"name": "Wine", "icon": "🍷", "category": "Food & Drink"},
            {"name": "Foodie", "icon": "🍽️", "category": "Food & Drink"},
            # Tech & Learning
            {"name": "Technology", "icon": "💻", "category": "Tech & Learning"},
            {"name": "Coding", "icon": "👨‍💻", "category": "Tech & Learning"},
            {"name": "Science", "icon": "🔬", "category": "Tech & Learning"},
            {"name": "Languages", "icon": "🗣️", "category": "Tech & Learning"},
            # Lifestyle
            {"name": "Travel", "icon": "✈️", "category": "Lifestyle"},
            {"name": "Nature", "icon": "🌿", "category": "Lifestyle"},
            {"name": "Animals", "icon": "🐾", "category": "Lifestyle"},
            {"name": "Fashion", "icon": "👗", "category": "Lifestyle"},
            {"name": "Meditation", "icon": "🧘‍♀️", "category": "Lifestyle"},
        ]

        for interest_data in interests:
            Interest.objects.update_or_create(
                name=interest_data["name"], defaults=interest_data
            )

        self.stdout.write(f"  Created/updated {len(interests)} interests")
