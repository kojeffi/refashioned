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
from django.db.models import Sum


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
    "mode": "live",  # Change to "live" in production
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

        serializer = CartSerializer(cart, context={'request': request})

        # Calculate total item count
        total_count = cart.cart_items.aggregate(total=Sum('quantity'))['total'] or 0

        return Response(
            {
                "message": "Cart retrieved successfully",
                "data": serializer.data,
                "total_count": total_count
            },
            status=status.HTTP_200_OK
        )



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
                "redirect_urls": {"return_url": "https://refashioned.onrender.com/payment/success", "cancel_url": "https://refashioned.onrender.com/payment/cancel"}
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
import base64
from django.conf import settings

def get_mpesa_access_token():
    try:
        # M-Pesa OAuth URL
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        # Encode consumer key and secret in Base64
        credentials = f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Set headers
        headers = {
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        # Make the request
        response = requests.get(url, headers=headers)
        
        # Log the response for debugging
        print("M-Pesa OAuth Response:", response.status_code, response.text)
        
        # Check for errors
        if response.status_code != 200:
            raise Exception(f"Failed to fetch access token: {response.status_code} - {response.text}")
        
        # Return the access token
        return response.json().get("access_token")
    
    except Exception as e:
        print("Error in get_mpesa_access_token:", str(e))
        return None

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import base64
from django.conf import settings

class MpesaSTKPushView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the access token
            access_token = get_mpesa_access_token()
            if not access_token:
                return Response({"error": "Failed to get access token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Ensure amount is a numeric value
            amount = float(request.data.get("amount"))
            if not amount or amount <= 0:
                return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate and format the phone number
            phone_number = request.data.get("phone_number")
            if not phone_number or len(phone_number) < 10:
                return Response({"error": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)

            # Add country code if missing (e.g., Kenya's code is 254)
            formatted_phone_number = phone_number if phone_number.startswith("254") else f"254{phone_number[1:]}"

            # Prepare the STK Push payload
            payload = {
                "BusinessShortCode": settings.MPESA_SHORTCODE,
                "Password": self.generate_password(),
                "Timestamp": self.get_timestamp(),
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,  # Use the numeric value
                "PartyA": formatted_phone_number,  # Use the formatted phone number
                "PartyB": settings.MPESA_SHORTCODE,
                "PhoneNumber": formatted_phone_number,  # Use the formatted phone number
                "CallBackURL": "https://refashioned.onrender.com/mpesa/callback/",
                "AccountReference": "Order1234",
                "TransactionDesc": "Payment for order"
            }

            # Log the payload
            print("M-Pesa STK Push Payload:", payload)

            # Make the STK Push request
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                json=payload, headers=headers
            )

            # Log the response
            print("M-Pesa STK Push Response:", response.json())

            # Check for errors
            if response.status_code != 200:
                return Response({"error": response.text}, status=response.status_code)

            # Return the response
            return Response(response.json(), status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_password(self):
        # Generate the password using the shortcode, passkey, and timestamp
        timestamp = self.get_timestamp()
        return base64.b64encode(
            (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
        ).decode()

    def get_timestamp(self):
        # Generate a timestamp in the format YYYYMMDDHHMMSS
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d%H%M%S")
    

    

class MpesaCallbackView(APIView):
    def post(self, request):
        data = request.data
        print("M-Pesa Callback Data:", data)
        if data["Body"]["stkCallback"]["ResultCode"] == 0:
            amount = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
            phone = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
            print(f"Payment of {amount} received from {phone}")
        return Response({"message": "Callback received"}, status=status.HTTP_200_OK)
    



# Contact API View
class ContactAPIView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to log in

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




from rest_framework import generics, permissions
from .models import Blog, Comment
from .serializers import BlogSerializer, CommentSerializer

class BlogListCreateView(generics.ListCreateAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can post comments

    def perform_create(self, serializer):
        blog_id = self.kwargs.get('pk')
        try:
            blog = Blog.objects.get(pk=blog_id)
        except Blog.DoesNotExist:
            return Response({"error": "Blog not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Automatically set the user to the authenticated user
        serializer.save(user=self.request.user, blog=blog)


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        blog = Blog.objects.get(pk=self.kwargs['pk'])
        return Comment.objects.filter(blog=blog)
    

class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_slug):
        # Get the user's cart
        cart = get_object_or_404(Cart, user=request.user, is_paid=False)
        
        # Find the product to remove
        product = get_object_or_404(Product, slug=product_slug)
        
        # Find the cart item associated with the product
        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        
        # Remove the item from the cart
        cart_item.delete()
        
        return Response(
            {"message": "Item removed from cart successfully"},
            status=status.HTTP_200_OK
        )
    



from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer

class ProductSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        category = request.query_params.get('category')

        print(f"Search query: {query}")  # Debugging log
        print(f"Min price: {min_price}")  # Debugging log
        print(f"Max price: {max_price}")  # Debugging log
        print(f"Category: {category}")  # Debugging log

        if not query:
            return Response({
                "message": "Please provide a search query.",
                "result_code": status.HTTP_400_BAD_REQUEST,
                "data": []
            })

        products = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(product_description__icontains=query) |
            Q(category__category_name__icontains=query)  # ✅ Use category_name
        )


        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        if category:
            products = products.filter(category__name__iexact=category)

        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response({
            "message": "Search results retrieved successfully",
            "result_code": status.HTTP_200_OK,
            "data": serializer.data
        })
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
import stripe, paypalrestsdk, requests, base64

# StripePaymentView with Order Completion Logic
class StripePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = get_object_or_404(Cart, user=request.user, is_paid=False)
            amount = int(cart.get_cart_total_price_after_coupon() * 100)  # Convert to cents

            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                payment_method_types=['card'],
                metadata={
                    'user_id': request.user.id,
                    'cart_id': cart.id
                }
            )

            return Response({
                "message": "Stripe payment initiated",
                "client_secret": payment_intent.client_secret
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Stripe Payment Confirmation Webhook Handler
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]  # Webhooks need to be accessible without authentication

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            # Handle successful payment completion
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                user_id = payment_intent['metadata']['user_id']
                cart_id = payment_intent['metadata']['cart_id']
                
                user = get_object_or_404(User, id=user_id)
                cart = get_object_or_404(Cart, id=cart_id, user=user, is_paid=False)
                
                # Create order from cart
                shipping_address = request.user.profile.shipping_address if hasattr(request.user, 'profile') and request.user.profile.shipping_address else None
                
                order = Order.objects.create(
                    user=user,
                    order_id=f"ORDER-{uuid.uuid4().hex[:8].upper()}",
                    total_amount=cart.get_cart_total_price_after_coupon(),
                    shipping_address=shipping_address,
                    payment_method="Stripe",
                    payment_id=payment_intent['id'],
                    is_paid=True
                )
                
                # Transfer cart items to order items
                for cart_item in cart.cart_items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        size_variant=cart_item.size_variant,
                        color_variant=cart_item.color_variant,
                        price=cart_item.get_product_price()
                    )
                
                # Mark cart as paid
                cart.is_paid = True
                cart.save()
                
                return Response({"message": "Payment processed successfully"}, status=status.HTTP_200_OK)
                
            return Response({"message": "Event received but not processed"}, status=status.HTTP_200_OK)
            
        except ValueError as e:
            # Invalid payload
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# PayPal Payment View with Order Completion Logic
class PayPalPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get the user's cart
            cart = get_object_or_404(Cart, user=request.user, is_paid=False)
            
            # Calculate the total price
            total_price = str(cart.get_cart_total_price_after_coupon())

            # Determine the primary key field (id or uid)
            cart_primary_key = getattr(cart, 'uid', None) or cart.id

            # Create PayPal payment
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{
                    "amount": {"total": total_price, "currency": "USD"},
                    "description": "Purchase from our store"
                }],
                "redirect_urls": {
                    "return_url": f"https://refashioned.onrender.com/payment/paypal/success?user_id={request.user.id}&cart_id={cart_primary_key}",
                    "cancel_url": "https://refashioned.onrender.com/payment/cancel"
                }
            })

            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
                return Response({"message": "PayPal payment initiated", "approval_url": approval_url}, status=status.HTTP_200_OK)

            return Response({"error": "Failed to create PayPal payment"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)     

# PayPal Success Handler
class PayPalSuccessView(APIView):
    permission_classes = [AllowAny]  # This needs to be accessible via redirect

    def get(self, request):
        payment_id = request.query_params.get('paymentId')
        payer_id = request.query_params.get('PayerID')
        user_id = request.query_params.get('user_id')
        cart_id = request.query_params.get('cart_id')
        
        if not all([payment_id, payer_id, user_id, cart_id]):
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                user = get_object_or_404(User, id=user_id)
                cart = get_object_or_404(Cart, id=cart_id, user=user, is_paid=False)
                
                # Get shipping address if available
                shipping_address = user.profile.shipping_address if hasattr(user, 'profile') and user.profile.shipping_address else None
                
                # Create order
                order = Order.objects.create(
                    user=user,
                    order_id=f"ORDER-{uuid.uuid4().hex[:8].upper()}",
                    total_amount=cart.get_cart_total_price_after_coupon(),
                    shipping_address=shipping_address,
                    payment_method="PayPal",
                    payment_id=payment_id,
                    is_paid=True
                )
                
                # Transfer cart items to order items
                for cart_item in cart.cart_items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        size_variant=cart_item.size_variant,
                        color_variant=cart_item.color_variant,
                        price=cart_item.get_product_price()
                    )
                
                # Mark cart as paid
                cart.is_paid = True
                cart.save()
                
                # Redirect to frontend success page
                return Response({
                    "message": "Payment completed successfully",
                    "order_id": order.order_id
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Payment execution failed"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Updated CheckoutView to handle all payment methods consistently
class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("Received data:", request.data)  # Log incoming request data
        cart = get_object_or_404(Cart, user=request.user, is_paid=False)
        payment_method = request.data.get("payment_method")
        
        if not payment_method:
            return Response({"message": "Payment method is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        total_amount = cart.get_cart_total_price_after_coupon()
        print("Total amount from cart:", total_amount)  # Log total amount from cart
        
        if payment_method == "stripe":
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'user_id': request.user.id,
                    'cart_id': cart.id
                }
            )
            return Response({
                "message": "Stripe payment initiated",
                "data": {"client_secret": intent.client_secret}
            }, status=status.HTTP_200_OK)
        
        elif payment_method == "paypal":
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{
                    "amount": {"total": str(total_amount), "currency": "USD"},
                    "description": "Purchase from our store"
                }],
                "redirect_urls": {
                    "return_url": f"https://refashioned.onrender.com/payment/paypal/success?user_id={request.user.id}&cart_id={cart.id}",
                    "cancel_url": "https://refashioned.onrender.com/payment/cancel"
                }
            })
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == "approval_url")
                return Response({"message": "PayPal payment initiated", "approval_url": approval_url}, status=status.HTTP_200_OK)
            return Response({"message": "Failed to create PayPal payment"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif payment_method == "mpesa":
            access_token = get_mpesa_access_token()
            if not access_token:
                return Response({"error": "Failed to get access token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            phone_number = request.data.get("phone_number")
            if not phone_number or len(phone_number) < 10:
                return Response({"error": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)
                
            # Format phone number properly
            formatted_phone_number = phone_number if phone_number.startswith("254") else f"254{phone_number[1:]}"
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = base64.b64encode(
                (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
            ).decode()
            
            headers = {
                "Authorization": f"Bearer {access_token}", 
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": settings.MPESA_SHORTCODE,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(total_amount),  # Ensure this is a numeric value
                "PartyA": formatted_phone_number,
                "PartyB": settings.MPESA_SHORTCODE,
                "PhoneNumber": formatted_phone_number,
                "CallBackURL": "https://refashioned.onrender.com/mpesa/callback/",
                "AccountReference": f"Order-{uuid.uuid4().hex[:8].upper()}",
                "TransactionDesc": "Payment for order"
            }
            
            print("M-Pesa payload:", payload)  # Log M-Pesa payload
            
            response = requests.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", 
                json=payload, 
                headers=headers
            )
            
            if response.status_code == 200:
                return Response({
                    "message": "M-Pesa payment initiated. Please check your phone to complete the transaction.",
                    "data": response.json()
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "error": "M-Pesa payment initiation failed", 
                    "details": response.json()
                }, status=response.status_code)
        
        return Response({"message": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)


# Updated M-Pesa Callback View to Complete Order
class MpesaCallbackView(APIView):
    permission_classes = [AllowAny]  # Callbacks must be accessible without authentication
    
    def post(self, request):
        data = request.data
        print("M-Pesa Callback Data:", data)
        
        # Check if the payment was successful
        if data.get("Body", {}).get("stkCallback", {}).get("ResultCode") == 0:
            try:
                # Extract payment details from callback metadata
                callback_metadata = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
                
                # Extract amount, transaction ID, and phone number
                amount = next((item["Value"] for item in callback_metadata if item["Name"] == "Amount"), None)
                mpesa_receipt_number = next((item["Value"] for item in callback_metadata if item["Name"] == "MpesaReceiptNumber"), None)
                phone_number = next((item["Value"] for item in callback_metadata if item["Name"] == "PhoneNumber"), None)
                
                # Find user by phone number (you may need to adjust this logic)
                profile = Profile.objects.filter(phone_number__endswith=str(phone_number)[-9:]).first()
                
                if profile:
                    user = profile.user
                    # Find the user's unpaid cart
                    cart = Cart.objects.filter(user=user, is_paid=False).first()
                    
                    if cart:
                        # Create order
                        order = Order.objects.create(
                            user=user,
                            order_id=f"ORDER-{uuid.uuid4().hex[:8].upper()}",
                            total_amount=amount,
                            shipping_address=profile.shipping_address,
                            payment_method="M-Pesa",
                            payment_id=mpesa_receipt_number,
                            is_paid=True
                        )
                        
                        # Transfer cart items to order items
                        for cart_item in cart.cart_items.all():
                            OrderItem.objects.create(
                                order=order,
                                product=cart_item.product,
                                quantity=cart_item.quantity,
                                size_variant=cart_item.size_variant,
                                color_variant=cart_item.color_variant,
                                price=cart_item.get_product_price()
                            )
                        
                        # Mark cart as paid
                        cart.is_paid = True
                        cart.save()
                        
                        print(f"Order {order.order_id} created successfully for payment {mpesa_receipt_number}")
            
            except Exception as e:
                print(f"Error processing M-Pesa callback: {str(e)}")
        
        # Always return a 200 OK response to the M-Pesa API
        return Response({"message": "Callback received"}, status=status.HTTP_200_OK)

# Machine Learning
from sklearn.neighbors import NearestNeighbors
import pandas as pd
from products.models import Product

from accounts.models import OrderItem


from sklearn.neighbors import NearestNeighbors
import pandas as pd

class ProductRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = OrderItem.objects.all().values('order__user_id', 'product_id')
        df = pd.DataFrame(list(orders))

        if df.empty:
            return Response({"message": "No order data available for recommendations."}, status=status.HTTP_200_OK)

        user_product_matrix = df.pivot_table(index='order__user_id', columns='product_id', aggfunc='size', fill_value=0)

        if user_product_matrix.shape[0] < 2:
            return Response({"message": "Not enough data to generate recommendations."}, status=status.HTTP_200_OK)

        model = NearestNeighbors(metric='cosine', algorithm='brute')
        model.fit(user_product_matrix)

        user_id = request.user.id
        if user_id not in user_product_matrix.index:
            return Response({"message": "No recommendations available for this user."}, status=status.HTTP_200_OK)

        user_index = user_product_matrix.index.get_loc(user_id)
        
        # Set `n_neighbors` dynamically
        n_neighbors = min(5, user_product_matrix.shape[0])
        distances, indices = model.kneighbors(user_product_matrix.iloc[user_index, :].values.reshape(1, -1), n_neighbors=n_neighbors)
        recommended_product_ids = user_product_matrix.columns[indices.flatten()].tolist()
        recommended_products = Product.objects.filter(uid__in=recommended_product_ids)
        serializer = ProductSerializer(recommended_products, many=True)

        return Response({
            "message": "Product recommendations retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)





from datetime import datetime

class DynamicPricingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        base_price = product.price

        # Example: Increase price by 10% during peak hours (10 AM to 6 PM)
        now = datetime.now().time()
        if now.hour >= 10 and now.hour <= 18:
            dynamic_price = base_price * 1.10
        else:
            dynamic_price = base_price

        return Response({
            "message": "Dynamic price calculated successfully",
            "data": {
                "product_id": product.id,
                "base_price": base_price,
                "dynamic_price": dynamic_price
            }
        }, status=status.HTTP_200_OK)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import openai
import os
from dotenv import load_dotenv

import os
import openai
from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny

load_dotenv()

class ChatbotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get("message", "")
        user_role = request.data.get("user_role", "customer")

        if not user_message:
            return Response({"message": "No message provided", "data": {"bot_response": "Please enter a message."}}, status=status.HTTP_400_BAD_REQUEST)

        # Define a customized system prompt
        system_prompt = {
            "customer": "You are a friendly assistant for our company, providing product support and guidance.",
            "admin": "You are an AI assistant for system administrators, offering technical assistance."
        }.get(user_role, "You are a helpful chatbot.")

        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")

            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]

            response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
            bot_response = response["choices"][0]["message"]["content"]

            return Response({
                "message": "Chatbot response generated successfully",
                "data": {"user_message": user_message, "bot_response": bot_response}
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "Error generating chatbot response", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer

class ProductFilterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Get query parameters
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        sort_by = request.query_params.get('sort_by')  # 'price_asc', 'price_desc', 'name_asc', 'name_desc'
        search_query = request.query_params.get('search')

        # Start with all products
        products = Product.objects.all()

        # Filter by price range
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        # Search by product name or description
        if search_query:
            products = products.filter(
                Q(product_name__icontains=search_query) |
                Q(product_description__icontains=search_query)
            )

        # Sort products
        if sort_by == 'price_asc':
            products = products.order_by('price')
        elif sort_by == 'price_desc':
            products = products.order_by('-price')
        elif sort_by == 'name_asc':
            products = products.order_by('product_name')
        elif sort_by == 'name_desc':
            products = products.order_by('-product_name')

        # Serialize the filtered and sorted products
        serializer = ProductSerializer(products, many=True, context={"request": request})

        return Response({
            "message": "Products filtered successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer

class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all orders for the authenticated user, ordered by most recent
        orders = Order.objects.filter(user=request.user).order_by('-order_date')
        serializer = OrderSerializer(orders, many=True)
        return Response({
            "message": "Orders retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        # Fetch the specific order for the authenticated user
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response({
            "message": "Order details retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, order_id):
        # Only allow admin users to update order status
        if not request.user.is_staff:
            return Response({"message": "Only admin users can update order status"}, status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(Order, order_id=order_id)
        new_status = request.data.get('status')

        if new_status not in dict(Order.ORDER_STATUS_CHOICES).keys():
            return Response({"message": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        return Response({
            "message": "Order status updated successfully",
            "data": OrderSerializer(order).data
        }, status=status.HTTP_200_OK)
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer

class OrderTrackingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        # Fetch the order for the authenticated user
        order = get_object_or_404(Order, order_id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response({
            "message": "Order tracking details retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import csv
from .models import Order

class DownloadOrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch all orders for the authenticated user
        orders = Order.objects.filter(user=request.user).order_by('-order_date')

        # Create a CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="order_history.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Order ID', 'Order Date', 'Payment Status', 'Shipping Address', 
            'Payment Mode', 'Order Total', 'Grand Total', 'Status'
        ])

        for order in orders:
            writer.writerow([
                order.order_id, order.order_date, order.payment_status, 
                order.shipping_address, order.payment_mode, order.order_total_price, 
                order.grand_total, order.status
            ])

        return response
    
    