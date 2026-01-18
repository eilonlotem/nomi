"""
Matching Algorithm for Nomi Dating App.

This module implements a comprehensive compatibility scoring system that
considers multiple dimensions of user profiles to suggest optimal matches.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from django.db.models import Q, QuerySet

from profiles.enums import Gender, Mood

if TYPE_CHECKING:
    from profiles.models import LookingFor, Profile
    from users.models import User


@dataclass
class CompatibilityBreakdown:
    """Detailed breakdown of compatibility scores between two users."""
    
    # Individual component scores (0-100 each)
    shared_tags_score: float = 0.0
    shared_interests_score: float = 0.0
    distance_score: float = 0.0
    age_compatibility_score: float = 0.0
    gender_match_score: float = 0.0
    relationship_type_score: float = 0.0
    mood_compatibility_score: float = 0.0
    pace_compatibility_score: float = 0.0
    time_preferences_score: float = 0.0
    
    # Metadata
    shared_tags_count: int = 0
    shared_interests_count: int = 0
    distance_km: Optional[float] = None
    
    # Weights for each component (can be customized)
    weights: dict[str, float] = field(default_factory=lambda: {
        "shared_tags": 0.20,       # Disability tags are very important
        "shared_interests": 0.15,  # Common interests matter
        "distance": 0.15,          # Location proximity
        "age": 0.10,               # Age preferences
        "gender": 0.10,            # Gender preferences (binary: match or not)
        "relationship_type": 0.10, # What they're looking for
        "mood": 0.08,              # Current mood/energy
        "pace": 0.07,              # Response and dating pace
        "time_preferences": 0.05, # When they prefer to meet
    })
    
    @property
    def total_score(self) -> int:
        """Calculate weighted total compatibility score (0-100)."""
        weighted_sum = (
            self.shared_tags_score * self.weights["shared_tags"] +
            self.shared_interests_score * self.weights["shared_interests"] +
            self.distance_score * self.weights["distance"] +
            self.age_compatibility_score * self.weights["age"] +
            self.gender_match_score * self.weights["gender"] +
            self.relationship_type_score * self.weights["relationship_type"] +
            self.mood_compatibility_score * self.weights["mood"] +
            self.pace_compatibility_score * self.weights["pace"] +
            self.time_preferences_score * self.weights["time_preferences"]
        )
        return min(100, max(0, round(weighted_sum)))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "total_score": self.total_score,
            "breakdown": {
                "shared_tags": round(self.shared_tags_score, 1),
                "shared_interests": round(self.shared_interests_score, 1),
                "distance": round(self.distance_score, 1),
                "age": round(self.age_compatibility_score, 1),
                "gender": round(self.gender_match_score, 1),
                "relationship_type": round(self.relationship_type_score, 1),
                "mood": round(self.mood_compatibility_score, 1),
                "pace": round(self.pace_compatibility_score, 1),
                "time_preferences": round(self.time_preferences_score, 1),
            },
            "metadata": {
                "shared_tags_count": self.shared_tags_count,
                "shared_interests_count": self.shared_interests_count,
                "distance_km": round(self.distance_km, 1) if self.distance_km else None,
            }
        }


class MatchingAlgorithm:
    """
    Core matching algorithm that calculates compatibility between users.
    
    The algorithm considers multiple dimensions:
    - Shared disability/identity tags
    - Shared interests
    - Geographic distance
    - Age preferences
    - Gender preferences
    - Relationship type preferences
    - Current mood/energy level
    - Communication and dating pace
    - Time preferences
    """
    
    # Constants for score calculations
    EARTH_RADIUS_KM = 6371.0
    MAX_RELEVANT_DISTANCE_KM = 100.0
    
    def calculate_compatibility(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
    ) -> CompatibilityBreakdown:
        """
        Calculate comprehensive compatibility between two users.
        
        Args:
            user_profile: The profile of the user looking for matches
            candidate_profile: The profile of a potential match
            
        Returns:
            CompatibilityBreakdown with all scores and metadata
        """
        breakdown = CompatibilityBreakdown()
        
        # Calculate individual component scores
        self._calculate_shared_tags_score(user_profile, candidate_profile, breakdown)
        self._calculate_shared_interests_score(user_profile, candidate_profile, breakdown)
        self._calculate_distance_score(user_profile, candidate_profile, breakdown)
        self._calculate_age_compatibility(user_profile, candidate_profile, breakdown)
        self._calculate_gender_match(user_profile, candidate_profile, breakdown)
        self._calculate_relationship_type_score(user_profile, candidate_profile, breakdown)
        self._calculate_mood_compatibility(user_profile, candidate_profile, breakdown)
        self._calculate_pace_compatibility(user_profile, candidate_profile, breakdown)
        self._calculate_time_preferences_score(user_profile, candidate_profile, breakdown)
        
        return breakdown
    
    def _calculate_shared_tags_score(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
        breakdown: CompatibilityBreakdown,
    ) -> None:
        """Calculate score based on shared disability/identity tags."""
        user_tags = set(user_profile.disability_tags.values_list("id", flat=True))
        candidate_tags = set(candidate_profile.disability_tags.values_list("id", flat=True))
        
        shared_tags = user_tags & candidate_tags
        breakdown.shared_tags_count = len(shared_tags)
        
        if not user_tags and not candidate_tags:
            # Both have no tags - neutral score
            breakdown.shared_tags_score = 50.0
        elif not user_tags or not candidate_tags:
            # One has tags, one doesn't - lower score
            breakdown.shared_tags_score = 30.0
        else:
            # Use Jaccard similarity coefficient
            union_tags = user_tags | candidate_tags
            jaccard = len(shared_tags) / len(union_tags) if union_tags else 0
            
            # Boost for having at least one shared tag (important for connection)
            base_score = jaccard * 80
            shared_bonus = min(20, len(shared_tags) * 10) if shared_tags else 0
            
            breakdown.shared_tags_score = min(100, base_score + shared_bonus)
    
    def _calculate_shared_interests_score(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
        breakdown: CompatibilityBreakdown,
    ) -> None:
        """Calculate score based on shared interests."""
        user_interests = set(user_profile.interests.values_list("id", flat=True))
        candidate_interests = set(candidate_profile.interests.values_list("id", flat=True))
        
        shared_interests = user_interests & candidate_interests
        breakdown.shared_interests_count = len(shared_interests)
        
        if not user_interests and not candidate_interests:
            breakdown.shared_interests_score = 50.0
        elif not user_interests or not candidate_interests:
            breakdown.shared_interests_score = 40.0
        else:
            # Use Jaccard similarity with bonus for shared interests
            union_interests = user_interests | candidate_interests
            jaccard = len(shared_interests) / len(union_interests) if union_interests else 0
            
            # Score based on jaccard + bonus for absolute number shared
            base_score = jaccard * 70
            shared_bonus = min(30, len(shared_interests) * 6)
            
            breakdown.shared_interests_score = min(100, base_score + shared_bonus)
    
    def _calculate_distance_score(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
        breakdown: CompatibilityBreakdown,
    ) -> None:
        """Calculate score based on geographic distance."""
        if not all([
            user_profile.latitude, user_profile.longitude,
            candidate_profile.latitude, candidate_profile.longitude
        ]):
            # No location data - neutral score
            breakdown.distance_score = 50.0
            breakdown.distance_km = None
            return
        
        # Calculate distance using Haversine formula
        distance = self._haversine_distance(
            float(user_profile.latitude), float(user_profile.longitude),
            float(candidate_profile.latitude), float(candidate_profile.longitude),
        )
        breakdown.distance_km = distance
        
        # Check user's max distance preference
        max_distance = self.MAX_RELEVANT_DISTANCE_KM
        try:
            if hasattr(user_profile, "looking_for") and user_profile.looking_for:
                max_distance = user_profile.looking_for.max_distance or self.MAX_RELEVANT_DISTANCE_KM
        except Exception:
            pass
        
        if distance <= 5:
            # Very close - perfect score
            breakdown.distance_score = 100.0
        elif distance <= max_distance:
            # Within preferred range - linear decay
            score = 100 - (distance / max_distance) * 60
            breakdown.distance_score = max(40, score)
        else:
            # Beyond preferred range - sharp penalty but not zero
            overage_ratio = (distance - max_distance) / max_distance
            breakdown.distance_score = max(10, 40 - overage_ratio * 30)
    
    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float,
    ) -> float:
        """Calculate distance between two points using Haversine formula."""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return self.EARTH_RADIUS_KM * c
    
    def _calculate_age_compatibility(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
        breakdown: CompatibilityBreakdown,
    ) -> None:
        """Calculate score based on age preferences."""
        # Get candidate's age from their profile or user model
        candidate_age = None
        if candidate_profile.date_of_birth:
            from datetime import date
            today = date.today()
            dob = candidate_profile.date_of_birth
            candidate_age = today.year - dob.year - (
                (today.month, today.day) < (dob.month, dob.day)
            )
        elif hasattr(candidate_profile, "user") and candidate_profile.user.date_of_birth:
            candidate_age = candidate_profile.user.age
        
        if candidate_age is None:
            breakdown.age_compatibility_score = 50.0
            return
        
        # Get user's age preferences
        min_age = 18
        max_age = 99
        try:
            if hasattr(user_profile, "looking_for") and user_profile.looking_for:
                min_age = user_profile.looking_for.min_age or 18
                max_age = user_profile.looking_for.max_age or 99
        except Exception:
            pass
        
        if min_age <= candidate_age <= max_age:
            # Within preferred range - calculate how central they are
            range_size = max_age - min_age
            if range_size > 0:
                center = (min_age + max_age) / 2
                distance_from_center = abs(candidate_age - center)
                normalized_distance = distance_from_center / (range_size / 2)
                # Higher score for being closer to center of preference
                breakdown.age_compatibility_score = 100 - (normalized_distance * 20)
            else:
                breakdown.age_compatibility_score = 100.0
        else:
            # Outside preferred range
            if candidate_age < min_age:
                distance_outside = min_age - candidate_age
            else:
                distance_outside = candidate_age - max_age
            
            # Gradual decay for being outside range
            breakdown.age_compatibility_score = max(0, 50 - distance_outside * 5)
    
    def _calculate_gender_match(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
        breakdown: CompatibilityBreakdown,
    ) -> None:
        """Calculate score based on gender preferences."""
        # Get candidate's gender
        candidate_gender = candidate_profile.gender
        
        # Get user's gender preferences
        preferred_genders: list[str] = []
        try:
            if hasattr(user_profile, "looking_for") and user_profile.looking_for:
                preferred_genders = user_profile.looking_for.genders or []
        except Exception:
            pass
        
        if not preferred_genders or "everyone" in preferred_genders:
            # No preference or open to everyone
            breakdown.gender_match_score = 100.0
            return
        
        if not candidate_gender:
            # Candidate hasn't specified - neutral
            breakdown.gender_match_score = 50.0
            return
        
        # Map candidate gender to preference categories
        gender_mapping = {
            "male": "men",
            "female": "women",
            "nonbinary": "nonbinary",
            "other": "nonbinary",  # Group with nonbinary for matching
        }
        
        candidate_category = gender_mapping.get(candidate_gender, candidate_gender)
        
        if candidate_category in preferred_genders:
            breakdown.gender_match_score = 100.0
        else:
            # Gender doesn't match preference - significant penalty
            breakdown.gender_match_score = 10.0
    
    def _calculate_relationship_type_score(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
        breakdown: CompatibilityBreakdown,
    ) -> None:
        """Calculate score based on relationship type preferences."""
        user_types: list[str] = []
        candidate_types: list[str] = []
        
        try:
            if hasattr(user_profile, "looking_for") and user_profile.looking_for:
                user_types = user_profile.looking_for.relationship_types or []
        except Exception:
            pass
        
        try:
            if hasattr(candidate_profile, "looking_for") and candidate_profile.looking_for:
                candidate_types = candidate_profile.looking_for.relationship_types or []
        except Exception:
            pass
        
        if not user_types or not candidate_types:
            # One or both haven't specified - neutral
            breakdown.relationship_type_score = 50.0
            return
        
        # Check for overlap in relationship types
        shared_types = set(user_types) & set(candidate_types)
        
        if shared_types:
            # Calculate score based on overlap ratio
            overlap_ratio = len(shared_types) / max(len(user_types), len(candidate_types))
            breakdown.relationship_type_score = 60 + (overlap_ratio * 40)
        else:
            # No overlap - low score but not zero (people can be flexible)
            breakdown.relationship_type_score = 25.0
    
    def _calculate_mood_compatibility(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
        breakdown: CompatibilityBreakdown,
    ) -> None:
        """Calculate score based on current mood/energy compatibility."""
        user_mood = user_profile.current_mood or ""
        candidate_mood = candidate_profile.current_mood or ""
        
        if not user_mood or not candidate_mood:
            breakdown.mood_compatibility_score = 50.0
            return
        
        # Mood compatibility matrix using enums
        # Higher scores for complementary or matching moods
        mood_compatibility = {
            (Mood.LOW_ENERGY, Mood.LOW_ENERGY): 90,    # Both low energy - understanding
            (Mood.LOW_ENERGY, Mood.OPEN): 70,          # Low + open works
            (Mood.LOW_ENERGY, Mood.CHATTY): 40,        # Mismatch
            (Mood.LOW_ENERGY, Mood.ADVENTUROUS): 30,   # Significant mismatch
            
            (Mood.OPEN, Mood.LOW_ENERGY): 70,
            (Mood.OPEN, Mood.OPEN): 85,
            (Mood.OPEN, Mood.CHATTY): 90,
            (Mood.OPEN, Mood.ADVENTUROUS): 80,
            
            (Mood.CHATTY, Mood.LOW_ENERGY): 40,
            (Mood.CHATTY, Mood.OPEN): 90,
            (Mood.CHATTY, Mood.CHATTY): 95,
            (Mood.CHATTY, Mood.ADVENTUROUS): 85,
            
            (Mood.ADVENTUROUS, Mood.LOW_ENERGY): 30,
            (Mood.ADVENTUROUS, Mood.OPEN): 80,
            (Mood.ADVENTUROUS, Mood.CHATTY): 85,
            (Mood.ADVENTUROUS, Mood.ADVENTUROUS): 100,
        }
        
        score = mood_compatibility.get((user_mood, candidate_mood), 50)
        breakdown.mood_compatibility_score = float(score)
    
    def _calculate_pace_compatibility(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
        breakdown: CompatibilityBreakdown,
    ) -> None:
        """Calculate score based on response/dating pace compatibility."""
        scores = []
        
        # Response pace compatibility
        user_response = user_profile.response_pace or ""
        candidate_response = candidate_profile.response_pace or ""
        
        if user_response and candidate_response:
            response_compat = self._get_pace_compatibility(user_response, candidate_response)
            scores.append(response_compat)
        
        # Date pace compatibility
        user_date = user_profile.date_pace or ""
        candidate_date = candidate_profile.date_pace or ""
        
        if user_date and candidate_date:
            date_compat = self._get_date_pace_compatibility(user_date, candidate_date)
            scores.append(date_compat)
        
        if scores:
            breakdown.pace_compatibility_score = sum(scores) / len(scores)
        else:
            breakdown.pace_compatibility_score = 50.0
    
    def _get_pace_compatibility(self, pace1: str, pace2: str) -> float:
        """Calculate compatibility between response paces."""
        pace_values = {
            "quick": 1,
            "moderate": 2,
            "slow": 3,
            "variable": 2.5,  # Variable is flexible
        }
        
        v1 = pace_values.get(pace1, 2)
        v2 = pace_values.get(pace2, 2)
        
        # "variable" is compatible with everything
        if "variable" in (pace1, pace2):
            return 80.0
        
        diff = abs(v1 - v2)
        if diff == 0:
            return 100.0
        elif diff <= 1:
            return 75.0
        else:
            return 50.0
    
    def _get_date_pace_compatibility(self, pace1: str, pace2: str) -> float:
        """Calculate compatibility between dating paces."""
        # Direct matches score highest
        if pace1 == pace2:
            return 100.0
        
        # Flexible is compatible with everything
        if "flexible" in (pace1, pace2):
            return 85.0
        
        # Compatible combinations
        compatible_pairs = {
            ("ready", "slow"): 60,       # Slightly mismatched but workable
            ("slow", "ready"): 60,
            ("ready", "virtual"): 50,    # Different expectations
            ("virtual", "ready"): 50,
            ("slow", "virtual"): 75,     # Both prefer to take it slow
            ("virtual", "slow"): 75,
        }
        
        return float(compatible_pairs.get((pace1, pace2), 50))
    
    def _calculate_time_preferences_score(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
        breakdown: CompatibilityBreakdown,
    ) -> None:
        """Calculate score based on time availability preferences."""
        user_times = set(user_profile.preferred_times or [])
        candidate_times = set(candidate_profile.preferred_times or [])
        
        if not user_times or not candidate_times:
            breakdown.time_preferences_score = 50.0
            return
        
        # "flexible" matches with everything
        if "flexible" in user_times or "flexible" in candidate_times:
            breakdown.time_preferences_score = 90.0
            return
        
        shared_times = user_times & candidate_times
        
        if shared_times:
            overlap_ratio = len(shared_times) / min(len(user_times), len(candidate_times))
            breakdown.time_preferences_score = 60 + (overlap_ratio * 40)
        else:
            # No overlap but they might be adjacent
            # morning<->afternoon, afternoon<->evening, evening<->night
            adjacent_pairs = [
                ("morning", "afternoon"),
                ("afternoon", "evening"),
                ("evening", "night"),
            ]
            
            for t1 in user_times:
                for t2 in candidate_times:
                    if (t1, t2) in adjacent_pairs or (t2, t1) in adjacent_pairs:
                        breakdown.time_preferences_score = 45.0
                        return
            
            breakdown.time_preferences_score = 25.0


class CandidateFilter:
    """
    Filters candidates based on hard requirements before scoring.
    This ensures users only see relevant matches.
    """
    
    EARTH_RADIUS_KM = 6371.0
    
    def is_relevant(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
    ) -> bool:
        """
        Check if a candidate meets the basic requirements to be shown.
        
        Checks:
        - Gender preference match (both ways)
        - Age within preferences (both ways)
        - Distance within max preference
        
        Returns:
            True if candidate should be shown, False otherwise
        """
        # Check gender preferences (mutual)
        if not self._check_gender_preferences(user_profile, candidate_profile):
            return False
        
        # Check age preferences (mutual)
        if not self._check_age_preferences(user_profile, candidate_profile):
            return False
        
        # Check distance preference
        if not self._check_distance_preference(user_profile, candidate_profile):
            return False
        
        return True
    
    def _check_gender_preferences(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
    ) -> bool:
        """Check if gender preferences match in both directions."""
        # What the user is looking for
        user_prefs: list[str] = []
        try:
            if hasattr(user_profile, "looking_for"):
                looking_for = user_profile.looking_for
                if looking_for:
                    user_prefs = looking_for.genders or []
        except Exception:
            pass
        
        # What the candidate is looking for
        candidate_prefs: list[str] = []
        try:
            if hasattr(candidate_profile, "looking_for"):
                looking_for = candidate_profile.looking_for
                if looking_for:
                    candidate_prefs = looking_for.genders or []
        except Exception:
            pass
        
        # Check if user wants to see this candidate's gender
        candidate_gender = candidate_profile.gender or ""
        if user_prefs and Gender.EVERYONE not in user_prefs:
            # If user has specific preferences, candidate must match
            if not candidate_gender:
                # Candidate has no gender set - don't show to users with specific prefs
                return False
            # Direct comparison - no conversion needed since we use same values
            if candidate_gender not in user_prefs:
                return False
        
        # Check if candidate wants to see the user's gender
        user_gender = user_profile.gender or ""
        if candidate_prefs and Gender.EVERYONE not in candidate_prefs:
            # If candidate has specific preferences, user must match
            if not user_gender:
                # User has no gender set - don't match with candidates who have prefs
                return False
            # Direct comparison - no conversion needed since we use same values
            if user_gender not in candidate_prefs:
                return False
        
        return True
    
    def _check_age_preferences(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
    ) -> bool:
        """Check if age preferences match in both directions."""
        from datetime import date
        
        # Get user's age
        user_age = None
        if user_profile.date_of_birth:
            dob = user_profile.date_of_birth
            today = date.today()
            user_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        elif hasattr(user_profile, "user") and user_profile.user.date_of_birth:
            user_age = user_profile.user.age
        
        # Get candidate's age
        candidate_age = None
        if candidate_profile.date_of_birth:
            dob = candidate_profile.date_of_birth
            today = date.today()
            candidate_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        elif hasattr(candidate_profile, "user") and candidate_profile.user.date_of_birth:
            candidate_age = candidate_profile.user.age
        
        # If ages are unknown, allow
        if user_age is None or candidate_age is None:
            return True
        
        # Get user's age preferences for candidates
        user_min, user_max = 18, 99
        try:
            if hasattr(user_profile, "looking_for") and user_profile.looking_for:
                user_min = user_profile.looking_for.min_age or 18
                user_max = user_profile.looking_for.max_age or 99
        except Exception:
            pass
        
        # Get candidate's age preferences
        cand_min, cand_max = 18, 99
        try:
            if hasattr(candidate_profile, "looking_for") and candidate_profile.looking_for:
                cand_min = candidate_profile.looking_for.min_age or 18
                cand_max = candidate_profile.looking_for.max_age or 99
        except Exception:
            pass
        
        # Check if candidate's age is in user's range
        if not (user_min <= candidate_age <= user_max):
            return False
        
        # Check if user's age is in candidate's range
        if not (cand_min <= user_age <= cand_max):
            return False
        
        return True
    
    def _check_distance_preference(
        self,
        user_profile: Profile,
        candidate_profile: Profile,
    ) -> bool:
        """Check if candidate is within user's distance preference."""
        # If no location data, allow
        if not all([
            user_profile.latitude, user_profile.longitude,
            candidate_profile.latitude, candidate_profile.longitude
        ]):
            return True
        
        # Calculate distance
        distance = self._haversine_distance(
            float(user_profile.latitude), float(user_profile.longitude),
            float(candidate_profile.latitude), float(candidate_profile.longitude),
        )
        
        # Get max distance preference
        max_distance = 100  # Default
        try:
            if hasattr(user_profile, "looking_for") and user_profile.looking_for:
                max_distance = user_profile.looking_for.max_distance or 100
        except Exception:
            pass
        
        # Allow some buffer (20%) beyond stated preference
        return distance <= max_distance * 1.2
    
    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float,
    ) -> float:
        """Calculate distance between two points using Haversine formula."""
        import math
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return self.EARTH_RADIUS_KM * c


