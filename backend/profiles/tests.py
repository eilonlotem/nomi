from django.test import TestCase
from rest_framework.test import APIRequestFactory

from matching.models import Match
from users.models import User

from .models import DisabilityTag, Profile, ProfileDisabilityTagVisibility
from .serializers import ProfileCardSerializer


class ProfileTagVisibilityTests(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()
        self.viewer = User.objects.create_user(username="viewer", password="testpass123")
        self.other = User.objects.create_user(username="other", password="testpass123")
        self.owner = User.objects.create_user(username="owner", password="testpass123")
        self.tag = DisabilityTag.objects.create(
            code="difficultySeeing",
            name_en="Difficulty seeing",
            icon="👁️",
            category="vision",
            disclosure_level="functional",
        )
        self.profile = Profile.objects.create(user=self.owner, display_name="Owner")
        self.profile.disability_tags.add(self.tag)

    def test_specific_visibility_allows_only_selected_viewers(self) -> None:
        visibility = ProfileDisabilityTagVisibility.objects.create(
            profile=self.profile,
            tag=self.tag,
            visibility="specific",
        )
        visibility.allowed_viewers.set([self.viewer])

        request = self.factory.get("/")
        request.user = self.viewer
        data = ProfileCardSerializer(self.profile, context={"request": request}).data
        self.assertEqual(len(data["disability_tags"]), 1)

        request = self.factory.get("/")
        request.user = self.other
        data = ProfileCardSerializer(self.profile, context={"request": request}).data
        self.assertEqual(len(data["disability_tags"]), 0)

    def test_matches_visibility_allows_matches(self) -> None:
        ProfileDisabilityTagVisibility.objects.create(
            profile=self.profile,
            tag=self.tag,
            visibility="matches",
        )
        Match.objects.create(user1=self.owner, user2=self.viewer)

        request = self.factory.get("/")
        request.user = self.viewer
        data = ProfileCardSerializer(self.profile, context={"request": request}).data
        self.assertEqual(len(data["disability_tags"]), 1)

        request = self.factory.get("/")
        request.user = self.other
        data = ProfileCardSerializer(self.profile, context={"request": request}).data
        self.assertEqual(len(data["disability_tags"]), 0)
