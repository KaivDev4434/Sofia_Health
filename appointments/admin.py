from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
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
        'confirmation_sent',
        'calendar_synced',
        'created_at',
    ]
    
    list_filter = [
        'is_paid',
        'appointment_type',
        'confirmation_sent',
        'calendar_synced',
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
        'google_calendar_event_id',
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
        ('Email & Calendar', {
            'fields': ('confirmation_sent', 'reminder_sent', 'calendar_synced', 'google_calendar_event_id')
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
    
    def changelist_view(self, request, extra_context=None):
        """Override changelist view to add analytics dashboard link."""
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = reverse('admin_dashboard')
        extra_context['show_dashboard_link'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    # Custom display methods
    def colored_payment_status(self, obj):
        """Display payment status with color."""
        if obj.is_paid:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Paid</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
        )
    colored_payment_status.short_description = 'Payment Status'
    
    def email_status(self, obj):
        """Display email status."""
        if obj.confirmation_sent:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">✗</span>')
    email_status.short_description = 'Email Sent'
    
    def calendar_status(self, obj):
        """Display calendar sync status."""
        if obj.calendar_synced:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: gray;">✗</span>')
    calendar_status.short_description = 'Calendar Synced'