class ProfileRanker:
    """
    Ranks and filters candidate profiles for a user.
    Uses the MatchingAlgorithm to score and sort candidates.
    """
    
    # Minimum score to be considered a relevant match
    DEFAULT_MIN_SCORE = 35
    
    def __init__(
        self,
        algorithm: Optional[MatchingAlgorithm] = None,
        candidate_filter: Optional[CandidateFilter] = None,
    ):
        self.algorithm = algorithm or MatchingAlgorithm()
        self.candidate_filter = candidate_filter or CandidateFilter()
    
    def get_ranked_profiles(
        self,
        user: User,
        candidates: QuerySet[Profile],
        limit: int = 20,
        min_score: Optional[int] = None,
        filter_irrelevant: bool = True,
    ) -> list[tuple[Profile, CompatibilityBreakdown]]:
        """
        Rank candidate profiles by compatibility with the user.
        
        Args:
            user: The user looking for matches
            candidates: QuerySet of candidate profiles to rank
            limit: Maximum number of results to return
            min_score: Minimum compatibility score to include (default: 35)
            filter_irrelevant: Whether to filter out candidates who don't meet basic criteria
            
        Returns:
            List of (profile, breakdown) tuples sorted by score descending
        """
        if min_score is None:
            min_score = self.DEFAULT_MIN_SCORE
            
        if not hasattr(user, "profile"):
            # User has no profile - can't calculate compatibility
            return [(p, CompatibilityBreakdown()) for p in candidates[:limit]]
        
        user_profile = user.profile
        
        # Calculate compatibility for each candidate
        scored_profiles: list[tuple[Profile, CompatibilityBreakdown]] = []
        
        for candidate_profile in candidates:
            # Pre-filter based on hard requirements
            if filter_irrelevant:
                if not self.candidate_filter.is_relevant(user_profile, candidate_profile):
                    continue
            
            breakdown = self.algorithm.calculate_compatibility(
                user_profile,
                candidate_profile,
            )
            
            if breakdown.total_score >= min_score:
                scored_profiles.append((candidate_profile, breakdown))
        
        # Sort by total score descending
        scored_profiles.sort(key=lambda x: x[1].total_score, reverse=True)
        
        return scored_profiles[:limit]
    
    def get_compatibility(
        self,
        user1: User,
        user2: User,
    ) -> CompatibilityBreakdown:
        """
        Calculate compatibility between two users.
        
        Args:
            user1: First user
            user2: Second user
            
        Returns:
            CompatibilityBreakdown between the users
        """
        if not hasattr(user1, "profile") or not hasattr(user2, "profile"):
            return CompatibilityBreakdown()
        
        return self.algorithm.calculate_compatibility(
            user1.profile,
            user2.profile,
        )


# Convenience function for quick compatibility check
def calculate_match_score(user1: User, user2: User) -> tuple[int, CompatibilityBreakdown]:
    """
    Calculate match score between two users.
    
    Args:
        user1: First user
        user2: Second user
        
    Returns:
        Tuple of (total_score, breakdown)
    """
    ranker = ProfileRanker()
    breakdown = ranker.get_compatibility(user1, user2)
    return breakdown.total_score, breakdown
