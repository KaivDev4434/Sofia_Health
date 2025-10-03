from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class Appointment(models.Model):
    """
    Model representing a healthcare appointment booking.
    """
    
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
    ]
    
    # Core required fields
    provider_name = models.CharField(
        max_length=200,
        help_text="Name of the healthcare provider"
    )
    appointment_time = models.DateTimeField(
        help_text="Scheduled date and time for the appointment"
    )
    client_email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Patient's email address"
    )
    
    # Payment tracking
    is_paid = models.BooleanField(
        default=False,
        help_text="Whether the appointment has been paid for"
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50.00,
        help_text="Amount paid for the appointment"
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stripe PaymentIntent ID for this transaction"
    )
    
    # Healthcare context
    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPE_CHOICES,
        default='consultation',
        help_text="Type of appointment"
    )
    notes = models.TextField(
        blank=True,
        help_text="Patient notes or reason for visit"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_time']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
    
    def __str__(self):
        return f"{self.provider_name} - {self.client_email} on {self.appointment_time.strftime('%Y-%m-%d %H:%M')}"
    
    def is_upcoming(self):
        """Check if appointment is in the future."""
        return self.appointment_time > timezone.now()
    
    def get_status(self):
        """Get human-readable status."""
        if self.is_paid:
            return "Confirmed" if self.is_upcoming() else "Completed"
        return "Pending Payment"
