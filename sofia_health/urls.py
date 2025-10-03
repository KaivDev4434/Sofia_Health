"""
Main URL configuration for Sofia Health project.
Routes: admin panel, appointment booking, and home redirect.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Redirect root to appointments
    path("", RedirectView.as_view(url='/appointments/', permanent=False), name='home_redirect'),
    
    # Django admin interface
    path("admin/", admin.site.urls),
    
    # Appointments app (booking, payment, calendar)
    path("appointments/", include('appointments.urls')),
]
