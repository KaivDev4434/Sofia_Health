from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    """
    Form for creating new appointment bookings.
    """
    
    class Meta:
        model = Appointment
        fields = ['provider_name', 'appointment_time', 'client_email', 'appointment_type', 'notes']
        widgets = {
            'provider_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Dr. Sarah Johnson',
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
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Reason for visit or any notes...',
            }),
        }
        labels = {
            'provider_name': 'Healthcare Provider',
            'appointment_time': 'Appointment Date & Time',
            'client_email': 'Your Email Address',
            'appointment_type': 'Appointment Type',
            'notes': 'Notes (Optional)',
        }
    
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
    
    def clean_provider_name(self):
        """
        Clean and validate provider name.
        """
        provider_name = self.cleaned_data.get('provider_name')
        
        if provider_name:
            provider_name = provider_name.strip()
            if len(provider_name) < 2:
                raise ValidationError("Provider name must be at least 2 characters long.")
        
        return provider_name

