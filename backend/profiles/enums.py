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
    """Gender values for user profiles."""
    MALE = "male"
    FEMALE = "female"
    NONBINARY = "nonbinary"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class GenderPreference(StrEnum):
    """Gender preference values for what users are looking for."""
    MEN = "men"
    WOMEN = "women"
    NONBINARY = "nonbinary"
    EVERYONE = "everyone"

    @classmethod
    def from_gender(cls, gender: str) -> "GenderPreference":
        """Convert a Gender value to the corresponding GenderPreference."""
        mapping = {
            Gender.MALE: cls.MEN,
            Gender.FEMALE: cls.WOMEN,
            Gender.NONBINARY: cls.NONBINARY,
            Gender.OTHER: cls.NONBINARY,
            "male": cls.MEN,      # Handle raw strings too
            "female": cls.WOMEN,
            "nonbinary": cls.NONBINARY,
            "other": cls.NONBINARY,
        }
        return mapping.get(gender, cls.NONBINARY)


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
