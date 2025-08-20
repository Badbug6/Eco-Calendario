# utils/test_google_api.py

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- NUOVA LOGICA PER I PERCORSI ROBUSTI ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
CREDENTIALS_PATH = os.path.join(PROJECT_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(PROJECT_DIR, 'token.json')

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def test_authentication():
    """Tenta di autenticarsi e restituisce l'oggetto service se ha successo."""
    print("--- 1. Test di Autenticazione ---")
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token scaduto. Tentativo di refresh...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"ERRORE: Impossibile aggiornare il token. Potrebbe essere necessario ri-autorizzare.")
                print(f"Dettaglio: {e}")
                return None
        else:
            print("Token non trovato o non valido. Avvio del flusso di autorizzazione...")
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"ERRORE: File '{CREDENTIALS_PATH}' non trovato. Impossibile autenticarsi.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    
    print("Autenticazione COMPLETATA con successo.")
    return build("calendar", "v3", credentials=creds)

def test_api_connection(service):
    """Esegue un test di sola lettura per verificare la connessione all'API."""
    print("\n--- 2. Test di Connessione API (Lettura Calendari) ---")
    try:
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])

        if not calendars:
            print("Nessun calendario trovato nel tuo account.")
        else:
            print("Connessione API CONFERMATA. Elenco dei calendari trovati:")
            for calendar in calendars:
                summary = calendar['summary']
                cal_id = calendar['id']
                print(f"  - Nome: {summary} (ID: {cal_id})")
        return True
    except HttpError as e:
        print(f"ERRORE HTTP durante la comunicazione con l'API di Google.")
        print(f"Codice: {e.resp.status}, Motivo: {e.reason}")
        if e.resp.status == 403:
            print("Questo errore (403 Forbidden) spesso significa che l'API di Google Calendar non è abilitata nel tuo progetto Google Cloud.")
        return False
    except Exception as e:
        print(f"Si è verificato un errore imprevisto: {e}")
        return False

if __name__ == '__main__':
    print("Avvio dello script di diagnostica per l'API di Google Calendar...")
    service = test_authentication()
    
    if service:
        test_api_connection(service)
    else:
        print("\nDiagnostica interrotta a causa di fallimento nell'autenticazione.")