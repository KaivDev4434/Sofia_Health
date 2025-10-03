"""
Google Calendar and ICS file integration utilities.
Handles OAuth flow, event creation, and calendar file generation.
"""

from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def create_google_calendar_flow(request):
    """Create OAuth flow for Google Calendar authorization."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
                "client_secret": settings.GOOGLE_CALENDAR_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_CALENDAR_REDIRECT_URI]
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_CALENDAR_REDIRECT_URI
    )
    
    # Generate authorization URL
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    # Store state in session for security
    request.session['google_oauth_state'] = state
    
    return auth_url


def handle_google_calendar_callback(request):
    """Handle OAuth callback and store credentials in session."""
    try:
        state = request.session.get('google_oauth_state')
        if not state:
            return False, "Invalid state parameter"
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CALENDAR_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CALENDAR_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_CALENDAR_REDIRECT_URI]
                }
            },
            scopes=SCOPES,
            state=state,
            redirect_uri=settings.GOOGLE_CALENDAR_REDIRECT_URI
        )
        
        # Exchange authorization code for credentials
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        
        # Store credentials in session (in production, store in database)
        credentials = flow.credentials
        request.session['google_calendar_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        return True, "Calendar access granted"
        
    except Exception as e:
        logger.error(f"Google Calendar OAuth error: {str(e)}")
        return False, f"OAuth error: {str(e)}"


def create_calendar_event(appointment, credentials_dict=None):
    """Create Google Calendar event for appointment with reminders."""
    try:
        if not credentials_dict:
            return False, "No calendar credentials available"
        
        # Initialize Google Calendar API client
        credentials = Credentials.from_authorized_user_info(credentials_dict, SCOPES)
        
        # Build calendar service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Prepare event details
        event = {
            'summary': f'Appointment with {appointment.provider_name}',
            'description': f'Healthcare appointment\n\nProvider: {appointment.provider_name}\nType: {appointment.get_appointment_type_display()}\nAppointment ID: #{appointment.id}\n\nNotes: {appointment.notes or "None"}',
            'start': {
                'dateTime': appointment.appointment_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (appointment.appointment_time + timedelta(minutes=60)).isoformat(),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                    {'method': 'popup', 'minutes': 30},       # 30 minutes before
                ],
            },
            'attendees': [
                {'email': appointment.client_email, 'displayName': 'Patient'},
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f'appointment-{appointment.id}',
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            } if settings.DEBUG else None,  # Only in development
        }
        
        # Remove conference data if None
        if event['conferenceData'] is None:
            del event['conferenceData']
        
        # Create the event
        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'  # Send invites to attendees
        ).execute()
        
        logger.info(f"Calendar event created: {created_event['id']}")
        return True, created_event['id']
        
    except HttpError as e:
        logger.error(f"Google Calendar API error: {str(e)}")
        return False, f"Calendar API error: {str(e)}"
    except Exception as e:
        logger.error(f"Calendar event creation error: {str(e)}")
        return False, f"Error creating calendar event: {str(e)}"


def update_calendar_event(appointment, event_id, credentials_dict=None):
    """Update existing Google Calendar event with new appointment details."""
    try:
        if not credentials_dict:
            return False, "No calendar credentials available"
        
        credentials = Credentials.from_authorized_user_info(credentials_dict, SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
        
        # Get existing event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update event details
        event['summary'] = f'Appointment with {appointment.provider_name}'
        event['description'] = f'Healthcare appointment\n\nProvider: {appointment.provider_name}\nType: {appointment.get_appointment_type_display()}\nAppointment ID: #{appointment.id}\n\nNotes: {appointment.notes or "None"}'
        event['start'] = {
            'dateTime': appointment.appointment_time.isoformat(),
            'timeZone': 'UTC',
        }
        event['end'] = {
            'dateTime': (appointment.appointment_time + timedelta(minutes=60)).isoformat(),
            'timeZone': 'UTC',
        }
        
        # Update the event
        updated_event = service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event,
            sendUpdates='all'
        ).execute()
        
        logger.info(f"Calendar event updated: {updated_event['id']}")
        return True, updated_event['id']
        
    except Exception as e:
        logger.error(f"Calendar event update error: {str(e)}")
        return False, f"Error updating calendar event: {str(e)}"


def delete_calendar_event(event_id, credentials_dict=None):
    """Delete Google Calendar event by ID."""
    try:
        if not credentials_dict:
            return False, "No calendar credentials available"
        
        credentials = Credentials.from_authorized_user_info(credentials_dict, SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
        
        service.events().delete(
            calendarId='primary',
            eventId=event_id,
            sendUpdates='all'
        ).execute()
        
        logger.info(f"Calendar event deleted: {event_id}")
        return True, "Event deleted successfully"
        
    except Exception as e:
        logger.error(f"Calendar event deletion error: {str(e)}")
        return False, f"Error deleting calendar event: {str(e)}"


def generate_ics_file(appointment):
    """Generate ICS calendar file for universal calendar import."""
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Sofia Health//Healthcare Appointments//EN
BEGIN:VEVENT
UID:appointment-{appointment.id}@sofiahealth.com
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{appointment.appointment_time.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{(appointment.appointment_time + timedelta(minutes=60)).strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:Appointment with {appointment.provider_name}
DESCRIPTION:Healthcare appointment\\n\\nProvider: {appointment.provider_name}\\nType: {appointment.get_appointment_type_display()}\\nAppointment ID: #{appointment.id}\\n\\nNotes: {appointment.notes or "None"}
LOCATION:Contact {appointment.provider_name} for location details
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""
    
    return ics_content
