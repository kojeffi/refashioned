from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Creates a profile whenever a new user is created"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Profile)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile instance safely without infinite loops."""
    if instance.user:
        instance.user.save(update_fields=[])  # Prevent recursive saves
