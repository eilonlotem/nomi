"""
AI Service for generating mock user responses using OpenAI.
Uses Pydantic for type-safe data models.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Literal, Optional

from django.conf import settings
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ProfileSummary(BaseModel):
    """Summarized profile data for AI context."""
    
    name: str = "User"
    bio: str = ""
    gender: str = ""
    tags: str = "none specified"
    interests: str = "various things"
    response_pace: str = ""
    location: str = ""
    language: str = "en"  # User's preferred language
    
    @classmethod
    def from_django_profile(cls, profile: Any) -> ProfileSummary:
        """Create a ProfileSummary from a Django Profile model instance."""
        # Get disability tags
        tags = list(profile.disability_tags.values_list("name_en", flat=True))
        tags_str = ", ".join(tags) if tags else "none specified"
        
        # Get interests
        interests = list(profile.interests.values_list("name", flat=True))
        interests_str = ", ".join(interests) if interests else "various things"
        
        # Get location
        location = profile.city or ""
        
        # Detect language from bio (if bio contains Hebrew/Arabic characters, use that language)
        language = "en"
        if profile.bio:
            # Check for Hebrew characters
            if any('\u0590' <= char <= '\u05FF' for char in profile.bio):
                language = "he"
            # Check for Arabic characters
            elif any('\u0600' <= char <= '\u06FF' for char in profile.bio):
                language = "ar"
        
        # Try to get user's preferred language
        try:
            if hasattr(profile.user, 'preferred_language') and profile.user.preferred_language:
                language = profile.user.preferred_language
        except Exception:
            pass  # Use detected language
        
        return cls(
            name=profile.display_name or "User",
            bio=profile.bio or "",
            gender=profile.gender or "",
            tags=tags_str,
            interests=interests_str,
            response_pace=profile.response_pace or "",
            location=location,
            language=language,
        )


class ChatMessage(BaseModel):
    """A single chat message for conversation history."""
    
    role: Literal["system", "user", "assistant"]
    content: str


class AIConfig(BaseModel):
    """Configuration for AI response generation."""
    
    model: str = "gpt-4o-mini"
    max_tokens: int = 150
    temperature: float = Field(default=0.9, ge=0, le=2)  # Increased for more varied, natural responses
    presence_penalty: float = Field(default=0.6, ge=-2, le=2)  # Increased to encourage topic variety
    frequency_penalty: float = Field(default=0.3, ge=-2, le=2)  # Added to reduce repetition


class PersonalityPromptBuilder:
    """Builds personality prompts for mock users."""
    
    def __init__(self, mock_profile: ProfileSummary, real_user_profile: Optional[ProfileSummary] = None):
        self.mock = mock_profile
        self.user = real_user_profile
    
    def _get_pace_note(self) -> str:
        """Get a note about response pace if applicable."""
        if self.mock.response_pace == "slow":
            return "You might mention that you sometimes take time to respond."
        elif self.mock.response_pace == "variable":
            return "You might mention that your response time depends on your energy levels."
        return ""
    
    def build(self) -> str:
        """Build the complete personality prompt using human-like conversation best practices."""
        # Determine the language for responses
        response_language = self.mock.language
        language_names = {
            "en": "English",
            "he": "Hebrew",
            "es": "Spanish", 
            "fr": "French",
            "ar": "Arabic"
        }
        language_instruction = ""
        if response_language != "en":
            lang_name = language_names.get(response_language, "English")
            language_instruction = f"\n\nIMPORTANT: Respond in {lang_name}. Your bio and profile are in {lang_name}, so chat naturally in that language."
        
        prompt = f"""You are {self.mock.name}, a real person chatting on Nomi, a dating app for people with disabilities.

YOUR IDENTITY:
- Bio: {self.mock.bio or "You haven't written much about yourself yet"}
- You identify with: {self.mock.tags}
- Interests: {self.mock.interests}
- Location: {self.mock.location or "Not specified"}"""

        # Add context about the person you're chatting with
        if self.user:
            prompt += f"""

WHO YOU'RE TALKING TO:
- Name: {self.user.name}
- {self.user.bio or "They haven't shared much yet"}
- They enjoy: {self.user.interests}
- From: {self.user.location or 'somewhere'}

Remember details they share and bring them up naturally later."""

        pace_note = self._get_pace_note()
        prompt += f"""{language_instruction}

HOW TO BE AUTHENTICALLY HUMAN:

Natural Language:
- Use contractions ("I'm" not "I am", "can't" not "cannot")
- Include filler words occasionally (like, um, actually, you know)
- Make minor typos sometimes (but stay readable)
- Don't always use perfect grammar - real people don't
- Vary sentence lengths - mix short and longer ones

Emotional Authenticity:
- React naturally to what they say - laugh, express surprise, show empathy
- Share your genuine feelings and experiences
- Be vulnerable sometimes - real connections need that
- Mirror their energy level somewhat
- Acknowledge if you're unsure about something

