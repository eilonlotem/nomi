"""
Management command to seed mock users for the application.
This command is idempotent - running it multiple times won't create duplicates.
Usage: python manage.py seed_mock_users

Run on every deploy to ensure mock users exist.
"""
from __future__ import annotations

from datetime import date, timedelta
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

# Mock users data - these are immutable seed users
# All 20 profiles are from Israel with diverse cities, backgrounds, and accessibility needs
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
        "tags": ["wheelchairUser", "chronicIllness"],
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
        "looking_for_genders": ["male", "nonbinary"],
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "כיסא הגלגלים שלי הוא בעצם יצירת אמנות - צבעתי אותו בעצמי בנושא גלקסיה!",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
        "date_pace": "slow",
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
        "tags": ["deafHoh", "neurodivergent"],
        "interests": ["Art", "Coffee", "Movies", "Cooking", "Gaming"],
        "mood": "chatty",
        "prompt_id": "perfectSunday",
        "prompt_answer": "סיור גלריות בבוקר, ואז ציור בבית קפה שקט",
        "picture_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop",
        "city": "ירושלים",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני שם לב לפרטים ויזואליים שאחרים מפספסים - זה הופך אותי לאמן טוב יותר ולצופה אנשים מצוין!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
        "date_pace": "ready",
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
        "tags": ["neurodivergent", "autism"],
        "interests": ["Gaming", "Coding", "Sci-Fi", "Music", "Reading"],
        "mood": "lowEnergy",
        "prompt_id": "convinced",
        "prompt_answer": "רובוטים יעריכו בסוף ממים טובים",
        "picture_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=500&fit=crop",
        "city": "חיפה",
        "looking_for_genders": ["male", "female", "nonbinary"],
        "relationship_types": ["friends", "casual"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "סמול טוק באמת מתיש אותי, אבל שיחות עמוקות על תחומי עניין? אני יכולה לדבר שעות!",
        "preferred_times": ["night", "evening"],
        "response_pace": "variable",
        "date_pace": "virtual",
    },
    # 4. Alex - Tel Aviv, chronic illness advocate
    {
        "username": f"{MOCK_USER_PREFIX}alex",
        "email": "alex@nomi.app",
        "first_name": "אלכס",
        "last_name": "שפירא",
        "display_name": "אלכס",
        "gender": "nonbinary",
        "age": 30,
        "bio": "חי/ה עם מחלה כרונית. פעיל/ה למען זכויות אנשים עם מוגבלות ונגישות. אוהב/ת הליכות בטבע (בקצב שלי) ושיחות משמעותיות.",
        "tags": ["chronicIllness", "invisible"],
        "interests": ["Writing", "Podcasts", "Nature", "Photography", "Meditation"],
        "mood": "adventurous",
        "prompt_id": "laughMost",
        "prompt_answer": "הדרכים היצירתיות שבהן אני מסביר/ה את המוגבלות הנסתרת שלי לזרים מבולבלים",
        "picture_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=500&fit=crop",
        "city": "תל אביב",
        "looking_for_genders": ["male", "female", "nonbinary"],
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "dontLetStop",
        "ask_me_answer": "לחקור מקומות יפים - אני פשוט לוקח/ת חטיפים נוספים ומתכנן/ת עצירות למנוחה!",
        "preferred_times": ["flexible"],
        "response_pace": "variable",
        "date_pace": "slow",
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
        "tags": ["mentalHealth", "caregiver"],
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
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "התמיכה וההבנה הבלתי מותנית - אנחנו באמת מבינים אחד את השני!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "moderate",
        "date_pace": "slow",
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
        "tags": ["mobility", "acquired"],
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
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "בניית הסטארטאפ שלי מאפס - מסתבר שהתאמה היא מיומנות מצוינת ליזמות!",
        "preferred_times": ["evening", "night"],
        "response_pace": "quick",
        "date_pace": "ready",
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
        "tags": ["blindLowVision"],
        "interests": ["Music", "Podcasts", "Dancing", "Swimming", "Languages"],
        "mood": "adventurous",
        "prompt_id": "laughMost",
        "prompt_answer": "כשאנשים מנופפים לי בביישנות לפני שהם נזכרים...",
        "picture_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=500&fit=crop",
        "city": "הרצליה",
        "looking_for_genders": ["male", "nonbinary"],
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני שומעת דברים שאחרים מפספסים - מעולה לציתות... כלומר, להערכת מוזיקה! 😄",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "quick",
        "date_pace": "flexible",
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
        "tags": ["autism", "neurodivergent"],
        "interests": ["Coding", "Gaming", "Sci-Fi", "Photography", "Coffee"],
        "mood": "lowEnergy",
        "prompt_id": "perfectSunday",
        "prompt_answer": "סשן קידוד ללא הפרעות, משלוח ואפס התחייבויות חברתיות",
        "picture_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=500&fit=crop",
        "city": "תל אביב",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "אני לא גס, אני ישיר! חוץ מזה, אני נותן את הפידבק הכי כנה.",
        "preferred_times": ["night"],
        "response_pace": "slow",
        "date_pace": "virtual",
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
        "tags": ["mentalHealth", "acquired"],
        "interests": ["Hiking", "Astronomy", "Photography", "Meditation", "Fitness"],
        "mood": "adventurous",
        "prompt_id": "dontLetStop",
        "prompt_answer": "לחקור כל מכתש ושביל בנגב - יש ימים קשים יותר, אבל הנוף שווה את זה",
        "picture_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&h=500&fit=crop",
        "city": "באר שבע",
        "looking_for_genders": ["female"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "ללמוד לבקש עזרה כשאני צריך - זה דרש יותר אומץ מכל דבר אחר",
        "preferred_times": ["morning", "evening"],
        "response_pace": "moderate",
        "date_pace": "slow",
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
        "tags": ["chronicIllness", "invisible"],
        "interests": ["Beach", "Art", "Reading", "Movies", "Cats"],
        "mood": "lowEnergy",
        "prompt_id": "wishPeopleKnew",
        "prompt_answer": "רק בגלל שאני נראית בסדר לא אומר שאני לא כואבת - אבל יש לי כישורי התמודדות מעולים!",
        "picture_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=500&fit=crop",
        "city": "נתניה",
        "looking_for_genders": ["male", "female"],
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "dontLetStop",
        "ask_me_answer": "לבלות שעות בצפייה בשקיעות בטיילת של נתניה - אני פשוט מביאה כריות נוספות!",
        "preferred_times": ["afternoon"],
        "response_pace": "variable",
        "date_pace": "slow",
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
        "tags": ["neurodivergent"],
        "interests": ["Startups", "Coffee", "Music", "Travel", "Dogs"],
        "mood": "chatty",
        "prompt_id": "laughMost",
        "prompt_answer": "כשאני מוצא 47 טאבים פתוחים ולא זוכר למה פתחתי אף אחד מהם",
        "picture_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=500&fit=crop",
        "city": "רמת גן",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני יכול ללמוד מיומנות חדשה בסוף שבוע... ולשכוח שהיא קיימת עד יום שני 😅",
        "preferred_times": ["flexible"],
        "response_pace": "variable",
        "date_pace": "ready",
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
        "tags": ["deafHoh"],
        "interests": ["Social Justice", "History", "Wine", "Cooking", "Dancing"],
        "mood": "open",
        "prompt_id": "convinced",
        "prompt_answer": "החומוס הכי טוב בישראל עדיין מחכה שיגלו אותו (ואני אמצא אותו)",
        "picture_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=500&fit=crop",
        "city": "ירושלים",
        "looking_for_genders": ["male"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "איך אנחנו שומרים אחד על השני וחוגגים כל ניצחון קטן ביחד",
        "preferred_times": ["evening"],
        "response_pace": "moderate",
        "date_pace": "flexible",
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
        "tags": ["mobility"],
        "interests": ["Scuba Diving", "Beach", "Photography", "Music", "Travel"],
        "mood": "adventurous",
        "prompt_id": "coolestThing",
        "prompt_answer": "הפכתי למדריך צלילה מותאם מוסמך - ים סוף הוא מגרש המשחקים שלי!",
        "picture_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&h=500&fit=crop",
        "city": "אילת",
        "looking_for_genders": ["female", "male", "nonbinary"],
        "relationship_types": ["casual", "friends"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "אני יכול לזהות דולפינים לפני כולם - זה מגיע עם כל כך הרבה זמן במים!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
        "date_pace": "ready",
    },
    # 14. Roni - Tel Aviv, trans advocate
    {
        "username": f"{MOCK_USER_PREFIX}roni",
        "email": "roni@nomi.app",
        "first_name": "רוני",
        "last_name": "סגל",
        "display_name": "רוני",
        "gender": "nonbinary",
        "age": 24,
        "bio": "טרנס וגאה. DJ בלילה, מעצב/ת גרפי/ת ביום. חי/ה באופן אותנטי בלב סצנת הלהט\"ב של תל אביב.",
        "tags": ["mentalHealth"],
        "interests": ["Music", "Art", "Dancing", "Fashion", "LGBTQ+ Advocacy"],
        "mood": "chatty",
        "prompt_id": "proudOf",
        "prompt_answer": "סוף סוף לחיות כעצמי האותנטי - כל יום הוא חגיגה של מי שאני באמת",
        "picture_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&h=500&fit=crop",
        "city": "תל אביב",
        "looking_for_genders": ["male", "female", "nonbinary"],
        "relationship_types": ["casual", "friends", "serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "המשפחה הנבחרת שאנחנו יוצרים - הם מגיעים אחד לשני לא משנה מה",
        "preferred_times": ["night", "evening"],
        "response_pace": "quick",
        "date_pace": "flexible",
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
        "tags": ["blindLowVision"],
        "interests": ["Coding", "Podcasts", "Board Games", "Coffee", "Stand-up Comedy"],
        "mood": "chatty",
        "prompt_id": "laughMost",
        "prompt_answer": "כשאנשים שואלים אם אני צריך עזרה לחצות את הכביש... בתוך בניין",
        "picture_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop",
        "city": "פתח תקווה",
        "looking_for_genders": ["female"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "אנשים עיוורים יכולים להיות עצמאיים! אני גר לבד, עובד בהייטק ומכין קפה מעולה",
        "preferred_times": ["evening"],
        "response_pace": "moderate",
        "date_pace": "slow",
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
        "tags": ["chronicIllness", "invisible"],
        "interests": ["Running", "Fitness", "Nutrition", "Travel", "Dogs"],
        "mood": "adventurous",
        "prompt_id": "dontLetStop",
        "prompt_answer": "לרוץ מרתונים - אני פשוט לוקחת חטיפים נוספים ומשאבת האינסולין שלי מעודדת אותי",
        "picture_url": "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=400&h=500&fit=crop",
        "city": "אשדוד",
        "looking_for_genders": ["male"],
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "לסיים את המרתון הראשון שלי תוך ניהול מושלם של רמת הסוכר לכל אורך המרוץ!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
        "date_pace": "ready",
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
        "tags": ["mentalHealth"],
        "interests": ["History", "Hiking", "Photography", "Cooking", "Reading"],
        "mood": "open",
        "prompt_id": "perfectSunday",
        "prompt_answer": "קיאק בזריחה בכינרת, ברנץ' בטבריה וערב הריים שקט עם ספר",
        "picture_url": "https://images.unsplash.com/photo-1504257432389-52343af06ae3?w=400&h=500&fit=crop",
        "city": "טבריה",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "ביטול תוכניות זה לא אישי - לפעמים אני פשוט צריך יום שקט לטעינה מחדש",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "slow",
        "date_pace": "slow",
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
        "tags": ["neurodivergent", "cognitive"],
        "interests": ["Art", "Museums", "Coffee", "Fashion", "Photography"],
        "mood": "open",
        "prompt_id": "superpower",
        "prompt_answer": "אני רואה דפוסים וקשרים שאחרים מפספסים - המוח שלי מחווט ליצירתיות!",
        "picture_url": "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=400&h=500&fit=crop",
        "city": "חיפה",
        "looking_for_genders": ["male", "female"],
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "האמנות שלי הוצגה במוזיאון חיפה לאמנות - לקח שנים אבל שווה כל רגע!",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
        "date_pace": "flexible",
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
        "tags": ["mobility", "speechLanguage"],
        "interests": ["Comedy", "Cooking", "Movies", "Gaming", "Writing"],
        "mood": "chatty",
        "prompt_id": "laughMost",
        "prompt_answer": "כשזרים מניחים שאני שיכור - ההליכה שלי פשוט מדהימה באופן טבעי",
        "picture_url": "https://images.unsplash.com/photo-1463453091185-61582044d556?w=400&h=500&fit=crop",
        "city": "תל אביב",
        "looking_for_genders": ["female"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "מופע הסטנדאפ הראשון שלי עם קהל מלא! מסתבר שהומור מוגבלות הוא אוניברסלי",
        "preferred_times": ["evening", "night"],
        "response_pace": "moderate",
        "date_pace": "ready",
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
        "tags": ["chronicIllness", "invisible", "caregiver"],
        "interests": ["Science", "Reading", "Movies", "Cooking", "Nature"],
        "mood": "lowEnergy",
        "prompt_id": "perfectSunday",
        "prompt_answer": "ברנץ' מאוחר, סרט תיעודי ובכלל ללא תוכניות - יעדי יום התאוששות",
        "picture_url": "https://images.unsplash.com/photo-1485893226355-9a1c32a0c81e?w=400&h=500&fit=crop",
        "city": "רחובות",
        "looking_for_genders": ["male"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "מחלות אוטואימוניות הן בלתי צפויות - אבל גם החיים, ולמדתי להתגלגל עם זה",
        "preferred_times": ["afternoon"],
        "response_pace": "variable",
        "date_pace": "slow",
        "time_notes": "חשיפה לשמש בעייתית לי, אז דייטים בפנים או בערב הם הכי טובים 🌙",
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
        
        # Check if user exists - if so, skip entirely (don't update)
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  ⏭️  Exists: {username} (manage via admin)")
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
        static_prefix = f"/{settings.STATIC_URL.strip('/')}"
        local_photo_base = f"{static_prefix}/mock_profiles/{user.username}"

        # Use locally stored mock images (generated via OpenAI) if available
        if user_data.get("use_local_images", True):
            user_data = {
                **user_data,
                "picture_url": f"{local_photo_base}/1.png",
                "additional_photos": [
                    f"{local_photo_base}/2.png",
                    f"{local_photo_base}/3.png",
                ],
            }

        profile = Profile.objects.create(
            user=user,
            display_name=user_data.get("display_name", user_data["first_name"]),
            bio=user_data["bio"],
            current_mood=user_data["mood"],
            gender=user_data["gender"],
            city=user_data.get("city", "Tel Aviv"),
            picture_url=user_data.get("picture_url", ""),
            prompt_id=user_data.get("prompt_id", "laughMost"),
            prompt_answer=user_data.get("prompt_answer", ""),
            # Ask Me About It
            ask_me_prompt_id=user_data.get("ask_me_prompt_id", ""),
            ask_me_answer=user_data.get("ask_me_answer", ""),
            # Time Preferences
            preferred_times=user_data.get("preferred_times", []),
            response_pace=user_data.get("response_pace", ""),
            date_pace=user_data.get("date_pace", ""),
            time_notes=user_data.get("time_notes", ""),
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
        # Use Gender enum for type safety (male/female/nonbinary values)
        from profiles.enums import Gender
        genders = user_data.get("looking_for_genders", [Gender.MALE, Gender.FEMALE])
        
        LookingFor.objects.create(
            profile=profile,
            min_age=18,
            max_age=50,
            max_distance=100,
            genders=genders,
            relationship_types=user_data.get("relationship_types", ["serious"]),
        )
        
        # Create profile photos
        # Primary photo from picture_url
        if user_data.get("picture_url"):
            ProfilePhoto.objects.create(
                profile=profile,
                url=user_data["picture_url"],
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