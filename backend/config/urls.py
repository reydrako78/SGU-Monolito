from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# AdminSite personalizado — solo superusuarios o can_access_django_admin
from core.admin import university_admin_site

urlpatterns = [
    # Panel técnico (Django Admin) — URL no-obvia + middleware de protección
    path('system-admin/', university_admin_site.urls),

    # OAuth (Google / Microsoft)
    path('accounts/', include('allauth.urls')),

    # JWT Tokens
    path('api/token/',         TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # API REST + Panel personalizado (core)
    path('', include('core.urls')),

    # Monolithic Apps API
    path('api/curriculum/', include('curriculum.urls')),
    path('api/students/', include('students.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/enrollments/', include('enrollments.urls')),
    path('api/grades/', include('grades.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
