"""
Django admin configuration for appointments and providers.
Enhanced with custom displays, filters, and analytics dashboard.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Appointment, Provider


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin interface for appointments with enhanced tracking."""
    list_display = [
        'id',
        'provider',
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
        'provider',
        'appointment_type',
        'confirmation_sent',
        'calendar_synced',
        'appointment_time',
        'created_at',
    ]
    
    search_fields = [
        'provider__name',
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
            'fields': ('provider', 'appointment_time', 'appointment_type', 'notes')
        }),
        ('Patient Information', {
            'fields': ('client_email',)
        }),
        ('Payment Information', {
            'fields': ('is_paid', 'amount_paid', 'stripe_payment_intent_id'),
            'description': 'Amount is automatically calculated based on provider and appointment type'
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


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    """Admin interface for providers with pricing and revenue tracking."""
    list_display = [
        'id',
        'name',
        'specialty',
        'consultation_price',
        'follow_up_price',
        'is_active',
        'appointment_count',
        'created_at',
    ]
    
    list_filter = [
        'is_active',
        'specialty',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'email',
        'specialty',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'appointment_count',
        'total_revenue',
    ]
    
    fieldsets = (
        ('Provider Information', {
            'fields': ('name', 'specialty', 'email', 'phone', 'is_active')
        }),
        ('Pricing Configuration', {
            'fields': ('consultation_price', 'follow_up_price'),
            'description': 'Set different prices for consultation and follow-up appointments'
        }),
        ('About', {
            'fields': ('bio',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('appointment_count', 'total_revenue'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def appointment_count(self, obj):
        """Display total number of appointments."""
        count = obj.appointments.count()
        return format_html(
            '<span style="font-weight: bold; color: #417690;">{}</span>',
            count
        )
    appointment_count.short_description = 'Total Appointments'
    
    def total_revenue(self, obj):
        """Display total revenue from this provider."""
        from django.db.models import Sum
        revenue = obj.appointments.filter(is_paid=True).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        return format_html(
            '<span style="font-weight: bold; color: green;">${}</span>',
            f'{revenue:.2f}'
        )
    total_revenue.short_description = 'Total Revenue'
    
    def save_model(self, request, obj, form, change):
        """Custom save to handle price updates."""
        super().save_model(request, obj, form, change)
        
        # Optionally update future unpaid appointments with new prices
        if change and ('consultation_price' in form.changed_data or 'follow_up_price' in form.changed_data):
            # This is optional - you might not want to update existing appointments
            pass
