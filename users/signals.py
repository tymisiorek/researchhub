# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Ensure a profile is created when a user is created (e.g., through social login)
        Profile.objects.get_or_create(user=instance, defaults={'role': 'common'})

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Save the profile if it exists to handle any updates
    if hasattr(instance, 'profile'):
        instance.profile.save()