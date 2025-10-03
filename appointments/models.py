"""
Healthcare provider and appointment models.
Handles provider management, appointment bookings, and pricing.
"""

from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class Provider(models.Model):
    """Healthcare provider with customizable pricing per appointment type."""
    
    # Available medical specialties
    SPECIALTY_CHOICES = [
        ('general', 'General Practitioner'),
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('pediatrics', 'Pediatrics'),
        ('psychiatry', 'Psychiatry'),
        ('orthopedics', 'Orthopedics'),
        ('neurology', 'Neurology'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Healthcare provider's full name"
    )
    specialty = models.CharField(
        max_length=50,
        choices=SPECIALTY_CHOICES,
        default='general',
        help_text="Provider's specialty"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Provider's email for notifications"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Provider's contact phone"
    )
    consultation_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50.00,
        help_text="Price for consultation appointments"
    )
    follow_up_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=30.00,
        help_text="Price for follow-up appointments"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the provider is currently accepting appointments"
    )
    bio = models.TextField(
        blank=True,
        help_text="Provider's biography or description"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Healthcare Provider'
        verbose_name_plural = 'Healthcare Providers'
    
    def __str__(self):
        return f"{self.name} ({self.get_specialty_display()})"
    
    def get_price_for_appointment_type(self, appointment_type):
        """Get price based on appointment type."""
        if appointment_type == 'consultation':
            return self.consultation_price
        elif appointment_type == 'follow_up':
            return self.follow_up_price
        return self.consultation_price  # Default fallback


class Appointment(models.Model):
    """Patient appointment with payment tracking and integrations."""
    
    # Types of appointments available
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
    ]
    
    # Core required fields
    provider = models.ForeignKey(
        Provider,
        on_delete=models.PROTECT,
        related_name='appointments',
        null=True,  # Temporarily nullable for migration
        blank=True,
        help_text="Healthcare provider for this appointment"
    )
    provider_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Legacy provider name field - will be deprecated"
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
    
    # Calendar integration
    google_calendar_event_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Google Calendar event ID"
    )
    calendar_synced = models.BooleanField(
        default=False,
        help_text="Whether the appointment has been synced to calendar"
    )
    
    # Email notifications
    confirmation_sent = models.BooleanField(
        default=False,
        help_text="Whether confirmation email has been sent"
    )
    reminder_sent = models.BooleanField(
        default=False,
        help_text="Whether reminder email has been sent"
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
        provider_display = self.provider.name if self.provider else (self.provider_name or "Unknown Provider")
        return f"{provider_display} - {self.client_email} on {self.appointment_time.strftime('%Y-%m-%d %H:%M')}"
    
    def is_upcoming(self):
        """Check if appointment is in the future."""
        return self.appointment_time > timezone.now()
    
    def get_status(self):
        """Get human-readable status."""
        if self.is_paid:
            return "Confirmed" if self.is_upcoming() else "Completed"
        return "Pending Payment"
    
    def calculate_price(self):
        """Calculate price based on provider and appointment type."""
        if self.provider:
            return self.provider.get_price_for_appointment_type(self.appointment_type)
        # Fallback to default price
        return 50.00 if self.appointment_type == 'consultation' else 30.00
    
    def save(self, *args, **kwargs):
        """Override save to automatically set price based on provider and type."""
        if not self.pk and self.provider:  # Only on creation and if provider exists
            self.amount_paid = self.calculate_price()
        super().save(*args, **kwargs)
