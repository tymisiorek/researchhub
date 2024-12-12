'''
*  REFERENCES
*  Title: Django Documentation
*  Author: Django
*  Date: 12/4/2024
*  URL: https://docs.djangoproject.com/en/5.1/ref/models/instances/#customizing-model-loading-and-saving
*
*  Use: Used to implement save function
'''

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from project_b_07.models import Team

class Milestone(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='milestones')
    team = models.ForeignKey(
        Team,  # Use the full app label path
        on_delete=models.CASCADE,
        related_name='milestones',
        null = True,
        blank = True
     )    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    progress = models.PositiveIntegerField(default=0)  # Progress in percentage (0-100)
    completed = models.BooleanField(default=False)

    def mark_complete(self):
        self.progress = 100
        self.completed = True
        self.save()
    
    def save(self, *args, **kwargs):
        if self.progress < 100:
            self.completed = False
        elif self.progress == 100 and not self.completed:
            self.completed = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.progress}%) - {self.team.name}"

