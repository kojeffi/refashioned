from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views
from .views import index

urlpatterns = [
    path('', index, name='home-url'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)