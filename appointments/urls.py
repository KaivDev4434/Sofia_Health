from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_appointment, name='create_appointment'),
    path('<int:appointment_id>/payment/', views.appointment_payment, name='appointment_payment'),
    path('<int:appointment_id>/confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('<int:appointment_id>/success/', views.appointment_success, name='appointment_success'),
    path('stripe-status/', views.stripe_status, name='stripe_status'),
    
    # Calendar integration
    path('<int:appointment_id>/calendar/connect/', views.calendar_connect, name='calendar_connect'),
    path('calendar/callback/', views.calendar_callback, name='calendar_callback'),
    path('<int:appointment_id>/calendar/download/', views.download_calendar_file, name='download_calendar_file'),
    
    # Admin analytics dashboard
    path('admin-dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
]

