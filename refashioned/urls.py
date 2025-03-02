from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("allauth.urls")),  # Django-Allauth routes
   
    path('api/', include('accounts.urls')),  
    path('api/', include('products.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT Login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # JWT Refresh
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
