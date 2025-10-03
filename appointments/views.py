from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_http_methods
import stripe

from .models import Appointment
from .forms import AppointmentForm

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_appointment(request):
    """
    View for creating a new appointment.
    GET: Display the appointment booking form
    POST: Process form submission and redirect to payment
    """
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.amount_paid = settings.APPOINTMENT_PRICE / 100  # Convert cents to dollars
            appointment.save()
            
            messages.success(request, 'Appointment details saved! Please complete payment to confirm.')
            return redirect('appointment_payment', appointment_id=appointment.id)
    else:
        form = AppointmentForm()
    
    context = {
        'form': form,
        'appointment_price': settings.APPOINTMENT_PRICE / 100,  # Display in dollars
    }
    return render(request, 'appointments/create.html', context)


def appointment_payment(request, appointment_id):
    """
    View for displaying payment page and creating Stripe PaymentIntent.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Redirect if already paid
    if appointment.is_paid:
        messages.info(request, 'This appointment has already been paid for.')
        return redirect('appointment_success', appointment_id=appointment.id)
    
    # Create Stripe PaymentIntent
    payment_intent = None
    error = None
    
    try:
        if not appointment.stripe_payment_intent_id:
            # Create new PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=settings.APPOINTMENT_PRICE,
                currency='usd',
                description=f'Appointment with {appointment.provider_name}',
                metadata={
                    'appointment_id': appointment.id,
                    'client_email': appointment.client_email,
                }
            )
            
            # Save PaymentIntent ID
            appointment.stripe_payment_intent_id = payment_intent.id
            appointment.save()
        else:
            # Retrieve existing PaymentIntent
            payment_intent = stripe.PaymentIntent.retrieve(appointment.stripe_payment_intent_id)
    
    except stripe.error.StripeError as e:
        error = str(e)
        messages.error(request, f'Payment error: {error}')
    
    context = {
        'appointment': appointment,
        'payment_intent': payment_intent,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'error': error,
    }
    return render(request, 'appointments/payment.html', context)


@require_http_methods(["POST"])
def confirm_payment(request, appointment_id):
    """
    View for confirming payment (mock confirmation for MVP).
    In production, this would be handled by Stripe webhooks.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Mock payment confirmation
    # In production, verify with Stripe API
    if appointment.stripe_payment_intent_id:
        try:
            # Retrieve PaymentIntent to check status
            payment_intent = stripe.PaymentIntent.retrieve(appointment.stripe_payment_intent_id)
            
            # For this MVP, we'll mark as paid for demonstration
            # In production, only mark as paid when payment_intent.status == 'succeeded'
            appointment.is_paid = True
            appointment.save()
            
            messages.success(request, 'Payment confirmed! Your appointment is booked.')
            return redirect('appointment_success', appointment_id=appointment.id)
        
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment verification failed: {str(e)}')
            return redirect('appointment_payment', appointment_id=appointment.id)
    
    messages.error(request, 'No payment information found.')
    return redirect('appointment_payment', appointment_id=appointment.id)


def appointment_success(request, appointment_id):
    """
    View for displaying successful appointment booking confirmation.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/success.html', context)


def home(request):
    """
    Simple home page redirecting to appointment creation.
    """
    return redirect('create_appointment')


def stripe_status(request):
    """
    Display Stripe configuration status (test vs live mode).
    """
    stripe_config = {
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'secret_key': settings.STRIPE_SECRET_KEY[:12] + '...' if settings.STRIPE_SECRET_KEY else 'Not set',
        'is_test_mode': settings.STRIPE_SECRET_KEY.startswith('sk_test_') if settings.STRIPE_SECRET_KEY else False,
        'is_live_mode': settings.STRIPE_SECRET_KEY.startswith('sk_live_') if settings.STRIPE_SECRET_KEY else False,
        'appointment_price': settings.APPOINTMENT_PRICE / 100,
    }
    
    return render(request, 'appointments/stripe_status.html', {'config': stripe_config})
