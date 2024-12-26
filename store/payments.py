import stripe
import paypalrestsdk
from django.conf import settings
from django.urls import reverse
import paypalrestsdk
from django.conf import settings
import paypalrestsdk
from django.conf import settings



stripe.api_key = settings.STRIPE_SECRET_KEY

# Initialize PayPal SDK
paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET,
})

def create_stripe_payment_intent(order):
    try:
        amount = int(order.total_price * 100)
        print(f"Creating Stripe Payment Intent for amount: {amount} cents")
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='gbp',
            metadata={'order_id': order.id}
        )
        return intent
    except Exception as e:
        print(f"Error creating payment intent: {e}")
        return None

def create_paypal_payment(order, return_url, cancel_url):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url
        },
        "transactions": [{
            "amount": {
                "total": str(order.total_price),
                "currency": "GBP"
            },
            "description": "Order #" + str(order.id)
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return link.href
    return None



paypalrestsdk.configure({
    "mode": "sandbox",  # "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def execute_paypal_payment(payment_id, payer_id):
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return True
    else:
        return False



paypalrestsdk.configure({
    "mode": "sandbox",  # Set to "live" in production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def create_paypal_payment(order, return_url, cancel_url):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": item.product.name,
                    "sku": item.product.sku,
                    "price": str(item.product.final_price),
                    "currency": "GBP",
                    "quantity": item.quantity
                } for item in order.orderitem_set.all()]
            },
            "amount": {
                "total": str(order.total_price),
                "currency": "GBP"
            },
            "description": f"Order {order.id}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                order.payment_id = payment.id
                order.save()
                return approval_url
    else:
        print(payment.error)
        return None

def execute_paypal_payment(payment_id, payer_id):
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return True
    else:
        print(payment.error)
        return False
