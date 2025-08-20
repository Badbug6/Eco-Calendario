import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import os

PDF_FILENAME = "test.pdf"

### PER UTENTI WINDOWS ###
# Assicurati che questo percorso sia corretto!
# Se sei su Mac o Linux, puoi commentare o cancellare questa riga.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Controlla se il file esiste
if not os.path.exists(PDF_FILENAME):
    print(f"ERRORE: File '{PDF_FILENAME}' non trovato.")
    print("Per favore, metti il tuo file PDF nella stessa cartella e rinominalo in 'test.pdf'")
else:
    print(f"--- Inizio analisi OCR su: {PDF_FILENAME} ---")
    
    try:
        # Apri il documento
        pdf_document = fitz.open(PDF_FILENAME)
        
        full_text_from_ocr = ""
        
        # Itera su ogni pagina
        for page_num, page in enumerate(pdf_document):
            print(f"\n--- Elaborazione Pagina {page_num + 1} ---")
            
            # Converte la pagina in un'immagine ad alta risoluzione
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            
            # Esegui l'OCR sull'immagine
            print("Esecuzione di Tesseract OCR (potrebbe richiedere qualche secondo)...")
            text = pytesseract.image_to_string(image, lang='ita')
            full_text_from_ocr += text
        
        print("\n\n--- OUTPUT GREZZO DELL'OCR ---")
        print("Quello che segue è esattamente il testo che Tesseract ha letto dall'immagine.")
        print("----------------------------------")
        print(full_text_from_ocr)
        print("----------------------------------")
        print("--- Fine Analisi ---")
        print("\nPer favore, copia tutto il testo da '--- OUTPUT GREZZO...' fino a qui e incollalo nella chat.")

    except Exception as e:
        print(f"\nSi è verificato un errore durante il processo OCR: {e}")
        print("Possibili cause:")
        print("1. Tesseract non è installato o il percorso non è corretto (controlla la riga 'pytesseract.pytesseract.tesseract_cmd').")
        print("2. I dati della lingua italiana ('ita') non sono installati.")
        print("3. Il file PDF è corrotto o vuoto.")