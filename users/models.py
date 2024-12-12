'''
*  REFERENCES
*  Title: ChatGPT
*  Author: OpenAI
*  Date: 11/16/2024
*
*  Used to add docstrings and comments to functions and write boilerplate for the
functions.

*  Title: djangoproject.com
*  Author: Django Documentation
*  Date: 11/16/2024
*
*  Used to implement logic for the user-related models and to ensure proper use of model methods. 
    Also used for
'''


# models.py
from django.contrib.auth.models import User  # Import the built-in User model for user management
from django.db import models  # Import Django's models module for database modeling
from django.conf import settings  # Import settings for project-level configurations
from project_b_07.models import Team  # Import the Team model from another app in the project

class Profile(models.Model):
    """
    Model to extend the built-in User model with additional attributes such as role.
    """
    ROLE_CHOICES = [  # Define the possible roles a user can have
        ('common', 'Common User'),
        ('admin', 'Administrator'),
        ('anonymous', 'Anonymous')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link each Profile to a single User with one-to-one relationship
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='common')  # Role field with choices and a default value

    def is_admin(self):
        """
        Check if the user has an 'admin' role.
        """
        return self.role == 'admin'
    
    def is_common_user(self):
        """
        Check if the user has a 'common' role.
        """
        return self.role == 'common'

    def __str__(self):
        """
        String representation of the Profile model showing the username and role.
        """
        return f"{self.user.username} ({self.get_role_display()})"

class Availability(models.Model):
    """
    Model to represent a user's availability on a specific date and time.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Reference the user model defined in project settings
        on_delete=models.CASCADE,  # Delete related availabilities if the user is deleted
        related_name="availabilities"  # Name for reverse relation from user to availability
    )
    team = models.ForeignKey(
        Team,  # Reference to the Team model
        on_delete=models.CASCADE,  # Delete related availabilities if the team is deleted
        related_name="availabilities"  # Name for reverse relation from team to availability
    )
    date = models.DateField()  # Date of the availability
    start_time = models.TimeField()  # Start time of the availability
    end_time = models.TimeField()  # End time of the availability

    class Meta:
        unique_together = ('user', 'team', 'date', 'start_time', 'end_time')  # Ensure unique availability for the user, team, date, and time

    def __str__(self):
        """
        String representation of the Availability model showing user, date, and time range.
        """
        return f"{self.user} available on {self.date} from {self.start_time} to {self.end_time} in team {self.team}"
