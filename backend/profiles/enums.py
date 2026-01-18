"""
Enums for profile-related values.
Using StrEnum to ensure type safety and prevent typos.
"""
from enum import Enum


# Python 3.9 compatible StrEnum
class StrEnum(str, Enum):
    """String enum that is compatible with Python 3.9+."""
    def __str__(self) -> str:
        return str(self.value)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.value == other
        return super().__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.value)


class Gender(StrEnum):
    """
    Gender values used for both profile gender AND preferences.
    Use the same values everywhere to avoid confusion.
    """
    MALE = "male"
    FEMALE = "female"
    NONBINARY = "nonbinary"
    OTHER = "other"
    EVERYONE = "everyone"  # Only used in preferences (looking_for.genders)


class Mood(StrEnum):
    """Current mood/energy level."""
    LOW_ENERGY = "lowEnergy"
    OPEN = "open"
    CHATTY = "chatty"
    ADVENTUROUS = "adventurous"


class ResponsePace(StrEnum):
    """How quickly a user typically responds."""
    QUICK = "quick"
    MODERATE = "moderate"
    SLOW = "slow"
    VARIABLE = "variable"


class DatePace(StrEnum):
    """Preferred dating pace."""
    READY = "ready"
    SLOW = "slow"
    VIRTUAL = "virtual"
    FLEXIBLE = "flexible"


class TimePreference(StrEnum):
    """Preferred times for dates."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"
    FLEXIBLE = "flexible"


class RelationshipType(StrEnum):
    """What kind of relationship user is looking for."""
    CASUAL = "casual"
    SERIOUS = "serious"
    FRIENDS = "friends"
    ACTIVITY = "activity"
