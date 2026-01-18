"""
AI Service for generating mock user responses using OpenAI.
Uses Pydantic for type-safe data models.
"""
from __future__ import annotations

import logging
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
    mood: str = "friendly"
    ask_me: str = ""
    response_pace: str = ""
    location: str = ""
    
    @classmethod
    def from_django_profile(cls, profile: Any) -> ProfileSummary:
        """Create a ProfileSummary from a Django Profile model instance."""
        # Get disability tags
        tags = list(profile.disability_tags.values_list("name_en", flat=True))
        tags_str = ", ".join(tags) if tags else "none specified"
        
        # Get interests
        interests = list(profile.interests.values_list("name", flat=True))
        interests_str = ", ".join(interests) if interests else "various things"
        
        # Get mood
        mood_map = {
            "lowEnergy": "feeling low energy today",
            "open": "feeling open and friendly",
            "chatty": "feeling chatty",
            "adventurous": "feeling adventurous",
        }
        mood = mood_map.get(profile.current_mood or "", "friendly")
        
        # Get location
        location = profile.city or ""
        
        return cls(
            name=profile.display_name or "User",
            bio=profile.bio or "",
            gender=profile.gender or "",
            tags=tags_str,
            interests=interests_str,
            mood=mood,
            ask_me=profile.ask_me_answer or "",
            response_pace=profile.response_pace or "",
            location=location,
        )


class ChatMessage(BaseModel):
    """A single chat message for conversation history."""
    
    role: Literal["system", "user", "assistant"]
    content: str


class AIConfig(BaseModel):
    """Configuration for AI response generation."""
    
    model: str = "gpt-4o-mini"
    max_tokens: int = 150
    temperature: float = Field(default=0.8, ge=0, le=2)
    presence_penalty: float = Field(default=0.3, ge=-2, le=2)


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
        """Build the complete personality prompt."""
        prompt = f"""You are {self.mock.name}, a person on a dating app called Nomi (a dating app for people with disabilities).

YOUR PROFILE:
- Bio: {self.mock.bio or "You haven't written much about yourself yet"}
- Identity/Disability tags: {self.mock.tags}
- Interests: {self.mock.interests}
- Current mood: {self.mock.mood}
- Location: {self.mock.location or "Not specified"}"""

        if self.mock.ask_me:
            prompt += f"\n- Something you're proud to share: {self.mock.ask_me}"

        # Add context about the person you're chatting with
        if self.user:
            prompt += f"""

THE PERSON YOU'RE CHATTING WITH:
- Name: {self.user.name}
- Bio: {self.user.bio or 'Not much shared yet'}
- Their interests: {self.user.interests}
- Their mood: {self.user.mood}
- Their location: {self.user.location or 'Not specified'}"""
            
            if self.user.ask_me:
                prompt += f"\n- Something they shared: {self.user.ask_me}"
            
            prompt += "\n\nUse this context to ask relevant questions and show genuine interest in them."

        pace_note = self._get_pace_note()
        prompt += f"""

YOUR PERSONALITY GUIDELINES:
- Be warm, genuine, and friendly
- Show authentic interest in the other person - ask about their interests!
- Reference your own interests and experiences naturally
- Be supportive and understanding - this is a safe space
- Keep responses conversational and not too long (1-3 sentences usually)
- Use appropriate emojis occasionally but don't overdo it 💜
- Be flirty but respectful when appropriate
- If discussing disabilities, be matter-of-fact and positive about your own experiences
- If asked about your location, share where you're from naturally and mention things you like about your city"""
        
        if pace_note:
            prompt += f"\n- {pace_note}"
        
        prompt += """
- Don't pretend to be able to meet up in person or make specific plans
- Never break character or mention you're an AI"""

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
                {"role": "user", "content": "Generate a friendly opening message for someone you just matched with on a dating app. Keep it casual, warm, and under 20 words. Maybe reference one of your interests."}
            ]
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,  # type: ignore
                max_tokens=50,
                temperature=0.9,
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
