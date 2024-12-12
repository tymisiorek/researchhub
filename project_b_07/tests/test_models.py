from django.test import TestCase
from django.urls import reverse
from project_b_07.models import Team, TeamFile, TeamMembership, TeamChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class TeamFileModelTest(TestCase):
    def setUp(self):
        # Create a user and a team to associate with TeamFile
        self.user = User.objects.create_user(username="testuser", password="password")
        self.team = Team.objects.create(name="Test Team", created_by=self.user)

    def test_uploaded_file_creation(self):
        # Create a TeamFile instance with required fields
        uploaded_file = TeamFile.objects.create(
            title="Test File",
            file="path/to/testfile.txt",
            team=self.team,
            uploaded_by=self.user
        )
        self.assertEqual(uploaded_file.title, "Test File")
        self.assertEqual(uploaded_file.team, self.team)
        self.assertEqual(uploaded_file.uploaded_by, self.user)

    def test_uploaded_file_str(self):
        uploaded_file = TeamFile.objects.create(
            title="Test File",
            file="path/to/testfile.txt",
            team=self.team,
            uploaded_by=self.user
        )
        self.assertEqual(str(uploaded_file), "Test File")


class TeamModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.team = Team.objects.create(name="Another Test Team", created_by=self.user)

    def test_team_str(self):
        self.assertEqual(str(self.team), "Another Test Team")



class TeamChatMessageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.team = Team.objects.create(name="Test Team", created_by=self.user)

    def test_team_chat_message_str(self):
        message = TeamChatMessage.objects.create(team=self.team, user=self.user, message="Hello, team!")
        self.assertEqual(str(message), f"Message by {self.user.username} in {self.team.name}")