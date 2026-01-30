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
            # Functional / everyday description
            {
                "code": "difficultySeeing",
                "name_en": "Difficulty seeing",
                "name_he": "מתקשה לראות",
                "name_es": "Me cuesta ver",
                "name_fr": "J'ai du mal à voir",
                "name_ar": "أجد صعوبة في الرؤية",
                "icon": "👁️",
                "category": "vision",
                "disclosure_level": "functional",
                "order": 1,
            },
            {
                "code": "partialVision",
                "name_en": "Partial vision",
                "name_he": "רואה באופן חלקי",
                "name_es": "Veo parcialmente",
                "name_fr": "Je vois partiellement",
                "name_ar": "أرى بشكل جزئي",
                "icon": "👓",
                "category": "vision",
                "disclosure_level": "functional",
                "order": 2,
            },
            {
                "code": "visionAids",
                "name_en": "Use vision aids",
                "name_he": "נעזר/ת בעזרים לראייה",
                "name_es": "Uso ayudas para la visión",
                "name_fr": "J'utilise des aides visuelles",
                "name_ar": "أستخدم أدوات مساعدة للرؤية",
                "icon": "🦯",
                "category": "vision",
                "disclosure_level": "functional",
                "order": 3,
            },
            {
                "code": "lightSensitivity",
                "name_en": "Light sensitivity",
                "name_he": "רגישות לאור",
                "name_es": "Sensibilidad a la luz",
                "name_fr": "Sensibilité à la lumière",
                "name_ar": "حساسية للضوء",
                "icon": "🌞",
                "category": "vision",
                "disclosure_level": "functional",
                "order": 4,
            },
            {
                "code": "difficultyHearing",
                "name_en": "Difficulty hearing",
                "name_he": "מתקשה לשמוע",
                "name_es": "Me cuesta oír",
                "name_fr": "J'ai du mal à entendre",
                "name_ar": "أجد صعوبة في السمع",
                "icon": "🦻",
                "category": "hearing",
                "disclosure_level": "functional",
                "order": 5,
            },
            {
                "code": "partialHearing",
                "name_en": "Partial hearing",
                "name_he": "שומע/ת באופן חלקי",
                "name_es": "Oigo parcialmente",
                "name_fr": "J'entends partiellement",
                "name_ar": "أسمع بشكل جزئي",
                "icon": "👂",
                "category": "hearing",
                "disclosure_level": "functional",
                "order": 6,
            },
            {
                "code": "hearingAids",
                "name_en": "Use hearing aids",
                "name_he": "נעזר/ת בעזרים לשמיעה",
                "name_es": "Uso ayudas auditivas",
                "name_fr": "J'utilise des aides auditives",
                "name_ar": "أستخدم أجهزة مساعدة للسمع",
                "icon": "🎧",
                "category": "hearing",
                "disclosure_level": "functional",
                "order": 7,
            },
            {
                "code": "noisyConversations",
                "name_en": "Hard to follow group conversations",
                "name_he": "מתקשה בשיחות עם הרבה אנשים",
                "name_es": "Me cuesta seguir conversaciones con mucha gente",
                "name_fr": "J'ai du mal à suivre les conversations en groupe",
                "name_ar": "أجد صعوبة في محادثات مع كثير من الأشخاص",
                "icon": "💬",
                "category": "hearing",
                "disclosure_level": "functional",
                "order": 8,
            },
            {
                "code": "mobilityDifficulty",
                "name_en": "Mobility challenges",
                "name_he": "קושי בהתניידות",
                "name_es": "Dificultad para moverme",
                "name_fr": "Difficultés de mobilité",
                "name_ar": "صعوبة في الحركة",
                "icon": "🚶",
                "category": "mobility",
                "disclosure_level": "functional",
                "order": 9,
            },
            {
                "code": "wheelchairUser",
                "name_en": "Wheelchair user",
                "name_he": "מתנייד/ת בכיסא גלגלים",
                "name_es": "Usuario/a de silla de ruedas",
                "name_fr": "Utilisateur/trice de fauteuil roulant",
                "name_ar": "مستخدم/ة كرسي متحرك",
                "icon": "♿",
                "category": "mobility",
                "disclosure_level": "functional",
                "order": 10,
            },
            {
                "code": "shortDistances",
                "name_en": "Can walk short distances",
                "name_he": "הולך/ת למרחקים קצרים",
                "name_es": "Camino distancias cortas",
                "name_fr": "Je marche sur de courtes distances",
                "name_ar": "أمشي لمسافات قصيرة",
                "icon": "👣",
                "category": "mobility",
                "disclosure_level": "functional",
                "order": 11,
            },
            {
                "code": "needsAccessibility",
                "name_en": "Need physical accommodations",
                "name_he": "זקוק/ה להתאמות פיזיות",
                "name_es": "Necesito adaptaciones físicas",
                "name_fr": "J'ai besoin d'aménagements physiques",
                "name_ar": "أحتاج إلى تكييفات جسدية",
                "icon": "🧩",
                "category": "mobility",
                "disclosure_level": "functional",
                "order": 12,
            },
            {
                "code": "speechDifficulty",
                "name_en": "Speech difficulties",
                "name_he": "קושי בדיבור",
                "name_es": "Dificultad para hablar",
                "name_fr": "Difficultés d'élocution",
                "name_ar": "صعوبة في الكلام",
                "icon": "🗣️",
                "category": "communication",
                "disclosure_level": "functional",
                "order": 13,
            },
            {
                "code": "alternativeCommunication",
                "name_en": "Use alternative communication",
                "name_he": "מתקשר/ת בדרכים חלופיות",
                "name_es": "Me comunico de formas alternativas",
                "name_fr": "J'utilise des moyens de communication alternatifs",
                "name_ar": "أتواصل بطرق بديلة",
                "icon": "🤟",
                "category": "communication",
                "disclosure_level": "functional",
                "order": 14,
            },
            {
                "code": "needsTimeToSpeak",
                "name_en": "Need extra time to express myself",
                "name_he": "צריך/ה זמן להתנסח",
                "name_es": "Necesito tiempo para expresarme",
                "name_fr": "J'ai besoin de temps pour m'exprimer",
                "name_ar": "أحتاج وقتاً للتعبير",
                "icon": "⏳",
                "category": "communication",
                "disclosure_level": "functional",
                "order": 15,
            },
            {
                "code": "processingDifficulty",
                "name_en": "Info processing challenges",
                "name_he": "קושי בעיבוד מידע",
                "name_es": "Dificultad para procesar información",
                "name_fr": "Difficultés de traitement de l'information",
                "name_ar": "صعوبة في معالجة المعلومات",
                "icon": "🧠",
                "category": "cognitive_emotional",
                "disclosure_level": "functional",
                "order": 16,
            },
            {
                "code": "sensoryOverload",
                "name_en": "Sensitive to overload/stimuli",
                "name_he": "רגישות לעומס או גירויים",
                "name_es": "Sensibilidad a la sobrecarga o estímulos",
                "name_fr": "Sensibilité à la surcharge ou aux stimuli",
                "name_ar": "حساسية للضغط أو المثيرات",
                "icon": "🌊",
                "category": "cognitive_emotional",
                "disclosure_level": "functional",
                "order": 17,
            },
            {
                "code": "slowClearPace",
                "name_en": "Need a slow, clear pace",
                "name_he": "זקוק/ה לקצב איטי וברור",
                "name_es": "Necesito un ritmo lento y claro",
                "name_fr": "J'ai besoin d'un rythme lent et clair",
                "name_ar": "أحتاج إلى وتيرة بطيئة وواضحة",
                "icon": "🐢",
                "category": "cognitive_emotional",
                "disclosure_level": "functional",
                "order": 18,
            },
            {
                "code": "calmSafeSpace",
                "name_en": "Need a calm, safe space",
                "name_he": "צריך/ה מרחב רגוע ובטוח",
                "name_es": "Necesito un espacio tranquilo y seguro",
                "name_fr": "J'ai besoin d'un espace calme et sûr",
                "name_ar": "أحتاج إلى مساحة هادئة وآمنة",
                "icon": "🌿",
                "category": "cognitive_emotional",
                "disclosure_level": "functional",
                "order": 19,
            },
        ]

        for tag_data in tags:
            DisabilityTag.objects.update_or_create(
                code=tag_data["code"], defaults=tag_data
            )

        DisabilityTag.objects.exclude(code__in=[tag["code"] for tag in tags]).update(
            is_active=False
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
