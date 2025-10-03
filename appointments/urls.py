from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_appointment, name='create_appointment'),
    path('<int:appointment_id>/payment/', views.appointment_payment, name='appointment_payment'),
    path('<int:appointment_id>/confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('<int:appointment_id>/success/', views.appointment_success, name='appointment_success'),
    path('stripe-status/', views.stripe_status, name='stripe_status'),
]

