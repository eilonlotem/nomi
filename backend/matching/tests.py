"""Tests for the Matching Algorithm."""
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

from django.test import TestCase

from .algorithm import CandidateFilter, CompatibilityBreakdown, MatchingAlgorithm


class MockLookingFor:
    def __init__(self, genders=None, min_age=18, max_age=99, max_distance=50):
        self.genders = genders or []
        self.min_age, self.max_age, self.max_distance = min_age, max_age, max_distance
        self.relationship_types = []


class MockProfile:
    def __init__(self, gender="", dob=None, lat=None, lng=None, looking_for=None, 
                 tags=None, interests=None, mood="", has_lf=True):
        self.gender = gender
        self.date_of_birth = dob
        self.latitude, self.longitude = lat, lng
        self._lf, self._has_lf = looking_for, has_lf
        self._tags, self._interests = tags or [], interests or []
        self.current_mood = mood
        self.response_pace = self.date_pace = ""
        self.preferred_times = []

    @property
    def looking_for(self):
        if not self._has_lf or not self._lf:
            raise Exception("DoesNotExist")
        return self._lf

    @property
    def disability_tags(self):
        m = MagicMock()
        m.values_list.return_value = self._tags
        return m

    @property
    def interests(self):
        m = MagicMock()
        m.values_list.return_value = self._interests
        return m


def dob(age): 
    return date.today() - timedelta(days=age * 365 + age // 4)


class GenderFilterTests(TestCase):
    def setUp(self):
        self.f = CandidateFilter()

    def test_woman_looking_for_men(self):
        user = MockProfile(gender="female", looking_for=MockLookingFor(genders=["men"]))
        male = MockProfile(gender="male", looking_for=MockLookingFor(genders=["women"]))
        female = MockProfile(gender="female", looking_for=MockLookingFor(genders=["men"]))
        
        self.assertTrue(self.f._check_gender_preferences(user, male))
        self.assertFalse(self.f._check_gender_preferences(user, female))

    def test_man_looking_for_women(self):
        user = MockProfile(gender="male", looking_for=MockLookingFor(genders=["women"]))
        female = MockProfile(gender="female", looking_for=MockLookingFor(genders=["men"]))
        male = MockProfile(gender="male", looking_for=MockLookingFor(genders=["women"]))
        
        self.assertTrue(self.f._check_gender_preferences(user, female))
        self.assertFalse(self.f._check_gender_preferences(user, male))

    def test_mutual_preference_required(self):
        woman = MockProfile(gender="female", looking_for=MockLookingFor(genders=["men"]))
        gay_man = MockProfile(gender="male", looking_for=MockLookingFor(genders=["men"]))
        self.assertFalse(self.f._check_gender_preferences(woman, gay_man))

    def test_everyone_matches_all(self):
        user = MockProfile(gender="female", looking_for=MockLookingFor(genders=["everyone"]))
        for g in ["male", "female", "nonbinary"]:
            cand = MockProfile(gender=g, looking_for=MockLookingFor(genders=["everyone"]))
            self.assertTrue(self.f._check_gender_preferences(user, cand))

    def test_no_gender_filtered(self):
        user = MockProfile(gender="female", looking_for=MockLookingFor(genders=["men"]))
        no_gender = MockProfile(gender="", looking_for=MockLookingFor(genders=["women"]))
        self.assertFalse(self.f._check_gender_preferences(user, no_gender))

    def test_empty_prefs_matches_all(self):
        user = MockProfile(gender="male", looking_for=MockLookingFor(genders=[]))
        cand = MockProfile(gender="female", looking_for=MockLookingFor(genders=[]))
        self.assertTrue(self.f._check_gender_preferences(user, cand))

    def test_no_looking_for_matches_all(self):
        user = MockProfile(gender="male", has_lf=False)
        cand = MockProfile(gender="female", has_lf=False)
        self.assertTrue(self.f._check_gender_preferences(user, cand))


class AgeFilterTests(TestCase):
    def setUp(self):
        self.f = CandidateFilter()

    def test_within_range_passes(self):
        user = MockProfile(dob=dob(30), looking_for=MockLookingFor(min_age=25, max_age=35))
        cand = MockProfile(dob=dob(30), looking_for=MockLookingFor(min_age=25, max_age=35))
        self.assertTrue(self.f._check_age_preferences(user, cand))

    def test_outside_range_fails(self):
        user = MockProfile(dob=dob(30), looking_for=MockLookingFor(min_age=25, max_age=35))
        cand = MockProfile(dob=dob(45), looking_for=MockLookingFor(min_age=40, max_age=50))
        self.assertFalse(self.f._check_age_preferences(user, cand))

    def test_mutual_check(self):
        user = MockProfile(dob=dob(30), looking_for=MockLookingFor(min_age=25, max_age=35))
        cand = MockProfile(dob=dob(28), looking_for=MockLookingFor(min_age=18, max_age=25))
        self.assertFalse(self.f._check_age_preferences(user, cand))


class DistanceFilterTests(TestCase):
    def setUp(self):
        self.f = CandidateFilter()
        self.tel_aviv = (Decimal("32.0853"), Decimal("34.7818"))
        self.herzliya = (Decimal("32.1663"), Decimal("34.8436"))

    def test_within_distance_passes(self):
        user = MockProfile(lat=self.tel_aviv[0], lng=self.tel_aviv[1], 
                          looking_for=MockLookingFor(max_distance=50))
        cand = MockProfile(lat=self.herzliya[0], lng=self.herzliya[1])
        self.assertTrue(self.f._check_distance_preference(user, cand))

    def test_haversine_accuracy(self):
        dist = self.f._haversine_distance(32.0853, 34.7818, 31.7683, 35.2137)
        self.assertTrue(50 < dist < 70)  # Tel Aviv to Jerusalem ~54km


class FullFilterTests(TestCase):
    def setUp(self):
        self.f = CandidateFilter()

    def test_perfect_match(self):
        user = MockProfile(gender="female", dob=dob(28), 
                          lat=Decimal("32.08"), lng=Decimal("34.78"),
                          looking_for=MockLookingFor(genders=["men"], min_age=25, max_age=35))
        cand = MockProfile(gender="male", dob=dob(30),
                          lat=Decimal("32.16"), lng=Decimal("34.84"),
                          looking_for=MockLookingFor(genders=["women"], min_age=25, max_age=35))
        self.assertTrue(self.f.is_relevant(user, cand))

    def test_gender_mismatch(self):
        user = MockProfile(gender="female", looking_for=MockLookingFor(genders=["men"]))
        cand = MockProfile(gender="female", looking_for=MockLookingFor(genders=["women"]))
        self.assertFalse(self.f.is_relevant(user, cand))


class CompatibilityTests(TestCase):
    def setUp(self):
        self.algo = MatchingAlgorithm()

    def test_mood_same_high(self):
        bd = CompatibilityBreakdown()
        self.algo._calculate_mood_compatibility(
            MockProfile(mood="chatty"), MockProfile(mood="chatty"), bd)
        self.assertGreaterEqual(bd.mood_compatibility_score, 90)

    def test_mood_mismatch_low(self):
        bd = CompatibilityBreakdown()
        self.algo._calculate_mood_compatibility(
            MockProfile(mood="adventurous"), MockProfile(mood="lowEnergy"), bd)
        self.assertLess(bd.mood_compatibility_score, 50)
