from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
                  path('register/', views.register, name='register-url'),
                  path('activate/<uidb64>/<token>/', views.activate, name='activate'),
                  path('login/', views.user_login, name='login-url'),
                  path('dashboard/', views.dashboard, name='home-url'),
                  path('terms/', views.terms, name='terms'),
                  path('privacy/', views.privacy, name='privacy'),
                  path('accessibility/', views.accessibility, name='accessibility'),
                  path('cookies/', views.cookies, name='cookies'),
                  path('profile/', views.profile, name='profile-url'),
                  path('contact/', views.contact, name='contact'),
                  path('change_password/', views.change_password, name='change_password'),
                  path('chatbot_view/', views.chatbot_view, name='chatbot_view'),
                  path('subscribe/', views.subscribe, name='subscribe'),
                  path('about/', views.about, name='about'),
                  path('shipping/', views.shipping, name='shipping'),
                  path('logout/', views.logout_view, name='logout-url'),

                  path('social/login/', views.start_social_auth, name='social_login'),
                  path('social/complete/<backend>/', views.complete_social_auth, name='social_complete'),

                  path('password_reset/',
                       auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'),
                       name='password_reset'),
                  path('password_reset/done/',
                       auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
                       name='password_reset_done'),
                  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
                      template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
                  path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
                      template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)