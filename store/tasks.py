# your_app/tasks.py
from celery import shared_task
from .models import Cart, AbandonedCart
from .utils import send_recovery_email
from datetime import timedelta
from django.utils import timezone

@shared_task
def check_and_send_abandoned_cart_emails():
    cutoff_time = timezone.now() - timedelta(hours=24)
    carts = Cart.objects.filter(updated_at__lt=cutoff_time, abandonedcart__isnull=True)

    for cart in carts:
        abandoned_cart, created = AbandonedCart.objects.get_or_create(cart=cart)
        if created:
            send_recovery_email(abandoned_cart)
