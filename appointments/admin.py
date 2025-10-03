from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Admin interface for Appointment model.
    """
    list_display = [
        'id',
        'provider_name',
        'client_email',
        'appointment_time',
        'appointment_type',
        'is_paid',
        'amount_paid',
        'created_at',
    ]
    
    list_filter = [
        'is_paid',
        'appointment_type',
        'appointment_time',
        'created_at',
    ]
    
    search_fields = [
        'provider_name',
        'client_email',
        'stripe_payment_intent_id',
    ]
    
    readonly_fields = [
        'stripe_payment_intent_id',
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('provider_name', 'appointment_time', 'appointment_type', 'notes')
        }),
        ('Patient Information', {
            'fields': ('client_email',)
        }),
        ('Payment Information', {
            'fields': ('is_paid', 'amount_paid', 'stripe_payment_intent_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'appointment_time'
    ordering = ['-appointment_time']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related if needed in future."""
        return super().get_queryset(request)
