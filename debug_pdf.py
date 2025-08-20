import fitz  # PyMuPDF
import os

PDF_FILENAME = "test.pdf"

# Controlla se il file esiste
if not os.path.exists(PDF_FILENAME):
    print(f"ERRORE: File '{PDF_FILENAME}' non trovato.")
    print("Per favore, metti il tuo file PDF nella stessa cartella di questo script e rinominalo in 'test.pdf'")
else:
    print(f"--- Analisi del file: {PDF_FILENAME} ---")
    
    try:
        # Apri il documento
        pdf_document = fitz.open(PDF_FILENAME)
        
        # Itera su ogni pagina
        for page_num, page in enumerate(pdf_document):
            print(f"\n--- Analisi Pagina {page_num + 1} ---")
            
            # Estrai i blocchi di testo con le loro coordinate
            # (x0, y0, x1, y1, testo, numero_blocco, tipo_blocco)
            blocks = page.get_text("blocks")
            
            if not blocks:
                print("Nessun blocco di testo trovato in questa pagina. Potrebbe essere un'immagine scannerizzata.")
            else:
                print(f"Trovati {len(blocks)} blocchi di testo.")
                # Stampa le informazioni di ogni blocco
                for i, block in enumerate(blocks):
                    x0, y0, x1, y1, text, _, _ = block
                    # Pulisci il testo da eventuali ritorni a capo per una migliore leggibilità
                    clean_text = text.replace('\n', ' ').strip()
                    print(f"  Blocco {i}:")
                    print(f"    Coordinate: (x0={x0:.2f}, y0={y0:.2f}) -> (x1={x1:.2f}, y1={y1:.2f})")
                    print(f"    Testo: '{clean_text}'")

        print("\n--- Fine Analisi ---")

    except Exception as e:
        print(f"Si è verificato un errore durante l'apertura o la lettura del PDF: {e}")