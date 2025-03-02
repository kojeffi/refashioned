from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db import transaction
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User



def send_account_activation_email(user, email_token):  # ✅ Pass user instead of email
    subject = "Your account needs to be verified"
    email_from = settings.DEFAULT_FROM_EMAIL

    # ✅ Generate uidb64 from the User object
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    # ✅ Fix activation link
    activation_link = f'http://127.0.0.1:3000/verify-email?uidb64={uidb64}&token={token}'

    html_message = render_to_string(
        'emails/account_activation.html', {'activation_link': activation_link}
    )
    plain_message = f'Hi, please verify your account by clicking the link: {activation_link}'

    try:
        transaction.on_commit(lambda: send_mail(
            subject,
            plain_message,
            email_from,
            [user.email],  # ✅ Use user.email
            fail_silently=False,
            html_message=html_message
        ))

        return JsonResponse({'success': True, 'message': 'Activation email sent.'}, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
