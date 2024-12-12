"""
*  REFERENCES
*  Title: ChatGPT
*  Author: OpenAI
*  Date: 11/16/2024
*  Code version: GPT-4
*
*  Use: Used to write docstrings/inline comments and model structure for Django models.
"""

from django.db import models
from django.contrib.auth.models import User
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
from datetime import datetime


class Team(models.Model):
    """
    Model representing a team with a name, description, creation timestamp, and creator.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically sets the field to the current timestamp when the object is created
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Links to the user who created the team

    def __str__(self):
        """
        String representation of the Team model, displaying the team name.
        """
        return self.name

class TeamMembership(models.Model):
    """
    Model representing membership in a team, with user, role, status, and join timestamp.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Links to the user who is a member
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')  # Links to the associated team
    role = models.CharField(max_length=50, default="Member", blank=True, null=True)  # Role of the user in the team
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Membership status
    joined_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the membership was created

    class Meta:
        unique_together = ('user', 'team')  # Ensures a user cannot have multiple memberships in the same team

class TeamFile(models.Model):
    """
    Model representing a file uploaded to a team, with details about the title, file content, description, keywords, and uploader.
    """
    title = models.CharField(max_length=255, default="Untitled")  # Title of the file
    file = models.FileField(storage=S3Boto3Storage())  # File stored using S3Boto3 storage backend
    description = models.TextField(default='')  # Description of the file
    keywords = models.CharField(max_length=255, default='')  # Keywords associated with the file for search purposes
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the file was uploaded
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # User who uploaded the file
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='files')  # Team the file is associated with

    def __str__(self):
        """
        String representation of the TeamFile model, displaying the file title.
        """
        return self.title

class TeamChatMessage(models.Model):
    """
    Model representing a chat message within a team.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='chat_messages')  # Team the message belongs to
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # User who posted the message
    message = models.TextField()  # Content of the chat message
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the message was created

    class Meta:
        ordering = ['created_at']  # Orders chat messages by creation time in ascending order

    def __str__(self):
        """
        String representation of the TeamChatMessage model, displaying the user and team.
        """
        return f"Message by {self.user.username} in {self.team.name}"