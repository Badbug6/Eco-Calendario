# WebApp Gestione Rifiuti

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Una web application self-hosted per la gestione completa della raccolta differenziata domestica. Permette di configurare un calendario di raccolta, sincronizzarlo con Google Calendar e consultare un dizionario dei rifiuti, interamente personalizzabile e popolabile tramite l'upload di PDF (anche scannerizzati) grazie all'OCR.

---

### Screenshot dell'Applicazione

*(Suggerimento: Sostituisci `screenshot.png` con uno screenshot della tua applicazione in esecuzione!)*
![Screenshot App](screenshot.png)

---

## 🎯 Caratteristiche Principali

*   **📅 Calendario di Raccolta Personalizzato:**
    *   Interfaccia web per aggiungere, modificare ed eliminare i promemoria di raccolta.
    *   Dati salvati in modo persistente su un database SQLite.
*   **🎨 Gestione Tipi di Rifiuto:**
    *   Aggiungi, modifica ed elimina i tipi di rifiuto (es. Organico, Vetro).
    *   Assegna un colore unico per ogni tipo di rifiuto per una visualizzazione chiara su Google Calendar.
*   **🔄 Sincronizzazione con Google Calendar:**
    *   Crea eventi ricorrenti settimanali sul tuo Google Calendar con un solo click.
    *   Gestisce la pulizia dei vecchi eventi per evitare duplicati.
*   **📚 Dizionario dei Rifiuti Intelligente:**
    *   Un elenco A-Z consultabile per sapere dove conferire ogni tipo di rifiuto.
    *   Gestione completa (CRUD) delle voci del dizionario.
    *   **Importazione da PDF con OCR:** Carica un PDF (anche scannerizzato) e l'app userà l'OCR Tesseract per estrarre i dati e popolare automaticamente il dizionario.
*   **🚀 Pronto per la Produzione:**
    *   Architettura basata sul server WSGI **Waitress**, stabile e multipiattaforma (Windows, macOS, Linux).
    *   Script di avvio separato (`run.py`) per un facile deployment.
*   **🔧 Strumenti di Diagnostica:**
    *   Utility per il controllo di integrità e il backup del database.
    *   Script di test per verificare la connessione e l'autenticazione con l'API di Google.

---

## 🛠️ Stack Tecnologico

*   **Backend:** Python 3
*   **Framework:** Flask
*   **Server WSGI (Produzione):** Waitress
*   **Database:** SQLite 3
*   **Google API:** Google Calendar API v3
*   **PDF e OCR:** PyMuPDF, Pytesseract e **Tesseract OCR** (dipendenza di sistema)
*   **Frontend:** HTML5, Bootstrap 5

---

## 🚀 Installazione e Configurazione

Segui questi passaggi per mettere in funzione l'applicazione.

### 1. Prerequisiti di Sistema: Tesseract OCR

Questa è l'unica dipendenza esterna a Python.

*   **Windows:** Scarica l'installer da [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). **Importante:** Durante l'installazione, assicurati di selezionare il pacchetto della lingua **Italiano (`Italian`)**.
*   **macOS (con Homebrew):** `brew install tesseract tesseract-lang`
*   **Linux (Debian/Ubuntu/Raspberry Pi OS):** `sudo apt update && sudo apt install tesseract-ocr tesseract-ocr-ita`

### 2. Clona e Prepara l'Ambiente

```bash
# Clona il repository (o semplicemente scarica e scompatta lo ZIP)
git clone https://.../tuo-progetto.git
cd tuo-progetto

# (Consigliato) Crea un ambiente virtuale
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# Installa tutte le dipendenze Python
pip install -r requirements.txt
```

### 3. Configurazione dell'API di Google Calendar

1.  Vai alla [Google Cloud Console](https://console.cloud.google.com/) e crea un nuovo progetto.
2.  Abilita l'**API di Google Calendar** per il tuo progetto.
3.  Vai a **Credenziali > `+ CREA CREDENZIALI` > ID client OAuth**.
4.  Come **Tipo di applicazione**, seleziona **Applicazione desktop**.
5.  Scarica il file JSON, **rinominalo in `credentials.json`** e mettilo nella cartella principale del progetto.
6.  Vai alla **Schermata di consenso OAuth**, nella sezione **Tester**, clicca su `+ ADD USERS` e aggiungi il tuo indirizzo email Google.

### 4. Inizializzazione del Database

Esegui questo comando **una sola volta** per creare il file del database (`schedule.db`) con tutte le tabelle e i dati di default.

```bash
python init_db.py```

---

## ⚙️ Utilizzo

### Per la Produzione (Consigliato)

Per avviare l'app con il server stabile **Waitress**. Questo è il metodo da usare per il funzionamento 24/7.

```bash
python run.py
```
L'app sarà disponibile sulla tua rete locale all'indirizzo `http://<IL_TUO_INDIRIZZO_IP>:8000`.

### Per Sviluppo e Test

Per lanciare l'app con il server di debug di Flask (che si ricarica automaticamente alle modifiche).

```bash
python app.py
```
L'app sarà disponibile su `http://localhost:5000`.

---

## 🔧 Strumenti di Diagnostica

Nella cartella `utils/` troverai degli script utili da lanciare dalla cartella principale.

*   **Testare la connessione a Google:**
    ```bash
    python utils/test_google_api.py
    ```
*   **Controllare e fare il backup del database:**
    ```bash
    python utils/db_utils.py
    ```

---

## 📜 Licenza

Questo progetto è rilasciato sotto la Licenza MIT.
