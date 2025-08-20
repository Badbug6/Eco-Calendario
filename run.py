# run.py

from waitress import serve
from app import app  # Importa l'oggetto 'app' dal tuo file app.py
import os

# --- Configurazione ---
HOST = '0.0.0.0'  # Ascolta su tutte le interfacce di rete
PORT = 8000       # La porta su cui l'app sarà disponibile

def main():
    """Funzione principale per avviare il server di produzione."""
    print("--- Avvio Server di Produzione con Waitress ---")
    print(f"L'applicazione sarà disponibile all'indirizzo: http://<il-tuo-ip>:{PORT}")
    print("Premi Ctrl+C per fermare il server.")
    
    # Controlla se i file essenziali esistono prima di partire
    essential_files = ['schedule.db', 'credentials.json', 'config.py']
    for filename in essential_files:
        if not os.path.exists(filename):
            print(f"\nATTENZIONE: File essenziale '{filename}' non trovato!")
            print("Assicurati che lo script sia eseguito dalla cartella principale del progetto.")
            # Puoi decidere di uscire se un file è critico
            # import sys
            # sys.exit(1)

    # serve() è la funzione di Waitress che avvia il server
    serve(app, host=HOST, port=PORT)

if __name__ == '__main__':
    main()