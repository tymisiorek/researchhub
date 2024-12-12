from django.test import TestCase
from django.urls import reverse
from project_b_07.models import Team, TeamMembership
from django.contrib.auth import get_user_model

User = get_user_model()

class FileUploadViewTest(TestCase):
    def setUp(self):
        # Create a user and team for the upload test
        self.user = User.objects.create_user(username="testuser", password="password")
        self.team = Team.objects.create(name="Test Team", created_by=self.user)
        self.client.login(username="testuser", password="password")

    def test_file_upload_view(self):
        # Use the updated 'upload_team_file' URL name with team_id
        url = reverse('upload_team_file', args=[self.team.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload_team_file.html')


class CreateTeamViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

    def test_create_team_view(self):
        response = self.client.post(reverse('create_team'), {'name': 'New Team', 'description': 'A new team'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Team.objects.filter(name='New Team').exists())
