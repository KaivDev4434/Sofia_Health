"""
Appointment booking form with validation.
Handles provider selection, time validation, and form rendering.
"""

from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Appointment, Provider


class AppointmentForm(forms.ModelForm):
    """Form for creating appointment bookings with dynamic pricing."""
    
    class Meta:
        model = Appointment
        fields = ['provider', 'appointment_time', 'client_email', 'appointment_type', 'notes']
        widgets = {
            'provider': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_provider',
            }),
            'appointment_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'patient@example.com',
            }),
            'appointment_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_appointment_type',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Reason for visit or any notes...',
            }),
        }
        labels = {
            'provider': 'Select Healthcare Provider',
            'appointment_time': 'Appointment Date & Time',
            'client_email': 'Your Email Address',
            'appointment_type': 'Appointment Type',
            'notes': 'Notes (Optional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active providers
        self.fields['provider'].queryset = Provider.objects.filter(is_active=True)
        
        # Add help text
        self.fields['provider'].help_text = 'Select your healthcare provider'
        self.fields['appointment_type'].help_text = 'Pricing varies by appointment type'
    
    def clean_appointment_time(self):
        """
        Validate that appointment time is in the future.
        """
        appointment_time = self.cleaned_data.get('appointment_time')
        
        if appointment_time and appointment_time <= timezone.now():
            raise ValidationError(
                "Appointment time must be in the future. Please select a valid date and time."
            )
        
        return appointment_time
    
    def clean(self):
        """
        Additional validation for provider availability.
        """
        cleaned_data = super().clean()
        provider = cleaned_data.get('provider')
        
        if provider and not provider.is_active:
            raise ValidationError(
                f"{provider.name} is not currently accepting appointments."
            )
        
        return cleaned_data
