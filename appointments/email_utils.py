"""
Email utilities for appointment notifications.
Handles confirmation, reminder, and provider notification emails.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def send_appointment_confirmation(appointment):
    """Send confirmation email to patient after successful booking."""
    try:
        subject = f"Appointment Confirmed - {appointment.provider_name}"
        
        context = {
            'appointment': appointment,
            'site_url': 'http://127.0.0.1:8000',  # In production, use actual domain
            'contact_email': 'support@sofiahealth.com',
        }
        
        html_message = render_to_string(
            'appointments/emails/confirmation.html',
            context
        )
        
        plain_message = render_to_string(
            'appointments/emails/confirmation.txt',
            context
        )
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.client_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Confirmation email sent to {appointment.client_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {str(e)}")
        return False


def send_appointment_reminder(appointment):
    """Send reminder email 24 hours before appointment."""
    try:
        subject = f"Appointment Reminder - {appointment.provider_name} Tomorrow"
        
        context = {
            'appointment': appointment,
            'site_url': 'http://127.0.0.1:8000',
            'contact_email': 'support@sofiahealth.com',
        }
        
        html_message = render_to_string(
            'appointments/emails/reminder.html',
            context
        )
        
        plain_message = render_to_string(
            'appointments/emails/reminder.txt',
            context
        )
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.client_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Reminder email sent to {appointment.client_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reminder email: {str(e)}")
        return False


def send_provider_notification(appointment):
    """Send notification to provider about new appointment booking."""
    try:
        # Get provider email (placeholder - would use appointment.provider.email in production)
        provider_email = "provider@sofiahealth.com"
        
        subject = f"New Appointment Booking - {appointment.client_email}"
        
        context = {
            'appointment': appointment,
            'site_url': 'http://127.0.0.1:8000',
            'admin_url': 'http://127.0.0.1:8000/admin/',
        }
        
        html_message = render_to_string(
            'appointments/emails/provider_notification.html',
            context
        )
        
        plain_message = render_to_string(
            'appointments/emails/provider_notification.txt',
            context
        )
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[provider_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Provider notification sent to {provider_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send provider notification: {str(e)}")
        return False


def schedule_appointment_reminder(appointment):
    """Schedule reminder email for 24h before appointment (Celery in production)."""
    # TODO: In production, use Celery for background scheduling
    # Example: send_reminder_email.apply_async(args=[appointment.id], eta=reminder_time)
    
    logger.info(f"Reminder scheduled for appointment {appointment.id} at {appointment.appointment_time - timedelta(hours=24)}")


def send_appointment_cancellation(appointment, reason=None):
    """Send cancellation notification with optional reason."""
    try:
        subject = f"Appointment Cancelled - {appointment.provider_name}"
        
        context = {
            'appointment': appointment,
            'reason': reason,
            'site_url': 'http://127.0.0.1:8000',
            'contact_email': 'support@sofiahealth.com',
        }
        
        html_message = render_to_string(
            'appointments/emails/cancellation.html',
            context
        )
        
        plain_message = render_to_string(
            'appointments/emails/cancellation.txt',
            context
        )
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.client_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Cancellation email sent to {appointment.client_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send cancellation email: {str(e)}")
        return False
