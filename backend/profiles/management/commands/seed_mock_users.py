"""
Management command to seed mock users for the application.
This command is idempotent - running it multiple times won't create duplicates.
Usage: python manage.py seed_mock_users

Run on every deploy to ensure mock users exist.
"""
from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.authtoken.models import Token

from profiles.models import Profile, ProfilePhoto, DisabilityTag, Interest, LookingFor


User = get_user_model()

# Unique identifier prefix for mock users - used to identify and protect them
MOCK_USER_PREFIX = "mock_"


def get_local_avatar_url(username: str) -> str | None:
    """
    Get the URL for a locally generated avatar if it exists.
    Returns None if no local avatar is available.
    Always returns absolute URL when BACKEND_URL is set, otherwise relative URL.
    """
    avatar_path = Path(settings.BASE_DIR) / "static" / "painted_avatars" / username / "avatar_1.png"
    if avatar_path.exists():
        # Get the backend URL from environment
        backend_url = os.getenv("BACKEND_URL", "").rstrip("/")
        if backend_url:
            # Return absolute URL
            return f"{backend_url}/static/painted_avatars/{username}/avatar_1.png"
        # For local development, return relative URL
        # Frontend will prepend the backend URL from API_URL env var
        return f"/static/painted_avatars/{username}/avatar_1.png"
    return None

