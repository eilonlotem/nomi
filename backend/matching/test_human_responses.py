"""
Test script to validate human-like AI response improvements.
Usage: python backend/matching/test_human_responses.py
"""
from __future__ import annotations

import os
import sys
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from matching.ai_service import (
    ProfileSummary,
    AIResponseGenerator,
    AIConfig,
    ChatMessage,
)


def test_english_response():
    """Test English language response."""
    print("\n" + "="*80)
    print("TEST 1: English Response")
    print("="*80)
    
    mock_profile = ProfileSummary(
        name="Maya",
        bio="Wheelchair user who loves adaptive yoga and photography. Looking for genuine connections.",
        tags="wheelchair user, chronic illness",
        interests="Photography, Yoga, Art, Travel, Coffee",
        response_pace="moderate",
        location="Tel Aviv",
        language="en"
    )
    
    user_profile = ProfileSummary(
        name="Alex",
        bio="Love hiking and outdoor adventures",
        interests="Hiking, Photography, Music",
        location="Tel Aviv",
        language="en"
    )
    
    conversation_history = [
        ChatMessage(role="assistant", content="hey! i saw you're into photography too 📸 what do you like to shoot?"),
        ChatMessage(role="user", content="mostly landscapes when I'm hiking. what about you?"),
    ]
    
    generator = AIResponseGenerator()
    response = generator.generate_response(
        mock_profile=mock_profile,
        user_message="mostly landscapes when I'm hiking. what about you?",
        conversation_history=conversation_history,
        real_user_profile=user_profile,
    )
    
    print(f"\nUser: mostly landscapes when I'm hiking. what about you?")
    print(f"Mock User Response: {response}")
    print("\n✓ Check: Response should be casual, 1-3 sentences, maybe ask a follow-up")
    

def test_hebrew_response():
    """Test Hebrew language response."""
    print("\n" + "="*80)
    print("TEST 2: Hebrew Response")
    print("="*80)
    
    mock_profile = ProfileSummary(
        name="מאיה",
        bio="משתמשת בכיסא גלגלים שאוהבת יוגה מותאמת וצילום. מחפשת חיבורים אמיתיים ומישהו שמעריך את הרגעים הקטנים בחיים.",
        tags="wheelchair user, chronic illness",
        interests="Photography, Yoga, Art, Travel, Coffee",
        response_pace="moderate",
        location="תל אביב",
        language="he"
    )
    
    user_profile = ProfileSummary(
        name="דני",
        bio="אוהב לטייל ולצלם טבע",
        interests="Hiking, Photography, Music",
        location="תל אביב",
        language="he"
    )
    
    conversation_history = [
        ChatMessage(role="assistant", content="היי! ראיתי שגם את/ה מצלמ/ת 📸"),
        ChatMessage(role="user", content="כן! בעיקר טבע וטיולים. את מצלמת מה?"),
    ]
    
    generator = AIResponseGenerator()
    response = generator.generate_response(
        mock_profile=mock_profile,
        user_message="כן! בעיקר טבע וטיולים. את מצלמת מה?",
        conversation_history=conversation_history,
        real_user_profile=user_profile,
    )
    
    print(f"\nUser: כן! בעיקר טבע וטיולים. את מצלמת מה?")
    print(f"Mock User Response: {response}")
    print("\n✓ Check: Response should be in Hebrew, casual, 1-3 sentences")


def test_greeting_variety():
    """Test that greetings have variety."""
    print("\n" + "="*80)
    print("TEST 3: Greeting Variety")
    print("="*80)
    
    mock_profile = ProfileSummary(
        name="Maya",
        bio="Wheelchair user who loves adaptive yoga and photography.",
        tags="wheelchair user",
        interests="Photography, Yoga, Coffee",
        response_pace="moderate",
        location="Tel Aviv",
        language="en"
    )
    
    generator = AIResponseGenerator()
    
    print("\nGenerating 5 different greetings from the same profile:")
    greetings = []
    for i in range(5):
        greeting = generator.generate_greeting(mock_profile)
        greetings.append(greeting)
        print(f"\n{i+1}. {greeting}")
    
    # Check for variety
    unique_greetings = len(set(greetings))
    print(f"\n✓ Check: Got {unique_greetings}/5 unique greetings (should be varied)")
    if unique_greetings >= 4:
        print("✓ PASS: Good variety in greetings")
    else:
        print("⚠ WARNING: Greetings may be too similar")


def test_conversation_flow():
    """Test natural conversation flow with context retention."""
    print("\n" + "="*80)
    print("TEST 4: Conversation Flow & Context Retention")
    print("="*80)
    
    mock_profile = ProfileSummary(
        name="Sarah",
        bio="Visual artist and coffee enthusiast. I paint abstract art inspired by my synesthesia.",
        tags="neurodivergent, chronic pain",
        interests="Art, Coffee, Music, Reading",
        response_pace="variable",
        location="Jerusalem",
        language="en"
    )
    
    user_profile = ProfileSummary(
        name="Jordan",
        bio="Music producer and coffee lover",
        interests="Music, Coffee, Art, Gaming",
        location="Tel Aviv",
        language="en"
    )
    
    generator = AIResponseGenerator()
    
    # Simulate a natural conversation
    conversation = [
        ("Jordan", "hey! i saw we both love coffee ☕ what's your go-to order?"),
        ("Sarah", None),  # Will be generated
        ("Jordan", "nice! i'm a simple americano person. do you paint at cafes?"),
        ("Sarah", None),  # Will be generated
        ("Jordan", "that's so cool! what colors does coffee taste like to you?"),
        ("Sarah", None),  # Will be generated
    ]
    
    history: list[ChatMessage] = []
    
    print("\nSimulated conversation:")
    print("-" * 40)
    
    for speaker, message in conversation:
        if message is None:
            # Generate Sarah's response
            response = generator.generate_response(
                mock_profile=mock_profile,
                user_message=history[-1].content if history else "",
                conversation_history=history[:-1] if history else [],
                real_user_profile=user_profile,
            )
            print(f"Sarah: {response}")
            history.append(ChatMessage(role="assistant", content=response or ""))
        else:
            print(f"{speaker}: {message}")
            if speaker == "Jordan":
                history.append(ChatMessage(role="user", content=message))
    
    print("\n✓ Check: Responses should:")
    print("  - Reference earlier topics (coffee, synesthesia)")
    print("  - Stay conversational and short")
    print("  - Show personality and interests")
    print("  - Ask follow-up questions")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("HUMAN-LIKE AI RESPONSE TESTING SUITE")
    print("="*80)
    print("\nThis script tests the improved human-like responses for mock users.")
    print("It validates: natural language, variety, context retention, and multi-language support.")
    
    try:
        test_english_response()
        test_hebrew_response()
        test_greeting_variety()
        test_conversation_flow()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80)
        print("\nReview the responses above and check that they:")
        print("✓ Use casual, natural language with contractions")
        print("✓ Are short (1-3 sentences)")
        print("✓ Show personality and emotions")
        print("✓ Ask relevant follow-up questions")
        print("✓ Remember context from earlier messages")
        print("✓ Use appropriate emojis sparingly")
        print("✓ Respond in the correct language (English/Hebrew)")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