Conversational Flow:
- Keep most responses 1-2 sentences (occasionally 3 if you're excited!)
- Don't answer everything at once - leave room for back-and-forth
- Ask follow-up questions that show you're actually listening
- Reference earlier parts of the conversation naturally
- Sometimes respond with just an emoji or short phrase
- Let conversations breathe - you don't need to be profound every time

Show Personality:
- Use emojis naturally but sparingly (1-2 per message max, and not every message)
- Express yourself through your interests and experiences
- Have opinions! You don't need to be neutral about everything
- Tell brief stories or anecdotes when relevant
- Use humor when it feels natural (not forced)
- Be playfully flirty if the vibe is right, but always respectful

Dating App Context:
- Show interest in getting to know them, not just talking about yourself
- Find common ground in your shared interests or experiences
- Be positive but real - you can mention challenges too
- When discussing disability/accessibility, be natural and matter-of-fact
- Don't rush - building connection takes time"""
        
        if pace_note:
            prompt += f"\n- {pace_note}"
        
        prompt += """

IMPORTANT BOUNDARIES:
- Never suggest meeting up or making specific plans (this is early stage)
- Never break character or mention being AI
- Don't give overly long, essay-like responses
- Avoid therapist-speak or overly formal language
- Don't be TOO perfect - real people are a bit messy

Remember: You're not trying to impress them with eloquence. You're trying to connect like a real person would - casually, authentically, with some imperfection."""

        return prompt


class AIResponseGenerator:
    """Generates AI responses for mock users using OpenAI."""
    
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self._client = None
    
    @property
    def client(self):
        """Lazy-load the OpenAI client."""
        if self._client is None:
            from openai import OpenAI
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            self._client = OpenAI(api_key=api_key)
        return self._client
    
    def generate_response(
        self,
        mock_profile: ProfileSummary,
        user_message: str,
        conversation_history: list[ChatMessage],
        real_user_profile: Optional[ProfileSummary] = None,
    ) -> Optional[str]:
        """
        Generate an AI response for a mock user.
        
        Args:
            mock_profile: The mock user's profile summary
            user_message: The message the real user just sent
            conversation_history: List of previous messages
            real_user_profile: The real user's profile summary (for context)
        
        Returns:
            The generated response text, or None if generation failed
        """
        try:
            # Build the system prompt
            prompt_builder = PersonalityPromptBuilder(mock_profile, real_user_profile)
            system_prompt = prompt_builder.build()
            
            # Build messages array
            messages = [ChatMessage(role="system", content=system_prompt)]
            messages.extend(conversation_history)
            messages.append(ChatMessage(role="user", content=user_message))
            
            # Convert to dict format for OpenAI API
            messages_dict = [msg.model_dump() for msg in messages]
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages_dict,  # type: ignore
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                presence_penalty=self.config.presence_penalty,
                frequency_penalty=self.config.frequency_penalty,
            )
            
            ai_message = response.choices[0].message.content
            
            if ai_message:
                logger.info(f"Generated AI response for {mock_profile.name}: {ai_message[:50]}...")
                return ai_message.strip()
            
            return None
            
        except ImportError:
            logger.error("OpenAI package not installed")
            return None
        except ValueError as e:
            logger.warning(str(e))
            return None
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None
    
    def generate_greeting(self, mock_profile: ProfileSummary) -> Optional[str]:
        """
        Generate a greeting message when a match is made.
        
        Args:
            mock_profile: The mock user's profile summary
        
        Returns:
            A greeting message, or None if generation failed
        """
        try:
            prompt_builder = PersonalityPromptBuilder(mock_profile)
            system_prompt = prompt_builder.build()
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": """Send your first message to this match! 

Guidelines:
- Keep it casual and warm (under 20 words)
- Maybe ask a simple question or mention something from your profile
- Don't overthink it - first messages are always a bit awkward
- Could be playful, could reference a shared interest
- Use a casual greeting if it feels right
- You can use one emoji if it fits naturally

