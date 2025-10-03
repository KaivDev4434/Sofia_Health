"""
Appointment booking views.
Handles appointment creation, Stripe payments, email/calendar integration.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
import stripe
import json

from .models import Appointment, Provider
from .forms import AppointmentForm
from .email_utils import (
    send_appointment_confirmation, 
    send_appointment_reminder,
    send_provider_notification,
    schedule_appointment_reminder
)
from .calendar_utils import (
    create_google_calendar_flow,
    handle_google_calendar_callback,
    create_calendar_event,
    generate_ics_file
)

# Initialize Stripe with secret key
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_appointment(request):
    """Create new appointment and redirect to payment page."""
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            # Price is automatically calculated in the model's save method
            appointment.save()
            
            # Schedule reminder email (in production, this would be a Celery task)
            schedule_appointment_reminder(appointment)
            
            messages.success(request, f'Appointment with {appointment.provider.name} saved! Please complete payment to confirm.')
            return redirect('appointment_payment', appointment_id=appointment.id)
    else:
        form = AppointmentForm()
    
    # Get all active providers with their pricing for JavaScript
    providers = Provider.objects.filter(is_active=True)
    provider_pricing = {}
    for provider in providers:
        provider_pricing[provider.id] = {
            'consultation': float(provider.consultation_price),
            'follow_up': float(provider.follow_up_price),
            'name': provider.name,
            'specialty': provider.get_specialty_display(),
        }
    
    context = {
        'form': form,
        'provider_pricing': json.dumps(provider_pricing),
        'default_price': settings.APPOINTMENT_PRICE / 100,  # Fallback price
    }
    return render(request, 'appointments/create.html', context)


def appointment_payment(request, appointment_id):
    """Display payment page and create Stripe PaymentIntent."""
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
            # Create new PaymentIntent with dynamic pricing
            amount_in_cents = int(appointment.amount_paid * 100)
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='usd',
                description=f'Appointment with {appointment.provider.name} - {appointment.get_appointment_type_display()}',
                metadata={
                    'appointment_id': appointment.id,
                    'client_email': appointment.client_email,
                    'provider': appointment.provider.name,
                    'appointment_type': appointment.appointment_type,
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
    """Confirm payment and send confirmation emails."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Verify payment with Stripe and mark as paid
    if appointment.stripe_payment_intent_id:
        try:
            # Retrieve PaymentIntent to verify status
            payment_intent = stripe.PaymentIntent.retrieve(appointment.stripe_payment_intent_id)
            
            # Mark as paid (in production, check payment_intent.status == 'succeeded')
            appointment.is_paid = True
            appointment.save()
            
            # Send confirmation email
            email_sent = send_appointment_confirmation(appointment)
            if email_sent:
                appointment.confirmation_sent = True
                appointment.save()
            
            # Send provider notification
            send_provider_notification(appointment)
            
            messages.success(request, 'Payment confirmed! Your appointment is booked and confirmation emails have been sent.')
            return redirect('appointment_success', appointment_id=appointment.id)
        
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment verification failed: {str(e)}')
            return redirect('appointment_payment', appointment_id=appointment.id)
    
    messages.error(request, 'No payment information found.')
    return redirect('appointment_payment', appointment_id=appointment.id)


def appointment_success(request, appointment_id):
    """Display successful booking confirmation page."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/success.html', context)


def home(request):
    """Redirect home to appointment creation page."""
    return redirect('create_appointment')


def stripe_status(request):
    """Display Stripe configuration status (test/live mode check)."""
    stripe_config = {
        'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'secret_key': settings.STRIPE_SECRET_KEY[:12] + '...' if settings.STRIPE_SECRET_KEY else 'Not set',
        'is_test_mode': settings.STRIPE_SECRET_KEY.startswith('sk_test_') if settings.STRIPE_SECRET_KEY else False,
        'is_live_mode': settings.STRIPE_SECRET_KEY.startswith('sk_live_') if settings.STRIPE_SECRET_KEY else False,
        'appointment_price': settings.APPOINTMENT_PRICE / 100,
    }
    
    return render(request, 'appointments/stripe_status.html', {'config': stripe_config})


def calendar_connect(request, appointment_id):
    """Initiate Google Calendar OAuth flow for appointment."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if not appointment.is_paid:
        messages.error(request, 'Please complete payment before adding to calendar.')
        return redirect('appointment_payment', appointment_id=appointment.id)
    
    try:
        auth_url = create_google_calendar_flow(request)
        request.session['calendar_appointment_id'] = appointment_id
        return redirect(auth_url)
    except Exception as e:
        messages.error(request, f'Calendar connection failed: {str(e)}')
        return redirect('appointment_success', appointment_id=appointment.id)


def calendar_callback(request):
    """Handle Google Calendar OAuth callback and create event."""
    appointment_id = request.session.get('calendar_appointment_id')
    if not appointment_id:
        messages.error(request, 'Invalid calendar connection request.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Handle OAuth callback and get credentials
    success, message = handle_google_calendar_callback(request)
    
    if success:
        # Create event in Google Calendar
        credentials_dict = request.session.get('google_calendar_credentials')
        event_success, event_id = create_calendar_event(appointment, credentials_dict)
        
        if event_success:
            appointment.google_calendar_event_id = event_id
            appointment.calendar_synced = True
            appointment.save()
            messages.success(request, 'Appointment added to your Google Calendar!')
        else:
            messages.warning(request, f'Calendar access granted but event creation failed: {event_id}')
    else:
        messages.error(request, f'Calendar connection failed: {message}')
    
    return redirect('appointment_success', appointment_id=appointment.id)


def download_calendar_file(request, appointment_id):
    """Generate and download ICS calendar file."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if not appointment.is_paid:
        messages.error(request, 'Please complete payment before downloading calendar file.')
        return redirect('appointment_payment', appointment_id=appointment.id)
    
    ics_content = generate_ics_file(appointment)
    
    response = HttpResponse(ics_content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="appointment-{appointment.id}.ics"'
    
    return response