# Mock users data - these are immutable seed users
# All 40 profiles are from Israel with diverse cities, backgrounds, and accessibility needs
# Profile content is in Hebrew
MOCK_USERS: list[dict[str, Any]] = [
    # 1. Maya - Tel Aviv, wheelchair user
    {
        "username": f"{MOCK_USER_PREFIX}maya",
        "email": "maya@nomi.app",
        "first_name": "מאיה",
        "last_name": "כהן",
        "display_name": "מאיה",
        "gender": "female",
        "age": 28,
        "bio": "משתמשת בכיסא גלגלים שאוהבת יוגה מותאמת וצילום. מחפשת חיבורים אמיתיים ומישהו שמעריך את הרגעים הקטנים בחיים.",
        "tags": ["wheelchairUser", "needsAccessibility"],
        "interests": ["Photography", "Yoga", "Art", "Travel", "Coffee"],
        "mood": "open",
        "prompt_id": "laughMost",
        "prompt_answer": "כשהחתול שלי שופט את בחירות החיים שלי מהצד השני של החדר",
        "picture_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=600&fit=crop",
        "additional_photos": [
            "https://images.unsplash.com/photo-1524250502761-1ac6f2e30d43?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=400&h=600&fit=crop",
        ],
        "city": "תל אביב",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 25,
        "looking_for_max_age": 35,
        "looking_for_max_distance": 30,
        "looking_for_location": "תל אביב",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "כיסא הגלגלים שלי הוא בעצם יצירת אמנות - צבעתי אותו בעצמי בנושא גלקסיה!",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
    },
    # 2. Daniel - Jerusalem, deaf artist
    {
        "username": f"{MOCK_USER_PREFIX}daniel",
        "email": "daniel@nomi.app",
        "first_name": "דניאל",
        "last_name": "לוי",
        "display_name": "דניאל",
        "gender": "male",
        "age": 32,
        "bio": "אמן חרש וחובב קפה. אני מתקשר בשפת הסימנים ואוהב להכיר אנשים חדשים שהם סבלניים וסקרנים.",
        "tags": ["difficultyHearing", "partialHearing", "processingDifficulty"],
        "interests": ["Art", "Coffee", "Movies", "Cooking", "Gaming"],
        "mood": "chatty",
        "prompt_id": "perfectSunday",
        "prompt_answer": "סיור גלריות בבוקר, ואז ציור בבית קפה שקט",
        "picture_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop",
        "city": "ירושלים",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 26,
        "looking_for_max_age": 38,
        "looking_for_max_distance": 40,
        "looking_for_location": "ירושלים",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני שם לב לפרטים ויזואליים שאחרים מפספסים - זה הופך אותי לאמן טוב יותר ולצופה אנשים מצוין!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
    },
    # 3. Noa - Haifa, neurodivergent tech
    {
        "username": f"{MOCK_USER_PREFIX}noa",
        "email": "noa@nomi.app",
        "first_name": "נועה",
        "last_name": "בן-דוד",
        "display_name": "נועה",
        "gender": "female",
        "age": 26,
        "bio": "נוירו-מגוונת וחובבת טכנולוגיה. אני מעריכה סבלנות, הבנה ושיחות עמוקות על כל מה שקשור למדע בדיוני.",
        "tags": ["processingDifficulty", "sensoryOverload", "slowClearPace"],
        "interests": ["Gaming", "Coding", "Sci-Fi", "Music", "Reading"],
        "mood": "lowEnergy",
        "prompt_id": "convinced",
        "prompt_answer": "רובוטים יעריכו בסוף ממים טובים",
        "picture_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=500&fit=crop",
        "city": "חיפה",
        "looking_for_genders": ["everyone"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 34,
        "looking_for_max_distance": 50,
        "looking_for_location": "חיפה",
        "relationship_types": ["friends", "casual"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "סמול טוק באמת מתיש אותי, אבל שיחות עמוקות על תחומי עניין? אני יכולה לדבר שעות!",
        "preferred_times": ["night", "evening"],
        "response_pace": "variable",
    },
    # 4. Alex - Tel Aviv, chronic illness advocate
    {
        "username": f"{MOCK_USER_PREFIX}alex",
        "email": "alex@nomi.app",
        "first_name": "אלכס",
        "last_name": "שפירא",
        "display_name": "אלכס",
        "gender": "male",
        "age": 30,
        "bio": "חי/ה עם מחלה כרונית. פעיל/ה למען זכויות אנשים עם מוגבלות ונגישות. אוהב/ת הליכות בטבע (בקצב שלי) ושיחות משמעותיות.",
        "tags": ["needsAccessibility", "calmSafeSpace"],
        "interests": ["Writing", "Podcasts", "Nature", "Photography", "Meditation"],
        "mood": "adventurous",
        "prompt_id": "custom",
        "prompt_answer": "הפודקאסטים שלי, מצלמה וטיולים בטבע - גם בימים הקשים",
        "picture_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=500&fit=crop",
        "city": "תל אביב",
        "looking_for_genders": ["everyone"],
        "looking_for_min_age": 24,
        "looking_for_max_age": 38,
        "looking_for_max_distance": 50,
        "looking_for_location": "תל אביב",
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "dontLetStop",
        "ask_me_answer": "לחקור מקומות יפים - אני פשוט לוקח/ת חטיפים נוספים ומתכנן/ת עצירות למנוחה!",
        "preferred_times": ["flexible"],
        "response_pace": "variable",
        "time_notes": "האנרגיה שלי משתנה מיום ליום, אז אני מעריך/ה גמישות!",
    },
    # 5. Shira - Rishon LeZion, mental health advocate
    {
        "username": f"{MOCK_USER_PREFIX}shira",
        "email": "shira@nomi.app",
        "first_name": "שירה",
        "last_name": "גולדשטיין",
        "display_name": "שירה",
        "gender": "female",
        "age": 29,
        "bio": "פעילה למען בריאות הנפש ומטפלת גאה. מאמינה בטיפול עצמי, חיבורים אמיתיים וכוח הריפוי של טיול טוב בכרמל.",
        "tags": ["calmSafeSpace", "sensoryOverload"],
        "interests": ["Meditation", "Reading", "Hiking", "Cooking", "Yoga"],
        "mood": "open",
        "prompt_id": "perfectSunday",
        "prompt_answer": "בוקר איטי עם קפה טורקי, ספר טוב והליכה לחוף אחר הצהריים",
        "picture_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=600&fit=crop",
        "additional_photos": [
            "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=400&h=600&fit=crop",
        ],
        "city": "ראשון לציון",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 27,
        "looking_for_max_age": 37,
        "looking_for_max_distance": 40,
        "looking_for_location": "ראשון לציון",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "התמיכה וההבנה הבלתי מותנית - אנחנו באמת מבינים אחד את השני!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "moderate",
    },
    # 6. Yossi - Tel Aviv, tech entrepreneur
    {
        "username": f"{MOCK_USER_PREFIX}yossi",
        "email": "yossi@nomi.app",
        "first_name": "יוסי",
        "last_name": "כץ",
        "display_name": "יוסי",
        "gender": "male",
        "age": 35,
        "bio": "עם הבדל בניידות מילדות. יזם טכנולוגי ביום, שף חובב בלילה. מחפש מישהי שאוהבת אוכל טוב וחברה עוד יותר טובה.",
        "tags": ["mobilityDifficulty", "needsAccessibility"],
        "interests": ["Cooking", "Technology", "Travel", "Wine", "Movies"],
        "mood": "chatty",
        "prompt_id": "convinced",
        "prompt_answer": "הארוחות הכי טובות הן אלה שמשתפים עם מישהו מיוחד",
        "picture_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=600&fit=crop",
        "additional_photos": [
            "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=600&fit=crop",
        ],
        "city": "תל אביב",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 28,
        "looking_for_max_age": 40,
        "looking_for_max_distance": 30,
        "looking_for_location": "תל אביב",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "בניית הסטארטאפ שלי מאפס - מסתבר שהתאמה היא מיומנות מצוינת ליזמות!",
        "preferred_times": ["evening", "night"],
        "response_pace": "quick",
    },
    # 7. Tamar - Herzliya, blind music lover
    {
        "username": f"{MOCK_USER_PREFIX}tamar",
        "email": "tamar@nomi.app",
        "first_name": "תמר",
        "last_name": "אזולאי",
        "display_name": "תמר",
        "gender": "female",
        "age": 27,
        "bio": "עיוורת מלידה, אבל אני רואה את העולם בדרך יפה משלי. אוהבת מוזיקה, מכורה לפודקאסטים ומומחית לחיבוקים. במקור מרמת גן.",
        "tags": ["difficultySeeing", "partialVision"],
        "interests": ["Music", "Podcasts", "Dancing", "Swimming", "Languages"],
        "mood": "adventurous",
        "prompt_id": "custom",
        "prompt_answer": "אני יודעת לזהות כל שיר אחרי 3 שניות - גם אם זה מ-1987",
        "picture_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=500&fit=crop",
        "city": "הרצליה",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 25,
        "looking_for_max_age": 35,
        "looking_for_max_distance": 40,
        "looking_for_location": "הרצליה",
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני שומעת דברים שאחרים מפספסים - מעולה לציתות... כלומר, להערכת מוזיקה! 😄",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "quick",
    },
    # 8. Amit - Tel Aviv, autistic developer
    {
        "username": f"{MOCK_USER_PREFIX}amit",
        "email": "amit@nomi.app",
        "first_name": "עמית",
        "last_name": "רוזן",
        "display_name": "עמית",
        "gender": "male",
        "age": 31,
        "bio": "אוטיסט וגאה. מפתח תוכנה שמדבר סרקזם ופייתון שוטף. מחפש חיבורים אמיתיים, לא סמול טוק.",
        "tags": ["sensoryOverload", "slowClearPace", "processingDifficulty"],
        "interests": ["Coding", "Gaming", "Sci-Fi", "Photography", "Coffee"],
        "mood": "lowEnergy",
        "prompt_id": "perfectSunday",
        "prompt_answer": "סשן קידוד ללא הפרעות, משלוח ואפס התחייבויות חברתיות",
        "picture_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=500&fit=crop",
        "city": "תל אביב",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 26,
        "looking_for_max_age": 36,
        "looking_for_max_distance": 25,
        "looking_for_location": "תל אביב",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "אני לא גס, אני ישיר! חוץ מזה, אני נותן את הפידבק הכי כנה.",
        "preferred_times": ["night"],
        "response_pace": "slow",
        "time_notes": "אני ינשוף לילה ומעדיף הודעות על שיחות",
    },
    # 9. Oren - Beer Sheva, veteran with PTSD
    {
        "username": f"{MOCK_USER_PREFIX}oren",
        "email": "oren@nomi.app",
        "first_name": "אורן",
        "last_name": "פרץ",
        "display_name": "אורן",
        "gender": "male",
        "age": 34,
        "bio": "חייל משוחרר שמנווט את החיים עם PTSD. חובב טיולי מדבר ואסטרונום חובב. השמיים של הנגב בלילה הם הטיפול שלי.",
        "tags": ["calmSafeSpace", "needsAccessibility"],
        "interests": ["Hiking", "Astronomy", "Photography", "Meditation", "Fitness"],
        "mood": "adventurous",
        "prompt_id": "custom",
        "prompt_answer": "לחקור כל מכתש ושביל בנגב - יש ימים קשים יותר, אבל הנוף שווה את זה",
        "picture_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&h=500&fit=crop",
        "city": "באר שבע",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 27,
        "looking_for_max_age": 40,
        "looking_for_max_distance": 60,
        "looking_for_location": "באר שבע",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "ללמוד לבקש עזרה כשאני צריך - זה דרש יותר אומץ מכל דבר אחר",
        "preferred_times": ["morning", "evening"],
        "response_pace": "moderate",
        "time_notes": "מקומות צפופים יכולים להציף אותי, אז אני מעדיף סביבות שקטות יותר",
    },
    # 10. Yael - Netanya, chronic pain warrior
    {
        "username": f"{MOCK_USER_PREFIX}yael",
        "email": "yael@nomi.app",
        "first_name": "יעל",
        "last_name": "מזרחי",
        "display_name": "יעל",
        "gender": "female",
        "age": 25,
        "bio": "חיה עם פיברומיאלגיה. אוהבת ים שלוקחת את החיים כפית אחת בכל פעם. מחפשת מישהו סבלני שמבין שתוכניות עשויות להשתנות.",
        "tags": ["needsAccessibility", "calmSafeSpace"],
        "interests": ["Beach", "Art", "Reading", "Movies", "Cats"],
        "mood": "lowEnergy",
        "prompt_id": "custom",
        "prompt_answer": "רק בגלל שאני נראית בסדר לא אומר שאני לא כואבת - אבל יש לי כישורי התמודדות מעולים!",
        "picture_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=500&fit=crop",
        "city": "נתניה",
        "looking_for_genders": ["male", "female"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 33,
        "looking_for_max_distance": 40,
        "looking_for_location": "נתניה",
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "dontLetStop",
        "ask_me_answer": "לבלות שעות בצפייה בשקיעות בטיילת של נתניה - אני פשוט מביאה כריות נוספות!",
        "preferred_times": ["afternoon"],
        "response_pace": "variable",
        "time_notes": "האנרגיה שלי בלתי צפויה, אז גמישות זה המפתח 💜",
    },
    # 11. Eyal - Ramat Gan, ADHD entrepreneur
    {
        "username": f"{MOCK_USER_PREFIX}eyal",
        "email": "eyal@nomi.app",
        "first_name": "אייל",
        "last_name": "אהרוני",
        "display_name": "אייל",
        "gender": "male",
        "age": 29,
        "bio": "מוח ADHD בעולם נוירוטיפי. יזם סדרתי עם 5 פרויקטים לא גמורים. כוח העל שלי? היפרפוקוס על דברים שאני אוהב.",
        "tags": ["processingDifficulty", "sensoryOverload"],
        "interests": ["Technology", "Coffee", "Music", "Travel", "Dogs"],
        "mood": "chatty",
        "prompt_id": "custom",
        "prompt_answer": "לשבת בבית קפה עם קפה טוב ולדבר על כל מה שעולה בראש - בלי סמול טוק",
        "picture_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=500&fit=crop",
        "city": "רמת גן",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 24,
        "looking_for_max_age": 35,
        "looking_for_max_distance": 35,
        "looking_for_location": "רמת גן",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני יכול ללמוד מיומנות חדשה בסוף שבוע... ולשכוח שהיא קיימת עד יום שני 😅",
        "preferred_times": ["flexible"],
        "response_pace": "variable",
        "time_notes": "אני עשוי להגיב מיד או בעוד 3 ימים - זה לא את, זה המוח שלי!",
    },
    # 12. Michal - Jerusalem, hard of hearing social worker
    {
        "username": f"{MOCK_USER_PREFIX}michal",
        "email": "michal@nomi.app",
        "first_name": "מיכל",
        "last_name": "שטרן",
        "display_name": "מיכל",
        "gender": "female",
        "age": 33,
        "bio": "עובדת סוציאלית כבדת שמיעה ולהוטה בנגישות. אני מרכיבה מכשירי שמיעה וקוראת שפתיים כמו מקצוענית. אוהבת את האווירה של העיר העתיקה בירושלים.",
        "tags": ["difficultyHearing", "hearingAids"],
        "interests": ["Social Justice", "History", "Wine", "Cooking", "Dancing"],
        "mood": "open",
        "prompt_id": "convinced",
        "prompt_answer": "החומוס הכי טוב בישראל עדיין מחכה שיגלו אותו (ואני אמצא אותו)",
        "picture_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=500&fit=crop",
        "city": "ירושלים",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 30,
        "looking_for_max_age": 40,
        "looking_for_max_distance": 30,
        "looking_for_location": "ירושלים",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "איך אנחנו שומרים אחד על השני וחוגגים כל ניצחון קטן ביחד",
        "preferred_times": ["evening"],
        "response_pace": "moderate",
        "time_notes": "מעדיפה שיחות וידאו - אני אוהבת לראות פנים כשאנחנו מדברים",
    },
    # 13. Noam - Eilat, mobility aid user
    {
        "username": f"{MOCK_USER_PREFIX}noam",
        "email": "noam@nomi.app",
        "first_name": "נועם",
        "last_name": "ביטון",
        "display_name": "נועם",
        "gender": "male",
        "age": 27,
        "bio": "משתמש בקביים וחי את החיים הכי טובים באילת. מדריך צלילה וחובב חוף. מוגבלות לא עוצרת אותי מלחקור עולמות תת-מימיים.",
        "tags": ["mobilityDifficulty", "shortDistances"],
        "interests": ["Scuba Diving", "Beach", "Photography", "Music", "Travel"],
        "mood": "adventurous",
        "prompt_id": "custom",
        "prompt_answer": "הפכתי למדריך צלילה מותאם מוסמך - ים סוף הוא מגרש המשחקים שלי!",
        "picture_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&h=500&fit=crop",
        "city": "אילת",
        "looking_for_genders": ["everyone"],
        "looking_for_min_age": 21,
        "looking_for_max_age": 35,
        "looking_for_max_distance": 100,
        "looking_for_location": "אילת",
        "relationship_types": ["casual", "friends"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני יכול לזהות דולפינים לפני כולם - זה מגיע עם כל כך הרבה זמן במים!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
    },
    # 14. Roni - Tel Aviv, trans advocate
    {
        "username": f"{MOCK_USER_PREFIX}roni",
        "email": "roni@nomi.app",
        "first_name": "רוני",
        "last_name": "סגל",
        "display_name": "רוני",
        "gender": "male",
        "age": 24,
        "bio": "טרנס וגאה. DJ בלילה, מעצב/ת גרפי/ת ביום. חי/ה באופן אותנטי בלב סצנת הלהט\"ב של תל אביב.",
        "tags": ["calmSafeSpace"],
        "interests": ["Music", "Art", "Dancing", "Fashion", "Social Justice"],
        "mood": "chatty",
        "prompt_id": "custom",
        "prompt_answer": "סוף סוף לחיות כעצמי האותנטי - כל יום הוא חגיגה של מי שאני באמת",
        "picture_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&h=500&fit=crop",
        "city": "תל אביב",
        "looking_for_genders": ["everyone"],
        "looking_for_min_age": 20,
        "looking_for_max_age": 32,
        "looking_for_max_distance": 30,
        "looking_for_location": "תל אביב",
        "relationship_types": ["casual", "friends", "serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "המשפחה הנבחרת שאנחנו יוצרים - הם מגיעים אחד לשני לא משנה מה",
        "preferred_times": ["night", "evening"],
        "response_pace": "quick",
    },
    # 15. Gil - Petah Tikva, blind programmer
    {
        "username": f"{MOCK_USER_PREFIX}gil",
        "email": "gil@nomi.app",
        "first_name": "גיל",
        "last_name": "דיין",
        "display_name": "גיל",
        "gender": "male",
        "age": 30,
        "bio": "מהנדס תוכנה עם לקות ראייה חוקית. אני מקודד עם קוראי מסך ומדבג עם נחישות. מחפש מישהי שמעריכה הומור טכנולוגי וקלמבורים גרועים.",
        "tags": ["difficultySeeing", "visionAids"],
        "interests": ["Coding", "Podcasts", "Board Games", "Coffee", "Comedy"],
        "mood": "chatty",
        "prompt_id": "custom",
        "prompt_answer": "סדרות ריאליטי גרועות - אני לא רואה אותן אבל אני שומע כל מילה",
        "picture_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop",
        "city": "פתח תקווה",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 25,
        "looking_for_max_age": 35,
        "looking_for_max_distance": 35,
        "looking_for_location": "פתח תקווה",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "אנשים עיוורים יכולים להיות עצמאיים! אני גר לבד, עובד בהייטק ומכין קפה מעולה",
        "preferred_times": ["evening"],
        "response_pace": "moderate",
        "time_notes": "הודעות קוליות הן שפת האהבה שלי 🎙️",
    },
    # 16. Eden - Ashdod, diabetic athlete
    {
        "username": f"{MOCK_USER_PREFIX}eden",
        "email": "eden@nomi.app",
        "first_name": "עדן",
        "last_name": "חדד",
        "display_name": "עדן",
        "gender": "female",
        "age": 23,
        "bio": "רצה מרתון עם סוכרת סוג 1. החיישן שלי הוא החבר הכי טוב שלי. מחפשת מישהו שלא יבהל כשאני בודקת סוכר בארוחת ערב.",
        "tags": ["needsAccessibility"],
        "interests": ["Running", "Fitness", "Nutrition", "Travel", "Dogs"],
        "mood": "adventurous",
        "prompt_id": "custom",
        "prompt_answer": "לרוץ מרתונים - אני פשוט לוקחת חטיפים נוספים ומשאבת האינסולין שלי מעודדת אותי",
        "picture_url": "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=400&h=500&fit=crop",
        "city": "אשדוד",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 30,
        "looking_for_max_distance": 40,
        "looking_for_location": "אשדוד",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "לסיים את המרתון הראשון שלי תוך ניהול מושלם של רמת הסוכר לכל אורך המרוץ!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
    },
    # 17. Tomer - Tiberias, anxiety warrior
    {
        "username": f"{MOCK_USER_PREFIX}tomer",
        "email": "tomer@nomi.app",
        "first_name": "תומר",
        "last_name": "אלמוג",
        "display_name": "תומר",
        "gender": "male",
        "age": 28,
        "bio": "חי עם חרדה, אבל היא לא מגדירה אותי. מדריך טיולים בכינרת. נרד היסטוריה שמכיר כל פינה נסתרת בצפון.",
        "tags": ["calmSafeSpace"],
        "interests": ["History", "Hiking", "Photography", "Cooking", "Reading"],
        "mood": "open",
        "prompt_id": "custom",
        "prompt_answer": "על שביל הכינרת בזריחה, כשהעולם שקט ורק אני והטבע",
        "picture_url": "https://images.unsplash.com/photo-1504257432389-52343af06ae3?w=400&h=500&fit=crop",
        "city": "טבריה",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 24,
        "looking_for_max_age": 34,
        "looking_for_max_distance": 50,
        "looking_for_location": "טבריה",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "ביטול תוכניות זה לא אישי - לפעמים אני פשוט צריך יום שקט לטעינה מחדש",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "slow",
        "time_notes": "אני צריך התראה מראש לתוכניות - ספונטניות היא לא החברה שלי",
    },
    # 18. Liora - Haifa, dyslexic artist
    {
        "username": f"{MOCK_USER_PREFIX}liora",
        "email": "liora@nomi.app",
        "first_name": "ליאורה",
        "last_name": "נחמני",
        "display_name": "ליאורה",
        "gender": "female",
        "age": 26,
        "bio": "אמנית דיסלקטית שחושבת בתמונות. הציורים שלי בגלריות ברחבי חיפה. מילים זה קשה, אבל צבעים אומרים המון.",
        "tags": ["processingDifficulty", "sensoryOverload"],
        "interests": ["Art", "Museums", "Coffee", "Fashion", "Photography"],
        "mood": "open",
        "prompt_id": "custom",
        "prompt_answer": "אני רואה דפוסים וקשרים שאחרים מפספסים - המוח שלי מחווט ליצירתיות!",
        "picture_url": "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=400&h=500&fit=crop",
        "city": "חיפה",
        "looking_for_genders": ["male", "female"],
        "looking_for_min_age": 23,
        "looking_for_max_age": 34,
        "looking_for_max_distance": 40,
        "looking_for_location": "חיפה",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "האמנות שלי הוצגה במוזיאון חיפה לאמנות - לקח שנים אבל שווה כל רגע!",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
        "time_notes": "אני מעדיפה הודעות קוליות על טקסט - יותר קל לי להתבטא 🎨",
    },
    # 19. Matan - Tel Aviv, cerebral palsy
    {
        "username": f"{MOCK_USER_PREFIX}matan",
        "email": "matan@nomi.app",
        "first_name": "מתן",
        "last_name": "עופר",
        "display_name": "מתן",
        "gender": "male",
        "age": 32,
        "bio": "עם שיתוק מוחין מלידה. קומיקאי סטנדאפ שמתבדח על מוגבלות. אם אי אפשר לצחוק על החיים, מה הטעם? גם, אני מכין שקשוקה מעולה.",
        "tags": ["mobilityDifficulty", "speechDifficulty", "needsTimeToSpeak"],
        "interests": ["Comedy", "Cooking", "Movies", "Gaming", "Writing"],
        "mood": "chatty",
        "prompt_id": "laughMost",
        "prompt_answer": "כשזרים מניחים שאני שיכור - ההליכה שלי פשוט מדהימה באופן טבעי",
        "picture_url": "https://images.unsplash.com/photo-1463453091185-61582044d556?w=400&h=500&fit=crop",
        "city": "תל אביב",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 27,
        "looking_for_max_age": 38,
        "looking_for_max_distance": 30,
        "looking_for_location": "תל אביב",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "מופע הסטנדאפ הראשון שלי עם קהל מלא! מסתבר שהומור מוגבלות הוא אוניברסלי",
        "preferred_times": ["evening", "night"],
        "response_pace": "moderate",
        "time_notes": "הדיבור שלי עשוי להיות איטי יותר, אבל השנינות שלי מהירה כמו ברק ⚡",
    },
    # 20. Inbar - Rehovot, lupus warrior
    {
        "username": f"{MOCK_USER_PREFIX}inbar",
        "email": "inbar@nomi.app",
        "first_name": "ענבר",
        "last_name": "ואקנין",
        "display_name": "ענבר",
        "gender": "female",
        "age": 28,
        "bio": "חיה עם לופוס ואוהבת את החיים בכל זאת. חוקרת במכון ויצמן. מדע ביום, נטפליקס בלילה. מחפשת שותף/ה למעבדה של החיים.",
        "tags": ["needsAccessibility", "calmSafeSpace"],
        "interests": ["Science", "Reading", "Movies", "Cooking", "Nature"],
        "mood": "lowEnergy",
        "prompt_id": "perfectSunday",
        "prompt_answer": "ברנץ' מאוחר, סרט תיעודי ובכלל ללא תוכניות - יעדי יום התאוששות",
        "picture_url": "https://images.unsplash.com/photo-1485893226355-9a1c32a0c81e?w=400&h=500&fit=crop",
        "city": "רחובות",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 26,
        "looking_for_max_age": 36,
        "looking_for_max_distance": 35,
        "looking_for_location": "רחובות",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "מחלות אוטואימוניות הן בלתי צפויות - אבל גם החיים, ולמדתי להתגלגל עם זה",
        "preferred_times": ["afternoon"],
        "response_pace": "variable",
        "time_notes": "חשיפה לשמש בעייתית לי, אז דייטים בפנים או בערב הם הכי טובים 🌙",
    },
    # 21. Dror - Kfar Saba, speech disorder
    {
        "username": f"{MOCK_USER_PREFIX}dror",
        "email": "dror@nomi.app",
        "first_name": "דרור",
        "last_name": "יעקובי",
        "display_name": "דרור",
        "gender": "male",
        "age": 26,
        "bio": "מגמגם גאה. מורה למוזיקה שמאמין שכל קול ייחודי. כשאני שר, המילים זורמות בחופשיות. מחפש מישהי שמוכנה לשמוע מעבר למילים.",
        "tags": ["speechDifficulty", "needsTimeToSpeak"],
        "interests": ["Music", "Teaching", "Guitar", "Poetry", "Hiking"],
        "mood": "open",
        "prompt_id": "custom",
        "prompt_answer": "אני בונה קשר עם אנשים דרך מוזיקה כשמילים קשות - זה השפה האוניברסלית שלי",
        "picture_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=500&fit=crop",
        "city": "כפר סבא",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 32,
        "looking_for_max_distance": 40,
        "looking_for_location": "כפר סבא",
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "תנו לי זמן לדבר - אני לא עצבני, המוח שלי פשוט עובד בקצב אחר מהפה",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
        "time_notes": "אני מעדיף שיחות אישיות על סביבות רועשות - קל יותר לי לתקשר",
    },
    # 22. Neta - Modi'in, wheelchair athlete
    {
        "username": f"{MOCK_USER_PREFIX}neta",
        "email": "neta@nomi.app",
        "first_name": "נטע",
        "last_name": "ברקוביץ",
        "display_name": "נטע",
        "gender": "female",
        "age": 24,
        "bio": "ספורטאית פראלימפית בכדורסל על כיסאות גלגלים. זכיתי במדליות, אבל המטרה האמיתית היא להיות מאושרת. מחפשת מישהו עם רוח תחרותית וחיוך חם.",
        "tags": ["wheelchairUser", "mobilityDifficulty"],
        "interests": ["Sports", "Basketball", "Fitness", "Travel", "Movies"],
        "mood": "adventurous",
        "prompt_id": "custom",
        "prompt_answer": "לייצג את ישראל באליפות העולם! כיסא הגלגלים שלי הוא כלי הספורט שלי",
        "picture_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=500&fit=crop",
        "city": "מודיעין",
        "looking_for_genders": ["male", "female"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 32,
        "looking_for_max_distance": 50,
        "looking_for_location": "מודיעין",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "לזכות במדליית כסף באליפות אירופה - הרגע הכי גאה בחיי!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
    },
    # 23. Itai - Hadera, OCD advocate
    {
        "username": f"{MOCK_USER_PREFIX}itai",
        "email": "itai@nomi.app",
        "first_name": "איתי",
        "last_name": "שוורץ",
        "display_name": "איתי",
        "gender": "male",
        "age": 30,
        "bio": "חי עם OCD וטיפול עזר לי למצוא איזון. מעצב פנים שאוהב סדר (מפתיע, נכון?). מחפש מישהי שמעריכה כנות ומוכנה ללמוד יחד.",
        "tags": ["calmSafeSpace"],
        "interests": ["Design", "Architecture", "Art", "Cooking", "Yoga"],
        "mood": "chatty",
        "prompt_id": "convinced",
        "prompt_answer": "מרחב מסודר = מוח שלו. זו לא אובססיה, זה אמנות",
        "picture_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=500&fit=crop",
        "city": "חדרה",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 25,
        "looking_for_max_age": 36,
        "looking_for_max_distance": 45,
        "looking_for_location": "חדרה",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "הטקסים שלי לא מוזרים, הם מנגנון התמודדות - וטיפול עוזר באמת",
        "preferred_times": ["morning", "evening"],
        "response_pace": "moderate",
    },
    # 24. Hila - Ashkelon, epilepsy warrior
    {
        "username": f"{MOCK_USER_PREFIX}hila",
        "email": "hila@nomi.app",
        "first_name": "הילה",
        "last_name": "זוהר",
        "display_name": "הילה",
        "gender": "female",
        "age": 27,
        "bio": "חיה עם אפילפסיה ועובדת כאחות. למדתי לטפל באחרים ובעצמי. אוהבת ים, טבע ואנשים שלא שופטים.",
        "tags": ["needsAccessibility"],
        "interests": ["Healthcare", "Beach", "Reading", "Cooking", "Dogs"],
        "mood": "open",
        "prompt_id": "perfectSunday",
        "prompt_answer": "הליכה עם הכלב שלי לחוף אשקלון, קפה קר וספר טוב",
        "picture_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=600&fit=crop",
        "additional_photos": [
            "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=600&fit=crop",
        ],
        "city": "אשקלון",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 25,
        "looking_for_max_age": 34,
        "looking_for_max_distance": 40,
        "looking_for_location": "אשקלון",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "dontLetStop",
        "ask_me_answer": "לעזור לאנשים בבית החולים - אני מבינה את החששות שלהם מנקודת מבט ייחודית",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
    },
    # 25. Yuval - Karmiel, dyspraxia advocate
    {
        "username": f"{MOCK_USER_PREFIX}yuval",
        "email": "yuval@nomi.app",
        "first_name": "יובל",
        "last_name": "בר-און",
        "display_name": "יובל",
        "gender": "male",
        "age": 25,
        "bio": "עם דיספרקסיה מילדות. קצת לא מתואם, אבל המוח שלי מהיר כמו ברק. עובד בהייטק ואוהב משחקי קופסה. מחפש מישהי שמצחיקה לה שאני נתקל בדברים.",
        "tags": ["processingDifficulty"],
        "interests": ["Gaming", "Board Games", "Technology", "Movies", "Coffee"],
        "mood": "chatty",
        "prompt_id": "custom",
        "prompt_answer": "משחקי קופסה עדיפים על משחקי מחשב - בואו נריב",
        "picture_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop",
        "city": "כרמיאל",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 30,
        "looking_for_max_distance": 60,
        "looking_for_location": "כרמיאל",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני פותר בעיות בדרכים לא שגרתיות - המוח שלי חושב מחוץ לקופסה",
        "preferred_times": ["evening", "night"],
        "response_pace": "quick",
    },
    # 26. Sarit - Holon, MS warrior
    {
        "username": f"{MOCK_USER_PREFIX}sarit",
        "email": "sarit@nomi.app",
        "first_name": "שרית",
        "last_name": "פרידמן",
        "display_name": "שרית",
        "gender": "female",
        "age": 32,
        "bio": "חיה עם טרשת נפוצה. ימים טובים וימים פחות, אבל תמיד מחפשת את האור. מטפלת באמנות ואוהבת צבעים ואנשים אמיתיים.",
        "tags": ["mobilityDifficulty", "needsAccessibility", "calmSafeSpace"],
        "interests": ["Painting", "Art", "Music", "Nature", "Meditation"],
        "mood": "lowEnergy",
        "prompt_id": "custom",
        "prompt_answer": "העייפות אינה עצלות - זה כמו שהסוללה שלי מתרוקנת פי 10 יותר מהר",
        "picture_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=500&fit=crop",
        "city": "חולון",
        "looking_for_genders": ["male", "female"],
        "looking_for_min_age": 27,
        "looking_for_max_age": 38,
        "looking_for_max_distance": 35,
        "looking_for_location": "חולון",
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "ההבנה שלא צריך להסביר את עצמי - אנשים פשוט מקבלים",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "variable",
        "time_notes": "האנרגיה שלי הכי טובה בבוקר, אחר הצהריים אני לפעמים צריכה מנוחה",
    },
    # 27. Asaf - Kiryat Ata, prosthetic leg athlete
    {
        "username": f"{MOCK_USER_PREFIX}asaf",
        "email": "asaf@nomi.app",
        "first_name": "אסף",
        "last_name": "מלכה",
        "display_name": "אסף",
        "gender": "male",
        "age": 29,
        "bio": "איבדתי את הרגל בתאונה, מצאתי כוח פנימי שלא ידעתי שיש לי. מאמן כושר אישי ורץ מרתונים. הרגל התותבת שלי היא הסופרגיבור שלי.",
        "tags": ["mobilityDifficulty", "needsAccessibility"],
        "interests": ["Running", "Fitness", "Sports", "Travel", "Photography"],
        "mood": "adventurous",
        "prompt_id": "custom",
        "prompt_answer": "לסיים מרתון תל אביב עם רגל תותבת - זה הוכיח לי שאני יכול הכל",
        "picture_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop",
        "city": "קריית אתא",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 24,
        "looking_for_max_age": 35,
        "looking_for_max_distance": 50,
        "looking_for_location": "קריית אתא",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "הפכתי את החולשה שלי לכוח - עכשיו אני מעורר השראה בכל מקום",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
    },
    # 28. Ruti - Bat Yam, Crohn's disease
    {
        "username": f"{MOCK_USER_PREFIX}ruti",
        "email": "ruti@nomi.app",
        "first_name": "רותי",
        "last_name": "אבוטבול",
        "display_name": "רותי",
        "gender": "female",
        "age": 26,
        "bio": "חיה עם קרוהן ולומדת לאהוב את הגוף שלי. בלוגרית אוכל ואוהבת לבשל מתכונים ידידותיים למעיים. מחפשת מישהו שמבין שלפעמים הבטן קובעת את התוכניות.",
        "tags": ["needsAccessibility", "calmSafeSpace"],
        "interests": ["Cooking", "Blogging", "Nutrition", "Beach", "Movies"],
        "mood": "open",
        "prompt_id": "custom",
        "prompt_answer": "לחקור מסעדות חדשות - אני פשוט חוקרת לפני ומביאה חטיפים מאושרים איתי",
        "picture_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=500&fit=crop",
        "city": "בת ים",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 25,
        "looking_for_max_age": 34,
        "looking_for_max_distance": 30,
        "looking_for_location": "בת ים",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "מחלות מעיים זה לא נושא שיחה רומנטי, אבל זה חלק ממי שאני והכנות חשובה לי",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
    },
    # 29. Adi - Nahariya, bipolar advocate
    {
        "username": f"{MOCK_USER_PREFIX}adi",
        "email": "adi@nomi.app",
        "first_name": "עדי",
        "last_name": "מזור",
        "display_name": "עדי",
        "gender": "male",
        "age": 28,
        "bio": "חי/ה עם ביפולריות וגאה. אמן/ית דיגיטלי/ת עם רגשות גדולים ואומנות גדולה עוד יותר. מחפש/ת אנשים אותנטיים שלא מפחדים מעומק.",
        "tags": ["calmSafeSpace", "sensoryOverload"],
        "interests": ["Digital Art", "Music", "Psychology", "Writing", "Coffee"],
        "mood": "open",
        "prompt_id": "custom",
        "prompt_answer": "אני חווה/ה רגשות בעוצמה - זה הופך אותי לאמן/ית מדהים/ה ולחבר/ה עמוק/ה",
        "picture_url": "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=400&h=500&fit=crop",
        "city": "נהריה",
        "looking_for_genders": ["everyone"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 36,
        "looking_for_max_distance": 70,
        "looking_for_location": "נהריה",
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "המצבים הרגשיים שלי זה לא אישיות - זה מחלה ואני מטפל/ת בה כמו שצריך",
        "preferred_times": ["flexible"],
        "response_pace": "variable",
        "time_notes": "האנרגיה שלי משתנה, אבל אני תמיד כנה/ה לגבי איך אני מרגיש/ה",
    },
    # 30. Omri - Kiryat Gat, Tourette's syndrome
    {
        "username": f"{MOCK_USER_PREFIX}omri",
        "email": "omri@nomi.app",
        "first_name": "עומרי",
        "last_name": "סימן-טוב",
        "display_name": "עומרי",
        "gender": "male",
        "age": 24,
        "bio": "עם תסמונת טורט. התיקים שלי הם חלק ממי שאני. עובד בתור מפתח ומשחק בלהקה. מחפש מישהי שרואה מעבר לתנועות.",
        "tags": ["processingDifficulty", "sensoryOverload"],
        "interests": ["Music", "Drumming", "Coding", "Gaming", "Comics"],
        "mood": "chatty",
        "prompt_id": "custom",
        "prompt_answer": "אני יכול לנגן סולו תופים בעיניים עצומות - הידיים שלי פשוט יודעות",
        "picture_url": "https://images.unsplash.com/photo-1463453091185-61582044d556?w=400&h=500&fit=crop",
        "city": "קריית גת",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 20,
        "looking_for_max_age": 28,
        "looking_for_max_distance": 50,
        "looking_for_location": "קריית גת",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "התיקים שלי גרועים יותר כשאני מלחיץ - אבל זה בסדר, זה רק התנועות של המוח שלי",
        "preferred_times": ["evening", "night"],
        "response_pace": "quick",
    },
    # 31. Dana - Afula, fibromyalgia advocate
    {
        "username": f"{MOCK_USER_PREFIX}dana",
        "email": "dana@nomi.app",
        "first_name": "דנה",
        "last_name": "חדד",
        "display_name": "דנה",
        "gender": "female",
        "age": 31,
        "bio": "חיה עם פיברומיאלגיה ומלמדת יוגה מותאמת. החוכמה שלי: להקשיב לגוף. אוהבת טבע, שקיעות ושיחות אמיתיות.",
        "tags": ["needsAccessibility", "slowClearPace"],
        "interests": ["Yoga", "Meditation", "Nature", "Reading", "Wellness"],
        "mood": "lowEnergy",
        "prompt_id": "perfectSunday",
        "prompt_answer": "יוגה עדינה בבוקר, תה ירוק וטיול איטי ביער - חגיגה של האטה",
        "picture_url": "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=400&h=500&fit=crop",
        "city": "עפולה",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 28,
        "looking_for_max_age": 40,
        "looking_for_max_distance": 50,
        "looking_for_location": "עפולה",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "הסבלנות וההבנה - אף אחד לא לוחץ עלי להיות מי שאני לא יכולה להיות היום",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "slow",
        "time_notes": "אני צריכה זמן להתאושש בין אירועים, אז תוכניות צריכות מרווח",
    },
    # 32. Shai - Beit Shemesh, visual processing disorder
    {
        "username": f"{MOCK_USER_PREFIX}shai",
        "email": "shai@nomi.app",
        "first_name": "שי",
        "last_name": "רביב",
        "display_name": "שי",
        "gender": "male",
        "age": 27,
        "bio": "עם הפרעת עיבוד חזותי. המוח שלי מעבד דברים אחרת, אבל זה הופך אותי ליצירתי. מוזיקאי ואוהב את הכוח של סאונד על פני תמונות.",
        "tags": ["processingDifficulty", "sensoryOverload"],
        "interests": ["Music", "Music Production", "Podcasts", "Cooking", "Hiking"],
        "mood": "open",
        "prompt_id": "custom",
        "prompt_answer": "אני שומע פרטים במוזיקה שאחרים מפספסים - המוח שלי מפצה על הראייה",
        "picture_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=500&fit=crop",
        "city": "בית שמש",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 23,
        "looking_for_max_age": 33,
        "looking_for_max_distance": 40,
        "looking_for_location": "בית שמש",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "קריאה לוקחת לי זמן ומסכים מייגעים - אבל שיחות פנים אל פנים? אני מעולה בהן",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
    },
    # 33. Shani - Raanana, colostomy bag user
    {
        "username": f"{MOCK_USER_PREFIX}shani",
        "email": "shani@nomi.app",
        "first_name": "שני",
        "last_name": "גבע",
        "display_name": "שני",
        "gender": "female",
        "age": 29,
        "bio": "חיה עם שקית קולוסטומיה. חשבתי שזה הסוף, אבל זה למעשה שחרר אותי. מעצבת אופנה שאוהבת חיים ואנשים שלא נבהלים ממציאות.",
        "tags": ["needsAccessibility"],
        "interests": ["Fashion", "Design", "Blogging", "Coffee", "Travel"],
        "mood": "chatty",
        "prompt_id": "custom",
        "prompt_answer": "לדבר בגלוי על השקית שלי ולעזור לאחרים להבין שזה לא מגדיר אותי",
        "picture_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=500&fit=crop",
        "city": "רעננה",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 27,
        "looking_for_max_age": 37,
        "looking_for_max_distance": 30,
        "looking_for_location": "רעננה",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "השקת קולקציית אופנה למי שחיים עם שקיות - לעזור לאחרים להרגיש יפים",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "quick",
    },
    # 34. Lior - Yokneam, schizophrenia advocate
    {
        "username": f"{MOCK_USER_PREFIX}lior",
        "email": "lior@nomi.app",
        "first_name": "ליאור",
        "last_name": "קדוש",
        "display_name": "ליאור",
        "gender": "male",
        "age": 33,
        "bio": "חי עם סכיזופרניה בניהול טוב. עובד כספרן ואוהב שקט, סדר וסיפורים טובים. מחפש מישהי סבלנית שמוכנה ללמוד יחד.",
        "tags": ["calmSafeSpace", "slowClearPace"],
        "interests": ["Reading", "Writing", "History", "Movies", "Philosophy"],
        "mood": "lowEnergy",
        "prompt_id": "convinced",
        "prompt_answer": "ספרים מספרים יותר אמת על אנשים מאשר רשתות חברתיות",
        "picture_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=500&fit=crop",
        "city": "יקנעם",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 28,
        "looking_for_max_age": 40,
        "looking_for_max_distance": 50,
        "looking_for_location": "יקנעם",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "סכיזופרניה עם טיפול נראית כמו כל חיים רגילים - אני עובד, אוהב ומתפקד",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "slow",
        "time_notes": "אני מעדיף סביבות שקטות עם פחות גירויים",
    },
    # 35. Gal - Kfar Yona, spinal injury
    {
        "username": f"{MOCK_USER_PREFIX}gal",
        "email": "gal@nomi.app",
        "first_name": "גל",
        "last_name": "שחר",
        "display_name": "גל",
        "gender": "female",
        "age": 25,
        "bio": "פציעת עמוד שדרה מתאונה. משתמשת בכיסא גלגלים ובונה חיים חדשים. גרפיקאית דיגיטלית שעובדת מהבית ואוהבת יצירתיות ללא גבולות.",
        "tags": ["wheelchairUser", "needsAccessibility"],
        "interests": ["Graphic Design", "Art", "Gaming", "Movies", "Design"],
        "mood": "open",
        "prompt_id": "custom",
        "prompt_answer": "ליצור אמנות ולחיות את החיים שאני רוצה - הכיסא זה רק אמצעי תחבורה",
        "picture_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=500&fit=crop",
        "city": "כפר יונה",
        "looking_for_genders": ["male", "female"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 33,
        "looking_for_max_distance": 45,
        "looking_for_location": "כפר יונה",
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "לבנות קריירה מהבית ולהפוך את האתגר לכוח - אני עצמאית לחלוטין",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
    },
    # 36. Uri - Dimona, hearing aids user
    {
        "username": f"{MOCK_USER_PREFIX}uri",
        "email": "uri@nomi.app",
        "first_name": "אורי",
        "last_name": "אברהם",
        "display_name": "אורי",
        "gender": "male",
        "age": 26,
        "bio": "משתמש במכשירי שמיעה ועובד כמהנדס חשמל. אני אוהב טכנולוגיה (כולל מה שבאוזניים שלי), מוזיקה ואנשים שמבינים שאני לא מתעלם - אני פשוט לא שומע.",
        "tags": ["difficultyHearing", "hearingAids"],
        "interests": ["Engineering", "Technology", "Music", "Hiking", "Coffee"],
        "mood": "chatty",
        "prompt_id": "custom",
        "prompt_answer": "לטייל ביפן - אני חולם על הטכנולוגיה, האוכל והשקט שם",
        "picture_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=500&fit=crop",
        "city": "דימונה",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 32,
        "looking_for_max_distance": 80,
        "looking_for_location": "דימונה",
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "תדברו אליי מלפנים, לא מאחורה - אני לא רואה את הקול",
        "preferred_times": ["evening"],
        "response_pace": "moderate",
    },
    # 37. Maya - Migdal HaEmek, eating disorder recovery
    {
        "username": f"{MOCK_USER_PREFIX}maya2",
        "email": "maya2@nomi.app",
        "first_name": "מאיה",
        "last_name": "סער",
        "display_name": "מאיה",
        "gender": "female",
        "age": 23,
        "bio": "בהחלמה מהפרעת אכילה וגאה בדרך שעשיתי. פעילה למען בריאות הנפש וקבלה עצמית. מחפשת מישהו שמבין שמסע זה לא תמיד קו ישר.",
        "tags": ["calmSafeSpace"],
        "interests": ["Wellness", "Photography", "Cooking", "Yoga", "Meditation"],
        "mood": "open",
        "prompt_id": "custom",
        "prompt_answer": "בחירה להחלים כל יום מחדש - זה הדבר הכי אמיץ שעשיתי",
        "picture_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=500&fit=crop",
        "city": "מגדל העמק",
        "looking_for_genders": ["male"],
        "looking_for_min_age": 22,
        "looking_for_max_age": 30,
        "looking_for_max_distance": 50,
        "looking_for_location": "מגדל העמק",
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "החלמה זה לא יעד, זה מסע יומי - ויש ימים טובים וימים קשים",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "moderate",
    },
    # 38. Barak - Safed, low vision artist
    {
        "username": f"{MOCK_USER_PREFIX}barak",
        "email": "barak@nomi.app",
        "first_name": "ברק",
        "last_name": "אלון",
        "display_name": "ברק",
        "gender": "male",
        "age": 30,
        "bio": "אמן עם ראייה חלקית בצפת המיסטית. אני רואה את העולם בטשטוש יפה ומתרגם את זה לציורים. מחפש מישהי שמבינה שראייה היא לא רק בעיניים.",
        "tags": ["difficultySeeing", "partialVision"],
        "interests": ["Art", "Painting", "Music", "Nature", "Meditation"],
        "mood": "adventurous",
        "prompt_id": "custom",
        "prompt_answer": "אני רואה את המהות של דברים, לא רק הצורה החיצונית - זה הופך אותי לאמן טוב יותר",
        "picture_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&h=500&fit=crop",
        "city": "צפת",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 25,
        "looking_for_max_age": 36,
        "looking_for_max_distance": 60,
        "looking_for_location": "צפת",
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "לעשות תערוכת יחיד בצפת - אנשים אמרו שהציורים שלי מראים רגש, לא רק צורות",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "slow",
    },
    # 39. Chen - Or Yehuda, sensory processing disorder
    {
        "username": f"{MOCK_USER_PREFIX}chen",
        "email": "chen@nomi.app",
        "first_name": "חן",
        "last_name": "ששון",
        "display_name": "חן",
        "gender": "male",
        "age": 24,
        "bio": "עם הפרעת עיבוד חושי. העולם לפעמים רועש מדי, בהיר מדי, הכל מדי. מוזיקאי/ת שמוצא/ת נחמה בצלילים שבחרתי. מחפש/ת אנשים שמכבדים גבולות.",
        "tags": ["sensoryOverload", "processingDifficulty", "calmSafeSpace"],
        "interests": ["Music Production", "Gaming", "Reading", "Music", "Meditation"],
        "mood": "lowEnergy",
        "prompt_id": "custom",
        "prompt_answer": "הגירויים מציפים אותי לפעמים - זה לא אישי אם אני צריך/ה הפסקה",
        "picture_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&h=500&fit=crop",
        "city": "אור יהודה",
        "looking_for_genders": ["everyone"],
        "looking_for_min_age": 20,
        "looking_for_max_age": 30,
        "looking_for_max_distance": 35,
        "looking_for_location": "אור יהודה",
        "relationship_types": ["friends", "serious"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני שומע/ת תדרים וטקסטורות שאחרים מפספסים - עוזר לי ביצירת מוזיקה",
        "preferred_times": ["night"],
        "response_pace": "variable",
        "time_notes": "אני מעדיף/ה מקומות שקטים עם פחות גירויים",
    },
    # 40. Nir - Rosh Pina, ALS early stage
    {
        "username": f"{MOCK_USER_PREFIX}nir",
        "email": "nir@nomi.app",
        "first_name": "ניר",
        "last_name": "טל",
        "display_name": "ניר",
        "gender": "male",
        "age": 34,
        "bio": "מאובחן עם ALS בשלב מוקדם. לומד לחיות בהווה וליהנות מכל רגע. מורה לפילוסופיה שמחפש עומק ומשמעות. מחפש חיבור אמיתי, לא רק רומנטיקה.",
        "tags": ["needsAccessibility", "slowClearPace"],
        "interests": ["Philosophy", "Writing", "Nature", "Reading", "Photography"],
        "mood": "open",
        "prompt_id": "convinced",
        "prompt_answer": "החיים יפים בגלל הזמניות שלהם, לא למרות זה",
        "picture_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=500&fit=crop",
        "city": "ראש פינה",
        "looking_for_genders": ["female"],
        "looking_for_min_age": 28,
        "looking_for_max_age": 42,
        "looking_for_max_distance": 70,
        "looking_for_location": "ראש פינה",
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "אני לא הולך למקום אפל - אני בוחר לחיות באור שיש לי עכשיו",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "moderate",
        "time_notes": "הכוח הפיזי שלי משתנה, אבל הרצון שלי לחיבור חזק כתמיד",
    },
]


class Command(BaseCommand):
    help = "Seed immutable mock users for the application (idempotent)"

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("🌱 Seeding mock users...")
        
        created = 0
        
        with transaction.atomic():
            for user_data in MOCK_USERS:
                was_created = self._create_mock_user(user_data)
                if was_created:
                    created += 1
        
        skipped = len(MOCK_USERS) - created
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Mock users: {created} created, {skipped} already exist (manage via Django admin)"
            )
        )
        self.stdout.write(
            f"   Total mock users in database: {User.objects.filter(username__startswith=MOCK_USER_PREFIX).count()}"
        )

    def _create_mock_user(self, user_data: dict[str, Any]) -> bool:
        """
        Create a mock user ONLY if it doesn't exist.
        Existing users are NOT updated - manage them via Django admin.
        Returns True if created, False if already exists (skipped).
        """
        username = user_data["username"]
        
        # Check if user exists - if so, ensure they have all profile data
        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            # Ensure existing user has all profile attributes populated
            self._ensure_photos(existing_user, user_data)
            self._ensure_looking_for(existing_user, user_data)
            self._ensure_profile_data(existing_user, user_data)
            self._ensure_disability_tags(existing_user, user_data)
            return False
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=user_data["email"],
            password="mockuser123!",  # Mock users can't really login
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
        )
        
        # Mark as onboarded so they appear in discovery
        user.is_onboarded = True
        user.is_profile_complete = True
        user.is_verified = True
        user.social_provider = "mock"
        user.save()
        
        # Create auth token
        Token.objects.get_or_create(user=user)
        
        # Create profile with initial data
        self._create_profile(user, user_data)
        
        self.stdout.write(f"  ➕ Created: {username}")
        return True

    def _create_profile(self, user: Any, user_data: dict[str, Any]) -> None:
        """Create the initial profile for a new mock user."""
        username = user_data["username"]
        
        # Check for local generated avatar first, fallback to Unsplash
        local_avatar = get_local_avatar_url(username)
        picture_url = local_avatar or user_data.get("picture_url", "")
        
        profile = Profile.objects.create(
            user=user,
            display_name=user_data.get("display_name", user_data["first_name"]),
            bio=user_data["bio"],
            current_mood=user_data["mood"],
            gender=user_data["gender"],
            city=user_data.get("city", "Tel Aviv"),
            picture_url=picture_url,
            prompt_id=user_data.get("prompt_id", "laughMost"),
            prompt_answer=user_data.get("prompt_answer", ""),
            # Ask Me About It
            ask_me_prompt_id=user_data.get("ask_me_prompt_id", ""),
            ask_me_answer=user_data.get("ask_me_answer", ""),
            # Time Preferences
            preferred_times=user_data.get("preferred_times", []),
            response_pace=user_data.get("response_pace", ""),
            time_notes=user_data.get("time_notes", ""),
            # Relationship Intent
            relationship_intent=self._derive_relationship_intent(user_data),
            is_visible=True,
            date_of_birth=date.today() - timedelta(days=user_data.get("age", 25) * 365),
        )
        
        # Add tags
        for tag_code in user_data.get("tags", []):
            tag = DisabilityTag.objects.filter(code=tag_code).first()
            if tag:
                profile.disability_tags.add(tag)
        
        # Add interests
        for interest_name in user_data.get("interests", []):
            interest, _ = Interest.objects.get_or_create(
                name=interest_name,
                defaults={"icon": "✨", "category": "Other"}
            )
            profile.interests.add(interest)
        
        # Create looking for preferences
        # Use Gender enum for type safety (male/female values)
        from profiles.enums import Gender
        genders = user_data.get("looking_for_genders", [Gender.MALE, Gender.FEMALE])
        
        LookingFor.objects.create(
            profile=profile,
            min_age=user_data.get("looking_for_min_age", 18),
            max_age=user_data.get("looking_for_max_age", 50),
            max_distance=user_data.get("looking_for_max_distance", 50),
            preferred_location=user_data.get("looking_for_location", user_data.get("city", "")),
            genders=genders,
        )
        
        # Create profile photos
        # Use local avatar if available, otherwise fallback to Unsplash
        primary_photo_url = local_avatar or user_data.get("picture_url")
        if primary_photo_url:
            ProfilePhoto.objects.create(
                profile=profile,
                url=primary_photo_url,
                is_primary=True,
                order=0,
            )
        
        # Additional photos (use Unsplash for now, could generate more local ones later)
        for i, photo_url in enumerate(user_data.get("additional_photos", []), start=1):
            ProfilePhoto.objects.create(
                profile=profile,
                url=photo_url,
                is_primary=False,
                order=i,
            )

    def _ensure_photos(self, user: Any, user_data: dict[str, Any]) -> None:
        """Ensure existing mock user has photos created."""
        if not hasattr(user, "profile"):
            return
        
        profile = user.profile
        username = user_data["username"]
        
        # Check if profile already has photos
        if profile.photos.exists():
            return
        
        # Use local avatar if available, otherwise fallback to Unsplash
        local_avatar = get_local_avatar_url(username)
        picture_url = local_avatar or user_data.get("picture_url")
        
        if picture_url:
            ProfilePhoto.objects.create(
                profile=profile,
                url=picture_url,
                is_primary=True,
                order=0,
            )
        
        # Additional photos
        for i, photo_url in enumerate(user_data.get("additional_photos", []), start=1):
            ProfilePhoto.objects.create(
                profile=profile,
                url=photo_url,
                is_primary=False,
                order=i,
            )
        
        self.stdout.write(f"  📷 Added photos: {user.username}")

    @staticmethod
    def _derive_relationship_intent(user_data: dict[str, Any]) -> str:
        """
        Derive relationship_intent from the user's relationship_types list.
        Maps: serious → relationship, friends → friendship, casual only → unsure.
        """
        rel_types = user_data.get("relationship_types", [])
        if "serious" in rel_types:
            return "relationship"
        if "friends" in rel_types:
            return "friendship"
        return "unsure"

    def _ensure_looking_for(self, user: Any, user_data: dict[str, Any]) -> None:
        """Ensure existing mock user has looking for preferences filled."""
        if not hasattr(user, "profile"):
            return

        profile = user.profile

        from profiles.enums import Gender
        genders = user_data.get("looking_for_genders", [Gender.MALE, Gender.FEMALE])

        looking_for_data = {
            "min_age": user_data.get("looking_for_min_age", 18),
            "max_age": user_data.get("looking_for_max_age", 50),
            "max_distance": user_data.get("looking_for_max_distance", 50),
            "preferred_location": user_data.get("looking_for_location", user_data.get("city", "")),
            "genders": genders,
        }

        looking_for, created = LookingFor.objects.update_or_create(
            profile=profile,
            defaults=looking_for_data,
        )
        if created:
            self.stdout.write(f"  💝 Added looking for: {user.username}")

    def _ensure_profile_data(self, user: Any, user_data: dict[str, Any]) -> None:
        """Ensure existing mock user has all profile fields populated
        (relationship intent, time notes, response pace, etc.)."""
        if not hasattr(user, "profile"):
            return

        profile = user.profile
        updated = False

        # Always set relationship intent from seed data
        relationship_intent = self._derive_relationship_intent(user_data)
        if relationship_intent and profile.relationship_intent != relationship_intent:
            profile.relationship_intent = relationship_intent
            updated = True

        # Ensure time_notes is populated
        time_notes = user_data.get("time_notes", "")
        if time_notes and profile.time_notes != time_notes:
            profile.time_notes = time_notes
            updated = True

        # Ensure response_pace is populated
        response_pace = user_data.get("response_pace", "")
        if response_pace and profile.response_pace != response_pace:
            profile.response_pace = response_pace
            updated = True

        # Ensure preferred_times is populated
        preferred_times = user_data.get("preferred_times", [])
        if preferred_times and profile.preferred_times != preferred_times:
            profile.preferred_times = preferred_times
            updated = True

        # Ensure ask_me fields are populated
        ask_me_prompt_id = user_data.get("ask_me_prompt_id", "")
        if ask_me_prompt_id and profile.ask_me_prompt_id != ask_me_prompt_id:
            profile.ask_me_prompt_id = ask_me_prompt_id
            updated = True

        ask_me_answer = user_data.get("ask_me_answer", "")
        if ask_me_answer and profile.ask_me_answer != ask_me_answer:
            profile.ask_me_answer = ask_me_answer
            updated = True

        if updated:
            profile.save()
            self.stdout.write(f"  🔄 Updated profile data: {user.username}")

    def _ensure_disability_tags(self, user: Any, user_data: dict[str, Any]) -> None:
        """Ensure existing mock user has all disability tags from seed data."""
        if not hasattr(user, "profile"):
            return

        profile = user.profile
        expected_tags = user_data.get("tags", [])
        if not expected_tags:
            return

        current_tag_codes = set(profile.disability_tags.values_list("code", flat=True))
        expected_tag_codes = set(expected_tags)

        missing_codes = expected_tag_codes - current_tag_codes
        if missing_codes:
            for tag_code in missing_codes:
                tag = DisabilityTag.objects.filter(code=tag_code).first()
                if tag:
                    profile.disability_tags.add(tag)
            self.stdout.write(f"  🏷️  Added disability tags ({', '.join(missing_codes)}): {user.username}")