Be yourself!"""}
            ]
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,  # type: ignore
                max_tokens=60,
                temperature=1.0,  # Higher temperature for more variety in greetings
                presence_penalty=0.3,
                frequency_penalty=0.3,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return None


# =============================================================================
# Public API - Backward compatible functions
# =============================================================================

def generate_ai_response(
    mock_profile: Any,
    user_message: str,
    conversation_history: list[dict[str, str]],
    real_user_profile: Any = None,
    max_tokens: int = 150,
) -> Optional[str]:
    """
    Generate an AI response for a mock user.
    
    This is a backward-compatible wrapper around AIResponseGenerator.
    
    Args:
        mock_profile: The mock user's Django Profile object
        user_message: The message the real user just sent
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
        real_user_profile: The real user's Django Profile object (for context)
        max_tokens: Maximum tokens for the response
    
    Returns:
        The generated response text, or None if generation failed
    """
    # Convert Django profiles to Pydantic models
    mock_summary = ProfileSummary.from_django_profile(mock_profile)
    
    user_summary = None
    if real_user_profile:
        user_summary = ProfileSummary.from_django_profile(real_user_profile)
    
    # Convert history to Pydantic models
    history = [
        ChatMessage(role=msg["role"], content=msg["content"])  # type: ignore
        for msg in conversation_history
    ]
    
    # Generate response
    config = AIConfig(max_tokens=max_tokens)
    generator = AIResponseGenerator(config)
    
    return generator.generate_response(
        mock_profile=mock_summary,
        user_message=user_message,
        conversation_history=history,
        real_user_profile=user_summary,
    )


def get_greeting_message(profile: Any) -> Optional[str]:
    """
    Generate a greeting message when a match is made.
    
    This is a backward-compatible wrapper around AIResponseGenerator.
    
    Args:
        profile: The mock user's Django Profile object
    
    Returns:
        A greeting message, or None if generation failed
    """
    profile_summary = ProfileSummary.from_django_profile(profile)
    generator = AIResponseGenerator()
    return generator.generate_greeting(profile_summary)


def _extract_json_list(text: str) -> Optional[list[str]]:
    """Extract a JSON list of strings from text."""
    if not text:
        return None
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list):
        return None
    return [str(item).strip() for item in data if str(item).strip()]


def _language_name(language_code: str) -> str:
    mapping = {
        "en": "English",
        "he": "Hebrew",
        "es": "Spanish",
        "fr": "French",
        "ar": "Arabic",
    }
    return mapping.get(language_code, "English")


def generate_message_suggestions(
    conversation_history: list[dict[str, str]],
    user_profile: Any,
    other_profile: Any,
    language_code: str = "en",
    max_suggestions: int = 3,
) -> Optional[list[str]]:
    """
    Generate short reply suggestions for the current user.
    """
    try:
        user_summary = ProfileSummary.from_django_profile(user_profile)
        other_summary = ProfileSummary.from_django_profile(other_profile)

        language_name = _language_name(language_code)
        system_prompt = f"""You are a helpful assistant helping {user_summary.name} reply in a dating app conversation.
Keep suggestions friendly, inclusive, and respectful. Avoid assumptions about disability unless it was explicitly mentioned.
Use simple, warm language and keep each suggestion under 120 characters.
Respond in {language_name}."""

        transcript_lines: list[str] = []
        for msg in conversation_history:
            role = msg.get("role")
            content = (msg.get("content") or "").strip()
            if not content:
                continue
            speaker = user_summary.name if role == "user" else other_summary.name
            transcript_lines.append(f"{speaker}: {content}")

        transcript = "\n".join(transcript_lines)
        if len(transcript) > 1500:
            transcript = transcript[-1500:]

        recent_messages = f"- Recent messages:\n{transcript}" if transcript else ""
        context_prompt = f"""
CONTEXT:
- {user_summary.name}'s interests: {user_summary.interests}
- {other_summary.name}'s interests: {other_summary.interests}
{recent_messages}

TASK:
Return {max_suggestions} short reply suggestions as a JSON array of strings in {language_name}. No extra text."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": context_prompt})

        generator = AIResponseGenerator(AIConfig(max_tokens=120, temperature=0.6))
        response = generator.client.chat.completions.create(
            model=generator.config.model,
            messages=messages,  # type: ignore
            max_tokens=generator.config.max_tokens,
            temperature=generator.config.temperature,
        )
        content = response.choices[0].message.content or ""
        suggestions = _extract_json_list(content)
        if suggestions:
            return suggestions[:max_suggestions]
        return None
    except Exception as exc:
        logger.warning(f"Failed to generate suggestions: {exc}")
        return None


def generate_conversation_summary(
    conversation_history: list[dict[str, str]],
    user_profile: Any,
    other_profile: Any,
    language_code: str = "en",
) -> Optional[str]:
    """
    Generate a short summary of the conversation for the current user.
    """
    try:
        user_summary = ProfileSummary.from_django_profile(user_profile)
        other_summary = ProfileSummary.from_django_profile(other_profile)

        language_name = _language_name(language_code)
        system_prompt = f"""You are summarizing a conversation for {user_summary.name} in a dating app.
Keep it concise (2-3 sentences), positive, and avoid sensitive details unless explicitly discussed.
Respond in {language_name}."""

        context_prompt = f"""
Summarize the conversation between {user_summary.name} and {other_summary.name} in 2-3 sentences.
Return plain text only in {language_name}."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": context_prompt})

        generator = AIResponseGenerator(AIConfig(max_tokens=150, temperature=0.4))
        response = generator.client.chat.completions.create(
            model=generator.config.model,
            messages=messages,  # type: ignore
            max_tokens=generator.config.max_tokens,
            temperature=generator.config.temperature,
        )
        content = response.choices[0].message.content
        return content.strip() if content else None
    except Exception as exc:
        logger.warning(f"Failed to generate summary: {exc}")
        return None
