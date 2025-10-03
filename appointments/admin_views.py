"""
Custom admin dashboard for appointment analytics.
Displays metrics, revenue tracking, and performance indicators.
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import Appointment


@staff_member_required
def admin_dashboard(request):
    """Display analytics dashboard with key metrics and insights."""
    
    # Calculate date ranges for filtering
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)
    
    # Total statistics
    total_appointments = Appointment.objects.count()
    total_paid = Appointment.objects.filter(is_paid=True).count()
    total_revenue = Appointment.objects.filter(is_paid=True).aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    
    # Today's statistics
    today_appointments = Appointment.objects.filter(
        created_at__gte=today_start
    ).count()
    today_paid = Appointment.objects.filter(
        created_at__gte=today_start,
        is_paid=True
    ).count()
    
    # This week's statistics
    week_appointments = Appointment.objects.filter(
        created_at__gte=week_start
    ).count()
    week_revenue = Appointment.objects.filter(
        created_at__gte=week_start,
        is_paid=True
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # This month's statistics
    month_appointments = Appointment.objects.filter(
        created_at__gte=month_start
    ).count()
    month_revenue = Appointment.objects.filter(
        created_at__gte=month_start,
        is_paid=True
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Email & Calendar statistics
    email_sent = Appointment.objects.filter(confirmation_sent=True).count()
    calendar_synced = Appointment.objects.filter(calendar_synced=True).count()
    reminders_sent = Appointment.objects.filter(reminder_sent=True).count()
    
    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        appointment_time__gte=now,
        is_paid=True
    ).order_by('appointment_time')[:5]
    
    # Recent appointments
    recent_appointments = Appointment.objects.order_by('-created_at')[:5]
    
    # Appointment by type
    appointments_by_type = Appointment.objects.values(
        'appointment_type'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Top providers
    top_providers = Appointment.objects.values(
        'provider_name'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    # Payment statistics
    pending_payments = Appointment.objects.filter(is_paid=False).count()
    payment_success_rate = (total_paid / total_appointments * 100) if total_appointments > 0 else 0
    
    # Email & Calendar conversion rates
    email_conversion = (email_sent / total_appointments * 100) if total_appointments > 0 else 0
    calendar_conversion = (calendar_synced / total_paid * 100) if total_paid > 0 else 0
    
    # Average revenue per appointment
    avg_revenue = total_revenue / total_paid if total_paid > 0 else 0
    
    context = {
        'title': 'Sofia Health Analytics Dashboard',
        'site_header': 'Sofia Health Administration',
        
        # Overview statistics
        'total_appointments': total_appointments,
        'total_paid': total_paid,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'payment_success_rate': round(payment_success_rate, 1),
        'avg_revenue': round(avg_revenue, 2),
        
        # Time-based statistics
        'today_appointments': today_appointments,
        'today_paid': today_paid,
        'week_appointments': week_appointments,
        'week_revenue': week_revenue,
        'month_appointments': month_appointments,
        'month_revenue': month_revenue,
        
        # Email & Calendar statistics
        'email_sent': email_sent,
        'calendar_synced': calendar_synced,
        'reminders_sent': reminders_sent,
        'email_conversion': round(email_conversion, 1),
        'calendar_conversion': round(calendar_conversion, 1),
        
        # Lists
        'upcoming_appointments': upcoming_appointments,
        'recent_appointments': recent_appointments,
        'appointments_by_type': appointments_by_type,
        'top_providers': top_providers,
    }
    
    return render(request, 'admin/appointments/dashboard.html', context)

