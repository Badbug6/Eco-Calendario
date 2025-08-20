# utils/db_utils.py

import sqlite3
import shutil
from datetime import datetime
import os

# --- NUOVA LOGICA PER IL PERCORSO ROBUSTO ---
# Trova il percorso assoluto della cartella in cui si trova questo script (la cartella 'utils')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Vai su di un livello per trovare la cartella principale del progetto
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
# Costruisci il percorso assoluto e corretto per il database
DB_PATH = os.path.join(PROJECT_DIR, 'schedule.db')

def check_integrity():
    """Controlla l'integrità del file del database SQLite."""
    print(f"--- Controllo integrità di '{DB_PATH}' ---")
    if not os.path.exists(DB_PATH):
        print("ERRORE: File del database non trovato.")
        print("Assicurati di aver eseguito 'init_db.py' nella cartella principale.")
        return False
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        result = cursor.execute('PRAGMA integrity_check;').fetchone()
        conn.close()
        
        if result[0] == 'ok':
            print("Risultato: Integrità del database CONFERMATA. Il file è a posto.")
            return True
        else:
            print("ERRORE: Controllo di integrità FALLITO. Il database potrebbe essere corrotto.")
            print(f"Dettagli: {result}")
            return False
    except Exception as e:
        print(f"Si è verificato un errore durante la connessione al database: {e}")
        return False

def backup_database():
    """Crea una copia di sicurezza del database con un timestamp."""
    print("\n--- Creazione copia di sicurezza ---")
    if not os.path.exists(DB_PATH):
        print("ERRORE: File del database non trovato. Impossibile creare il backup.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"schedule_backup_{timestamp}.db"
    # Salva il backup nella cartella principale del progetto
    backup_path = os.path.join(PROJECT_DIR, backup_filename)
    
    try:
        shutil.copy(DB_PATH, backup_path)
        print(f"Backup creato con successo: '{backup_filename}'")
    except Exception as e:
        print(f"Si è verificato un errore durante la creazione del backup: {e}")

if __name__ == '__main__':
    is_ok = check_integrity()
    
    if is_ok:
        choice = input("\nVuoi creare una copia di sicurezza del database? (s/n): ").lower()
        if choice == 's':
            backup_database()
        else:
            print("Operazione annullata.")