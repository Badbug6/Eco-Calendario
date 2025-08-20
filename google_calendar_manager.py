# google_calendar_manager.py

import os.path
from datetime import datetime, time, timedelta
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import CALENDAR_ID

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

DAY_MAP = {
    "Lunedì": "MO", "Martedì": "TU", "Mercoledì": "WE",
    "Giovedì": "TH", "Venerdì": "FR", "Sabato": "SA", "Domenica": "SU"
}

def authenticate_google_calendar():
    """Autentica e restituisce il servizio per l'API di Google Calendar."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            
    return build("calendar", "v3", credentials=creds)

def get_next_weekday(start_date, weekday_str):
    """Calcola la prossima data per un dato giorno della settimana."""
    weekdays = list(DAY_MAP.keys())
    target_weekday = weekdays.index(weekday_str)
    days_ahead = (target_weekday - start_date.weekday() + 7) % 7
    if days_ahead == 0:
        days_ahead = 7
    return start_date + timedelta(days=days_ahead)

def create_recurring_event(service, waste_type, day_of_week, time_str, color_id):
    """Crea un evento ricorrente settimanale per un tipo di rifiuto."""
    
    event_time = time.fromisoformat(time_str)
    timezone = 'Europe/Rome'
    
    today = datetime.now(pytz.timezone(timezone)).date()
    start_date = get_next_weekday(today, day_of_week)
    
    start_datetime = datetime.combine(start_date, event_time, tzinfo=pytz.timezone(timezone))
    end_datetime = start_datetime + timedelta(hours=1)
    
    rrule_day = DAY_MAP[day_of_week]
    
    event = {
        'summary': f"♻️ Raccolta: {waste_type}",
        'description': 'Evento generato automaticamente dall\'app di Raccolta Differenziata.\n#raccoltadifferenziata',
        'start': {'dateTime': start_datetime.isoformat(), 'timeZone': timezone},
        'end': {'dateTime': end_datetime.isoformat(), 'timeZone': timezone},
        'recurrence': [f'RRULE:FREQ=WEEKLY;BYDAY={rrule_day}'],
        'colorId': color_id
    }

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"Evento '{created_event['summary']}' creato con successo.")
    return created_event

def delete_all_waste_events(service):
    """Trova e cancella tutti gli eventi di raccolta differenziata creati dall'app."""
    print("Ricerca di vecchi eventi da cancellare...")
    events_to_delete = []
    page_token = None
    
    while True:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            q="#raccoltadifferenziata",
            pageToken=page_token
        ).execute()
        
        events = events_result.get('items', [])
        events_to_delete.extend(events)
        
        page_token = events_result.get('nextPageToken')
        if not page_token:
            break
            
    if not events_to_delete:
        print("Nessun evento precedente da cancellare.")
        return 0

    print(f"Trovati {len(events_to_delete)} eventi da cancellare.")
    for event in events_to_delete:
        try:
            service.events().delete(calendarId=CALENDAR_ID, eventId=event['id']).execute()
            print(f"  - Evento '{event['summary']}' ({event['id']}) cancellato.")
        except Exception as e:
            print(f"Errore durante la cancellazione dell'evento {event['id']}: {e}")

    return len(events_to_delete)