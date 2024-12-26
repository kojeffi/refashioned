from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)
from django.contrib.auth.models import User
from django.db import models
from cloudinary.models import CloudinaryField

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_photo = CloudinaryField('profile_photo', blank=True, null=True)
    about = models.TextField(blank=True)
    age = models.IntegerField(null=True, blank=True)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Example field
    purchase_count = models.IntegerField(default=0)  # Example field
    churn = models.BooleanField(default=False)  # New churn field
    bio = models.TextField(blank=True)
    interests = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        if self.profile_photo:
            try:
                # Optionally, you can resize the image after upload
                # cloudinary.uploader.upload(self.profile_photo.path, width=300, height=300, crop='limit')
                pass
            except Exception as e:
                logger.error(f"Error processing profile photo {self.profile_photo.path}: {e}")



@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        try:
            Profile.objects.create(user=instance)
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.username}: {e}")
    else:
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            try:
                Profile.objects.create(user=instance)
            except Exception as e:
                logger.error(f"Error creating profile for user {instance.username} after DoesNotExist exception: {e}")
        except Exception as e:
            logger.error(f"Error saving profile for user {instance.username}: {e}")

class Message(models.Model):
    user_message = models.CharField(max_length=200)
    bot_response = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_message} - {self.bot_response}"

class Subscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


