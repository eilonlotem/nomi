"""
Management command to seed mock users for the application.
This command is idempotent - running it multiple times won't create duplicates.
Usage: python manage.py seed_mock_users

Run on every deploy to ensure mock users exist.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

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
MOCK_USERS: list[dict[str, Any]] = [
    # 1. Maya - Tel Aviv, wheelchair user
    {
        "username": f"{MOCK_USER_PREFIX}maya",
        "email": "maya@nomi.app",
        "first_name": "Maya",
        "last_name": "Cohen",
        "display_name": "Maya",
        "gender": "female",
        "age": 28,
        "bio": "Wheelchair user who loves adaptive yoga and photography. Looking for genuine connections and someone who appreciates life's simple moments.",
        "tags": ["wheelchairUser", "chronicIllness"],
        "interests": ["Photography", "Yoga", "Art", "Travel", "Coffee"],
        "mood": "open",
        "prompt_id": "laughMost",
        "prompt_answer": "When my cat judges my life choices from across the room",
        "picture_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=600&fit=crop",
        "additional_photos": [
            "https://images.unsplash.com/photo-1524250502761-1ac6f2e30d43?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=400&h=600&fit=crop",
        ],
        "city": "Tel Aviv",
        "looking_for_genders": ["male", "nonbinary"],
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "My wheelchair is basically a custom art piece - I painted it myself with a galaxy theme!",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
        "date_pace": "slow",
    },
    # 2. Daniel - Jerusalem, deaf artist
    {
        "username": f"{MOCK_USER_PREFIX}daniel",
        "email": "daniel@nomi.app",
        "first_name": "Daniel",
        "last_name": "Levy",
        "display_name": "Daniel",
        "gender": "male",
        "age": 32,
        "bio": "Deaf artist and coffee enthusiast. I communicate in sign language and love meeting new people who are patient and curious.",
        "tags": ["deafHoh", "neurodivergent"],
        "interests": ["Art", "Coffee", "Movies", "Cooking", "Gaming"],
        "mood": "chatty",
        "prompt_id": "perfectSunday",
        "prompt_answer": "Gallery hopping in the morning, then sketching at a quiet café",
        "picture_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop",
        "city": "Jerusalem",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "I notice visual details others miss - it makes me a better artist and a great people-watcher!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
        "date_pace": "ready",
    },
    # 3. Noa - Haifa, neurodivergent tech
    {
        "username": f"{MOCK_USER_PREFIX}noa",
        "email": "noa@nomi.app",
        "first_name": "Noa",
        "last_name": "Ben-David",
        "display_name": "Noa",
        "gender": "female",
        "age": 26,
        "bio": "Neurodivergent tech enthusiast. I appreciate patience, understanding, and deep conversations about anything sci-fi.",
        "tags": ["neurodivergent", "autism"],
        "interests": ["Gaming", "Coding", "Sci-Fi", "Music", "Reading"],
        "mood": "lowEnergy",
        "prompt_id": "convinced",
        "prompt_answer": "Robots will eventually appreciate good memes",
        "picture_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=500&fit=crop",
        "city": "Haifa",
        "looking_for_genders": ["male", "female", "nonbinary"],
        "relationship_types": ["friends", "casual"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "Small talk is genuinely exhausting, but deep convos about special interests? I could go for hours!",
        "preferred_times": ["night", "evening"],
        "response_pace": "variable",
        "date_pace": "virtual",
    },
    # 4. Alex - Tel Aviv, chronic illness advocate
    {
        "username": f"{MOCK_USER_PREFIX}alex",
        "email": "alex@nomi.app",
        "first_name": "Alex",
        "last_name": "Shapiro",
        "display_name": "Alex",
        "gender": "nonbinary",
        "age": 30,
        "bio": "Living with chronic illness. Advocate for disability rights and accessibility. Love nature walks (at my own pace) and meaningful conversations.",
        "tags": ["chronicIllness", "invisible"],
        "interests": ["Writing", "Podcasts", "Nature", "Photography", "Meditation"],
        "mood": "adventurous",
        "prompt_id": "laughMost",
        "prompt_answer": "The creative ways I explain my invisible disability to confused strangers",
        "picture_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=500&fit=crop",
        "city": "Tel Aviv",
        "looking_for_genders": ["male", "female", "nonbinary"],
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "dontLetStop",
        "ask_me_answer": "Exploring beautiful places - I just bring extra snacks and plan for rest stops!",
        "preferred_times": ["flexible"],
        "response_pace": "variable",
        "date_pace": "slow",
        "time_notes": "My energy varies day to day, so I appreciate flexibility!",
    },
    # 5. Shira - Rishon LeZion, mental health advocate
    {
        "username": f"{MOCK_USER_PREFIX}shira",
        "email": "shira@nomi.app",
        "first_name": "Shira",
        "last_name": "Goldstein",
        "display_name": "Shira",
        "gender": "female",
        "age": 29,
        "bio": "Mental health advocate and proud caregiver. Believer in self-care, genuine connections, and the healing power of a good hike in the Carmel.",
        "tags": ["mentalHealth", "caregiver"],
        "interests": ["Meditation", "Reading", "Hiking", "Cooking", "Yoga"],
        "mood": "open",
        "prompt_id": "perfectSunday",
        "prompt_answer": "Slow morning with Turkish coffee, a good book, and an afternoon beach walk",
        "picture_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=600&fit=crop",
        "additional_photos": [
            "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=400&h=600&fit=crop",
        ],
        "city": "Rishon LeZion",
        "looking_for_genders": ["male"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "The unconditional support and understanding - we truly get each other!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "moderate",
        "date_pace": "slow",
    },
    # 6. Yossi - Tel Aviv, tech entrepreneur
    {
        "username": f"{MOCK_USER_PREFIX}yossi",
        "email": "yossi@nomi.app",
        "first_name": "Yossi",
        "last_name": "Katz",
        "display_name": "Yossi",
        "gender": "male",
        "age": 35,
        "bio": "Mobility difference since childhood. Tech entrepreneur by day, amateur chef by night. Looking for someone who loves good food and better company.",
        "tags": ["mobility", "acquired"],
        "interests": ["Cooking", "Technology", "Travel", "Wine", "Movies"],
        "mood": "chatty",
        "prompt_id": "convinced",
        "prompt_answer": "The best meals are the ones shared with someone special",
        "picture_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=600&fit=crop",
        "additional_photos": [
            "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=600&fit=crop",
            "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=600&fit=crop",
        ],
        "city": "Tel Aviv",
        "looking_for_genders": ["female"],
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "Building my startup from scratch - turns out adaptability is a great skill for entrepreneurship!",
        "preferred_times": ["evening", "night"],
        "response_pace": "quick",
        "date_pace": "ready",
    },
    # 7. Tamar - Herzliya, blind music lover
    {
        "username": f"{MOCK_USER_PREFIX}tamar",
        "email": "tamar@nomi.app",
        "first_name": "Tamar",
        "last_name": "Azoulay",
        "display_name": "Tamar",
        "gender": "female",
        "age": 27,
        "bio": "Blind since birth, but I see the world in my own beautiful way. Music lover, podcast addict, and expert hugger. Originally from Ramat Gan.",
        "tags": ["blindLowVision"],
        "interests": ["Music", "Podcasts", "Dancing", "Swimming", "Languages"],
        "mood": "adventurous",
        "prompt_id": "laughMost",
        "prompt_answer": "When people awkwardly wave at me before remembering...",
        "picture_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=500&fit=crop",
        "city": "Herzliya",
        "looking_for_genders": ["male", "nonbinary"],
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "I hear things others miss - great for eavesdropping... I mean, appreciating music! 😄",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "quick",
        "date_pace": "flexible",
    },
    # 8. Amit - Tel Aviv, autistic developer
    {
        "username": f"{MOCK_USER_PREFIX}amit",
        "email": "amit@nomi.app",
        "first_name": "Amit",
        "last_name": "Rosen",
        "display_name": "Amit",
        "gender": "male",
        "age": 31,
        "bio": "Autistic and proud. Software developer who speaks fluent sarcasm and Python. Looking for genuine connections, not small talk.",
        "tags": ["autism", "neurodivergent"],
        "interests": ["Coding", "Gaming", "Sci-Fi", "Photography", "Coffee"],
        "mood": "lowEnergy",
        "prompt_id": "perfectSunday",
        "prompt_answer": "Uninterrupted coding session, takeout, and zero social obligations",
        "picture_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=500&fit=crop",
        "city": "Tel Aviv",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "I'm not being rude, I'm being direct! Also, I give the best honest feedback.",
        "preferred_times": ["night"],
        "response_pace": "slow",
        "date_pace": "virtual",
        "time_notes": "I'm a night owl and prefer texting over calls",
    },
    # 9. Oren - Beer Sheva, veteran with PTSD
    {
        "username": f"{MOCK_USER_PREFIX}oren",
        "email": "oren@nomi.app",
        "first_name": "Oren",
        "last_name": "Peretz",
        "display_name": "Oren",
        "gender": "male",
        "age": 34,
        "bio": "IDF veteran navigating life with PTSD. Desert hiking enthusiast and amateur astronomer. The Negev sky at night is my therapy.",
        "tags": ["mentalHealth", "acquired"],
        "interests": ["Hiking", "Astronomy", "Photography", "Meditation", "Fitness"],
        "mood": "adventurous",
        "prompt_id": "dontLetStop",
        "prompt_answer": "Exploring every crater and trail in the Negev - some days are harder, but the views are worth it",
        "picture_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&h=500&fit=crop",
        "city": "Beer Sheva",
        "looking_for_genders": ["female"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "Learning to ask for help when I need it - that took more courage than anything",
        "preferred_times": ["morning", "evening"],
        "response_pace": "moderate",
        "date_pace": "slow",
        "time_notes": "Crowded places can be overwhelming, so I prefer quieter settings",
    },
    # 10. Yael - Netanya, chronic pain warrior
    {
        "username": f"{MOCK_USER_PREFIX}yael",
        "email": "yael@nomi.app",
        "first_name": "Yael",
        "last_name": "Mizrachi",
        "display_name": "Yael",
        "gender": "female",
        "age": 25,
        "bio": "Living with fibromyalgia. Beach lover who takes life one spoon at a time. Looking for someone patient who understands that plans might change.",
        "tags": ["chronicIllness", "invisible"],
        "interests": ["Beach", "Art", "Reading", "Movies", "Cats"],
        "mood": "lowEnergy",
        "prompt_id": "wishPeopleKnew",
        "prompt_answer": "Just because I look fine doesn't mean I'm not in pain - but I've got great coping skills!",
        "picture_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=500&fit=crop",
        "city": "Netanya",
        "looking_for_genders": ["male", "female"],
        "relationship_types": ["serious", "friends"],
        "ask_me_prompt_id": "dontLetStop",
        "ask_me_answer": "Spending hours watching sunsets on the Netanya promenade - I just bring extra cushions!",
        "preferred_times": ["afternoon"],
        "response_pace": "variable",
        "date_pace": "slow",
        "time_notes": "My energy is unpredictable, so flexibility is key 💜",
    },
    # 11. Eyal - Ramat Gan, ADHD entrepreneur
    {
        "username": f"{MOCK_USER_PREFIX}eyal",
        "email": "eyal@nomi.app",
        "first_name": "Eyal",
        "last_name": "Aharoni",
        "display_name": "Eyal",
        "gender": "male",
        "age": 29,
        "bio": "ADHD brain in a neurotypical world. Serial entrepreneur with 5 unfinished projects. My superpower? Hyperfocus on things I love.",
        "tags": ["neurodivergent"],
        "interests": ["Startups", "Coffee", "Music", "Travel", "Dogs"],
        "mood": "chatty",
        "prompt_id": "laughMost",
        "prompt_answer": "When I find 47 browser tabs open and can't remember why I opened any of them",
        "picture_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&h=500&fit=crop",
        "city": "Ramat Gan",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "I can learn a new skill in a weekend... and forget it exists by Monday 😅",
        "preferred_times": ["flexible"],
        "response_pace": "variable",
        "date_pace": "ready",
        "time_notes": "I might reply instantly or in 3 days - it's not you, it's my brain!",
    },
    # 12. Michal - Jerusalem, hard of hearing social worker
    {
        "username": f"{MOCK_USER_PREFIX}michal",
        "email": "michal@nomi.app",
        "first_name": "Michal",
        "last_name": "Stern",
        "display_name": "Michal",
        "gender": "female",
        "age": 33,
        "bio": "Hard of hearing social worker passionate about accessibility. I wear hearing aids and read lips like a pro. Love Jerusalem's old city vibes.",
        "tags": ["deafHoh"],
        "interests": ["Social Justice", "History", "Wine", "Cooking", "Dancing"],
        "mood": "open",
        "prompt_id": "convinced",
        "prompt_answer": "The best hummus in Israel is still waiting to be discovered (and I'll find it)",
        "picture_url": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=500&fit=crop",
        "city": "Jerusalem",
        "looking_for_genders": ["male"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "How we look out for each other and celebrate every small victory together",
        "preferred_times": ["evening"],
        "response_pace": "moderate",
        "date_pace": "flexible",
        "time_notes": "Video calls preferred - I like to see faces when we chat",
    },
    # 13. Noam - Eilat, mobility aid user
    {
        "username": f"{MOCK_USER_PREFIX}noam",
        "email": "noam@nomi.app",
        "first_name": "Noam",
        "last_name": "Biton",
        "display_name": "Noam",
        "gender": "male",
        "age": 27,
        "bio": "Crutches user living my best life in Eilat. Scuba diving instructor and beach bum. Disability doesn't stop me from exploring underwater worlds.",
        "tags": ["mobility"],
        "interests": ["Scuba Diving", "Beach", "Photography", "Music", "Travel"],
        "mood": "adventurous",
        "prompt_id": "coolestThing",
        "prompt_answer": "I became a certified adaptive scuba instructor - the Red Sea is my playground!",
        "picture_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&h=500&fit=crop",
        "city": "Eilat",
        "looking_for_genders": ["female", "male", "nonbinary"],
        "relationship_types": ["casual", "friends"],
        "ask_me_prompt_id": "superpower",
        "ask_me_answer": "I can spot dolphins before anyone else - comes with spending so much time in the water!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
        "date_pace": "ready",
    },
    # 14. Roni - Tel Aviv, trans advocate
    {
        "username": f"{MOCK_USER_PREFIX}roni",
        "email": "roni@nomi.app",
        "first_name": "Roni",
        "last_name": "Segal",
        "display_name": "Roni",
        "gender": "nonbinary",
        "age": 24,
        "bio": "Trans and proud. DJ by night, graphic designer by day. Living authentically in the heart of Tel Aviv's LGBTQ+ scene.",
        "tags": ["mentalHealth"],
        "interests": ["Music", "Art", "Dancing", "Fashion", "LGBTQ+ Advocacy"],
        "mood": "chatty",
        "prompt_id": "proudOf",
        "prompt_answer": "Finally living as my authentic self - every day is a celebration of who I really am",
        "picture_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&h=500&fit=crop",
        "city": "Tel Aviv",
        "looking_for_genders": ["male", "female", "nonbinary"],
        "relationship_types": ["casual", "friends", "serious"],
        "ask_me_prompt_id": "loveAboutCommunity",
        "ask_me_answer": "The chosen family we create - they show up for each other no matter what",
        "preferred_times": ["night", "evening"],
        "response_pace": "quick",
        "date_pace": "flexible",
    },
    # 15. Gil - Petah Tikva, blind programmer
    {
        "username": f"{MOCK_USER_PREFIX}gil",
        "email": "gil@nomi.app",
        "first_name": "Gil",
        "last_name": "Dayan",
        "display_name": "Gil",
        "gender": "male",
        "age": 30,
        "bio": "Legally blind software engineer. I code with screen readers and debug with determination. Looking for someone who appreciates tech humor and bad puns.",
        "tags": ["blindLowVision"],
        "interests": ["Coding", "Podcasts", "Board Games", "Coffee", "Stand-up Comedy"],
        "mood": "chatty",
        "prompt_id": "laughMost",
        "prompt_answer": "When people ask if I need help crossing the street... inside a building",
        "picture_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=500&fit=crop",
        "city": "Petah Tikva",
        "looking_for_genders": ["female"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "Blind people can be independent! I live alone, work in tech, and make great coffee",
        "preferred_times": ["evening"],
        "response_pace": "moderate",
        "date_pace": "slow",
        "time_notes": "Voice notes are my love language 🎙️",
    },
    # 16. Eden - Ashdod, diabetic athlete
    {
        "username": f"{MOCK_USER_PREFIX}eden",
        "email": "eden@nomi.app",
        "first_name": "Eden",
        "last_name": "Hadad",
        "display_name": "Eden",
        "gender": "female",
        "age": 23,
        "bio": "Type 1 diabetic marathon runner. My CGM is my best friend. Looking for someone who won't freak out when I check my blood sugar at dinner.",
        "tags": ["chronicIllness", "invisible"],
        "interests": ["Running", "Fitness", "Nutrition", "Travel", "Dogs"],
        "mood": "adventurous",
        "prompt_id": "dontLetStop",
        "prompt_answer": "Running marathons - I just carry extra snacks and my insulin pump cheers me on",
        "picture_url": "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=400&h=500&fit=crop",
        "city": "Ashdod",
        "looking_for_genders": ["male"],
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "Completing my first marathon while managing my blood sugar perfectly the whole race!",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "quick",
        "date_pace": "ready",
    },
    # 17. Tomer - Tiberias, anxiety warrior
    {
        "username": f"{MOCK_USER_PREFIX}tomer",
        "email": "tomer@nomi.app",
        "first_name": "Tomer",
        "last_name": "Almog",
        "display_name": "Tomer",
        "gender": "male",
        "age": 28,
        "bio": "Living with anxiety, but it doesn't define me. Tour guide at the Sea of Galilee. History nerd who knows every hidden spot in the north.",
        "tags": ["mentalHealth"],
        "interests": ["History", "Hiking", "Photography", "Cooking", "Reading"],
        "mood": "open",
        "prompt_id": "perfectSunday",
        "prompt_answer": "Sunrise kayak on the Kinneret, brunch in Tiberias, and a quiet afternoon with a book",
        "picture_url": "https://images.unsplash.com/photo-1504257432389-52343af06ae3?w=400&h=500&fit=crop",
        "city": "Tiberias",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "Canceling plans isn't personal - sometimes I just need a quiet recharge day",
        "preferred_times": ["morning", "afternoon"],
        "response_pace": "slow",
        "date_pace": "slow",
        "time_notes": "I need advance notice for plans - spontaneity isn't my friend",
    },
    # 18. Liora - Haifa, dyslexic artist
    {
        "username": f"{MOCK_USER_PREFIX}liora",
        "email": "liora@nomi.app",
        "first_name": "Liora",
        "last_name": "Nahmani",
        "display_name": "Liora",
        "gender": "female",
        "age": 26,
        "bio": "Dyslexic artist who thinks in pictures. My paintings are in galleries across Haifa. Words are hard, but colors speak volumes.",
        "tags": ["neurodivergent", "cognitive"],
        "interests": ["Art", "Museums", "Coffee", "Fashion", "Photography"],
        "mood": "open",
        "prompt_id": "superpower",
        "prompt_answer": "I see patterns and connections others miss - my brain is wired for creativity!",
        "picture_url": "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=400&h=500&fit=crop",
        "city": "Haifa",
        "looking_for_genders": ["male", "female"],
        "relationship_types": ["serious", "casual"],
        "ask_me_prompt_id": "coolestThing",
        "ask_me_answer": "My art was featured in the Haifa Museum of Art - took years but worth every moment!",
        "preferred_times": ["afternoon", "evening"],
        "response_pace": "moderate",
        "date_pace": "flexible",
        "time_notes": "I prefer voice notes over text - easier for me to express myself 🎨",
    },
    # 19. Matan - Tel Aviv, cerebral palsy
    {
        "username": f"{MOCK_USER_PREFIX}matan",
        "email": "matan@nomi.app",
        "first_name": "Matan",
        "last_name": "Ofer",
        "display_name": "Matan",
        "gender": "male",
        "age": 32,
        "bio": "Cerebral palsy since birth. Stand-up comedian who jokes about disability. If you can't laugh at life, what's the point? Also, I make great shakshuka.",
        "tags": ["mobility", "speechLanguage"],
        "interests": ["Comedy", "Cooking", "Movies", "Gaming", "Writing"],
        "mood": "chatty",
        "prompt_id": "laughMost",
        "prompt_answer": "When strangers assume I'm drunk - my walk is just naturally fabulous",
        "picture_url": "https://images.unsplash.com/photo-1463453091185-61582044d556?w=400&h=500&fit=crop",
        "city": "Tel Aviv",
        "looking_for_genders": ["female"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "proudOf",
        "ask_me_answer": "My first sold-out comedy show! Turns out disability humor is universally relatable",
        "preferred_times": ["evening", "night"],
        "response_pace": "moderate",
        "date_pace": "ready",
        "time_notes": "My speech might be slower, but my wit is lightning fast ⚡",
    },
    # 20. Inbar - Rehovot, lupus warrior
    {
        "username": f"{MOCK_USER_PREFIX}inbar",
        "email": "inbar@nomi.app",
        "first_name": "Inbar",
        "last_name": "Vaknin",
        "display_name": "Inbar",
        "gender": "female",
        "age": 28,
        "bio": "Living with lupus and loving life anyway. Researcher at Weizmann Institute. Science by day, Netflix by night. Looking for my lab partner in life.",
        "tags": ["chronicIllness", "invisible", "caregiver"],
        "interests": ["Science", "Reading", "Movies", "Cooking", "Nature"],
        "mood": "lowEnergy",
        "prompt_id": "perfectSunday",
        "prompt_answer": "Late morning brunch, a documentary, and absolutely no plans - recovery day goals",
        "picture_url": "https://images.unsplash.com/photo-1485893226355-9a1c32a0c81e?w=400&h=500&fit=crop",
        "city": "Rehovot",
        "looking_for_genders": ["male"],
        "relationship_types": ["serious"],
        "ask_me_prompt_id": "wishPeopleKnew",
        "ask_me_answer": "Autoimmune diseases are unpredictable - but so is life, and I've learned to roll with it",
        "preferred_times": ["afternoon"],
        "response_pace": "variable",
        "date_pace": "slow",
        "time_notes": "Sun exposure is tricky for me, so indoor or evening dates are best 🌙",
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