from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, UserProfileForm
from .models import Profile, Message
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Subscription
from django.core.mail import send_mail
# from store.models import Notification

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string


def register(request):
    if request.method == 'POST':
        # Get the data from the form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')

        # Debug: check the received form data
        print("Form Data:", username, email, password1, password2)

        # Check if all required fields are provided
        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return redirect('register-url')

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register-url')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register-url')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register-url')

        # Create the user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.is_active = False  # Deactivate account until email is verified
            user.save()
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return redirect('register-url')

        # Send verification email
        current_site = get_current_site(request)
        mail_subject = 'Activate your account.'
        message = render_to_string('user_app/acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        to_email = email
        send_mail(mail_subject, message, 'omondijeff88@example.com', [to_email])

        messages.success(request, 'Please confirm your email address to complete the registration')
        return redirect('login-url')

    return render(request, 'user_app/register.html')




from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator


from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib import messages

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('login-url')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('register-url')


@login_required
def dashboard(request):
    user = request.user
    username = user.username
    email = user.email
    return render(request, 'store/index.html', {'username': username, 'email': email})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile-url')
    else:
        form = UserProfileForm()
    return render(request, 'store/index.html', {'form': form})

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import EmailLoginForm
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import EmailLoginForm
from django.contrib.auth.models import User
from datetime import datetime

def get_greeting():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = {
            'message': 'Good Morning!',
            'icon': 'fas fa-sun text-warning'
        }
    elif 12 <= current_hour < 17:
        greeting = {
            'message': 'Good Afternoon!',
            'icon': 'fas fa-cloud-sun text-primary'
        }
    else:
        greeting = {
            'message': 'Good Evening!',
            'icon': 'fas fa-moon text-info'
        }
    return greeting

def user_login(request):
    if request.method == 'POST':
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home-url')
                else:
                    messages.error(request, 'Invalid email or password.')
            except User.DoesNotExist:
                messages.error(request, 'User with this email does not exist.')
    else:
        form = EmailLoginForm()

    greeting = get_greeting()  # Get the greeting based on the current time
    return render(request, 'user_app/login.html', {'form': form, 'greeting': greeting})



@login_required
def profile(request):
    user = request.user
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile-url')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'user_app/overview.html', {'form': form})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Send email
        send_mail(
            subject,
            message,
            email,
            ['omondijeff88@gmail.com'],  # Change this to your email address
            fail_silently=False,
        )
        return JsonResponse({'success': True})

    return render(request, 'user_app/contact.html')

def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST['user_message']
        bot_response = generate_bot_response(user_message)  # Call a function to generate bot responses
        message = Message.objects.create(user_message=user_message, bot_response=bot_response)

        return render(request, 'index.html', {'message': message})
    else:
        return render(request, 'index.html', {})

def generate_bot_response(user_message):
    if 'hello' in user_message.lower():
        return "Hi there! How can I assist you today?"
    elif 'help' in user_message.lower():
        return "Sure, I'm here to help. What do you need assistance with?"
    elif 'how are you' in user_message.lower():
        return "I'm just a bot, but thanks for asking! How can I assist you?"
    elif 'bye' in user_message.lower():
        return "Goodbye! Feel free to return if you have more questions."
    else:
        return "Sorry, I didn't understand that. Can you please rephrase your question?"


from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from .models import Subscription

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not Subscription.objects.filter(email=email).exists():
            subscription = Subscription(email=email)
            subscription.save()

            subject = 'Subscription Confirmation'
            message = 'Thank you for subscribing!'
            sender_email = 'omondijeff88@gmail.com'
            recipient_list = [email]
            send_mail(subject, message, sender_email, recipient_list)

            # Redirect to home with success message
            return HttpResponseRedirect(reverse('home-url') + '?success_message=Thank+you+for+subscribing!')
        else:
            # Redirect to home with error message
            return HttpResponseRedirect(reverse('home-url') + '?error_message=Email+already+subscribed!')
    else:
        # If the request method is GET, render the subscription form
        success_message = request.GET.get('success_message', '')
        error_message = request.GET.get('error_message', '')
        return render(request, 'store/index.html', {
            'success_message': success_message,
            'error_message': error_message,
        })

def about(request):
    return render(request, 'user_app/about.html')

def shipping(request):
    return render(request, 'user_app/shipping.html')




@login_required
def terms(request):
    return render(request, 'store/terms.html')


@login_required
def privacy(request):
    return render(request, 'store/privacy.html')


@login_required
def cookies(request):
    return render(request, 'store/cookies.html')


@login_required
def accessibility(request):
    return render(request, 'store/accessibility.html')


from django.shortcuts import render, redirect
from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    return render(request, 'user_app/logout.html')



from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import Profile, Message, Subscription
from store.serializers import UserSerializer, ProfileSerializer, MessageSerializer, SubscriptionSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


from django.shortcuts import redirect
from social_django.views import auth, complete

def start_social_auth(request, backend):
    return auth(request, backend)

def complete_social_auth(request, backend):
    return complete(request, backend, redirect_name='next')


