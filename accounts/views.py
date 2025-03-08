import os
import json
import uuid
import stripe
import paypalrestsdk
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.models import Profile, Cart, CartItem, Order, OrderItem,FAQ
from home.models import ShippingAddress
from accounts.serializers import UserSerializer, CartSerializer, OrderSerializer,ContactSerializer
from base.emails import send_account_activation_email
from products.models import Product, SizeVariant
from django.http import JsonResponse

from .models import CustomUser, Profile

from accounts.serializers import FAQSerializer



from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Profile
from .serializers import ProfileSerializer
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny

from django.db import models
from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from django.urls import path
from .models import Product 

@method_decorator(csrf_exempt, name='dispatch')
class ProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile)
        return Response({
            "message": "Profile retrieved successfully",
            "profile": serializer.data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile, created = Profile.objects.get_or_create(user=request.user, defaults=serializer.validated_data)
            return Response({
                "message": "Profile created successfully" if created else "Profile already exists",
                "profile": ProfileSerializer(profile).data,
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile updated successfully",
                "profile": serializer.data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        profile.delete()
        return Response({
            "message": "Profile deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)


User = get_user_model()

# Initialize Stripe and PayPal
stripe.api_key = settings.STRIPE_SECRET_KEY
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" in production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})

def get_mpesa_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate"
    querystring = {"grant_type": "client_credentials"}
    headers = {
        "Authorization": f"Basic {settings.MPESA_CREDENTIALS}"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return data.get("access_token")



# ✅ JWT Login View
class LoginView(APIView):
    authentication_classes = []  # No authentication needed for login
    permission_classes = [AllowAny]  # Allow anyone to log in

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        profile = Profile.objects.filter(user=user).first()
        if not profile or not profile.is_email_verified:
            return Response({"message": "Account not verified"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        # ✅ Return user details along with tokens
        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "first_name": user.first_name,  # ✅ Fixed (use field directly)
                "last_name": user.last_name,  # ✅ Fixed (use field directly)
                "email": user.email,
                "profile_image": profile.profile_image.url if profile.profile_image else None,
                "phone": profile.phone_number,
                "bio": profile.bio,  # ✅ Added profile bio
                "shipping_address": profile.shipping_address.address if profile.shipping_address else None,
                "cart_count": profile.get_cart_count(),  # ✅ Display cart items count
                "is_admin": user.is_staff,  # ✅ Show if the user is an admin
            }
        }, status=status.HTTP_200_OK)


# Register View
from django.db import transaction

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        if CustomUser.objects.filter(email=email).exists():
            return Response({"message": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():  # Ensures database consistency
            user = CustomUser.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=False  # Require email verification
            )
            user.set_password(password)
            user.save()

            # Create a profile for the user
            Profile.objects.get_or_create(user=user)

            # Generate verification link
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            verification_url = f"http://127.0.0.1:3000/verify-email?uidb64={uidb64}&token={token}"

            # Send verification email
            send_mail(
                "Verify Your Email",
                f"Click the link to verify your account: {verification_url}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

        return Response({"message": "User registered, check email for verification"}, status=status.HTTP_201_CREATED)
 


from rest_framework.permissions import AllowAny

class ActivateAccountView(APIView):
    permission_classes = [AllowAny]  # 👈 This allows anyone to access this view

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(CustomUser, pk=uid)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()

                # Mark the profile as email verified
                profile = get_object_or_404(Profile, user=user)
                profile.is_email_verified = True
                profile.save()

                return Response({"message": "Account activated successfully."}, status=status.HTTP_200_OK)

            return Response({"message": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"message": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)


# ✅ JWT Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

# ✅ Add to Cart View
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        product = get_object_or_404(Product, uid=uid)
        cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)

        size_name = request.data.get('size')  # ✅ Now optional

        size_variant = None
        if size_name:
            try:
                size_variant = SizeVariant.objects.get(size_name=size_name)
            except SizeVariant.DoesNotExist:
                return Response({"error": f"Size '{size_name}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, size_variant=size_variant
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return Response({"message": "Item added to cart successfully"}, status=status.HTTP_200_OK)


# ✅ View Cart
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(f"🔍 Authenticated user: {request.user}")

        # Optimize query performance using `prefetch_related`
        cart = Cart.objects.prefetch_related(
            'cart_items__product',
            'cart_items__size_variant',
            'cart_items__color_variant'
        ).filter(user=request.user, is_paid=False).first()

        if not cart or not cart.cart_items.exists():
            return Response({"message": "Cart is empty", "data": None}, status=status.HTTP_404_NOT_FOUND)

        # Pass the request object to the serializer context
        serializer = CartSerializer(cart, context={'request': request})
        return Response({"message": "Cart retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    


    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(f"🔍 Authenticated user: {request.user}")

        # Optimize query performance using `prefetch_related`
        cart = Cart.objects.prefetch_related(
            'cart_items__product',
            'cart_items__size_variant',
            'cart_items__color_variant'
        ).filter(user=request.user, is_paid=False).first()

        if not cart or not cart.cart_items.exists():
            return Response({"message": "Cart is empty", "data": None}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartSerializer(cart)
        return Response({"message": "Cart retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)
# ✅ Payment View
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_method = request.data.get('payment_method')
        cart = get_object_or_404(Cart, user=request.user, is_paid=False)

        if payment_method == 'stripe':
            intent = stripe.PaymentIntent.create(
                amount=int(cart.get_cart_total_price_after_coupon() * 100),
                currency='usd',
            )
            return Response({"message": "Stripe payment initiated", "data": {"client_secret": intent.client_secret}}, status=status.HTTP_200_OK)

        elif payment_method == 'paypal':
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{"amount": {"total": str(cart.get_cart_total_price_after_coupon()), "currency": "USD"}}],
                "redirect_urls": {"return_url": "http://localhost:8000/payment/success", "cancel_url": "http://localhost:8000/payment/cancel"}
            })

            if payment.create():
                return Response({"message": "PayPal payment initiated", "data": {"approval_url": payment.links[1].href}}, status=status.HTTP_200_OK)

            return Response({"message": "Payment creation failed"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)
    

# ✅ Order History View
class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-order_date')
        serializer = OrderSerializer(orders, many=True)
        return Response({"message": "Orders retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response({"message": "Order details retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    
class DeleteAccountView(APIView):
    def delete(self, request):
        request.user.delete()
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_200_OK)
    


#password reset

from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# ✅ Password Reset Request
@method_decorator(csrf_exempt, name='dispatch')
class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        form.save(
            use_https=self.request.is_secure(),
            from_email=None,
            request=self.request
        )
        return JsonResponse({"message": "Password reset email sent.", "result_code": 200}, status=200)

    def form_invalid(self, form):
        return JsonResponse({"message": "Invalid request.", "result_code": 400, "errors": form.errors}, status=400)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "Password reset email sent successfully.", "result_code": 200}, status=200)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        form.save()
        return JsonResponse({"message": "Password has been reset successfully.", "result_code": 200}, status=200)

    def form_invalid(self, form):
        return JsonResponse({"message": "Invalid reset token or password mismatch.", "result_code": 400, "errors": form.errors}, status=400)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def get(self, request, *args, **kwargs):
        return JsonResponse({"message": "Password reset complete. You can now log in with the new password.", "result_code": 200}, status=200)
    

# mpesa
import requests
from django.conf import settings
import base64

class MpesaSTKPushView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        access_token = get_mpesa_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": base64.b64encode(
                (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + "timestamp").encode()
            ).decode(),
            "Timestamp": "timestamp",
            "TransactionType": "CustomerPayBillOnline",
            "Amount": request.data.get("amount"),
            "PartyA": request.data.get("phone_number"),
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": request.data.get("phone_number"),
            "CallBackURL": "https://refashioned.onrender.com/mpesa/callback/",
            "AccountReference": "Order1234",
            "TransactionDesc": "Payment for order"
        }

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload, headers=headers
        )
        return Response(response.json(), status=response.status_code)
    



class MpesaCallbackView(APIView):
    def post(self, request):
        data = request.data
        print("M-Pesa Callback Data:", data)
        if data["Body"]["stkCallback"]["ResultCode"] == 0:
            amount = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
            phone = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
            print(f"Payment of {amount} received from {phone}")
        return Response({"message": "Callback received"}, status=status.HTTP_200_OK)
    


class StripePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = get_object_or_404(Cart, user=request.user, is_paid=False)
            amount = int(cart.get_cart_total_price_after_coupon() * 100)  # Convert to cents

            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                payment_method_types=['card']
            )

            return Response({
                "message": "Stripe payment initiated",
                "client_secret": payment_intent.client_secret
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        



class PayPalPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = get_object_or_404(Cart, user=request.user, is_paid=False)
            total_price = str(cart.get_cart_total_price_after_coupon())

            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{
                    "amount": {"total": total_price, "currency": "USD"},
                    "description": "Purchase from our store"
                }],
                "redirect_urls": {
                    "return_url": "http://localhost:8000/payment/success",
                    "cancel_url": "http://localhost:8000/payment/cancel"
                }
            })

            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
                return Response({"message": "PayPal payment initiated", "approval_url": approval_url}, status=status.HTTP_200_OK)

            return Response({"error": "Failed to create PayPal payment"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

# Contact API View
class ContactAPIView(APIView):
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Contact form submitted successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FAQListView(APIView):
    permission_classes = [AllowAny]  # 👈 This allows anyone to access this view

    def get(self, request):
        faqs = FAQ.objects.all()
        serializer = FAQSerializer(faqs, many=True)
        return Response({
            "message": "FAQs retrieved successfully",
            "result_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def post(self, request):
        serializer = FAQSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "FAQ added successfully",
                "result_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FAQDetailView(APIView):
    permission_classes = [AllowAny]  # 👈 This allows anyone to access this view

    def get(self, request, faq_id):
        faq = get_object_or_404(FAQ, id=faq_id)
        serializer = FAQSerializer(faq)
        return Response({
            "message": "FAQ retrieved successfully",
            "result_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def delete(self, request, faq_id):
        faq = get_object_or_404(FAQ, id=faq_id)
        faq.delete()
        return Response({
            "message": "FAQ deleted successfully",
            "result_code": status.HTTP_204_NO_CONTENT,
            "data": {}
        })

