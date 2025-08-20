# app.py

import sqlite3
import fitz  # PyMuPDF
import os
from flask import Flask, render_template, request, flash, redirect, url_for, g, abort
import pytesseract
from PIL import Image
import io # Per gestire i dati delle immagini in memoria

# Ora importiamo GOOGLE_CALENDAR_COLORS, non WASTE_TYPES_CONFIG
from config import GOOGLE_CALENDAR_COLORS
import google_calendar_manager

### PER UTENTI WINDOWS ###
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# --- FUNZIONE HELPER PER IL PARSING OCR (IBRIDA) ---
def parse_pdf_with_ocr(pdf_bytes):
    """
    Analizza un PDF basato su immagine usando OCR e un parser ibrido.
    """
    matched_pairs = []
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = ""
        for page in pdf_document:
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            full_text += pytesseract.image_to_string(image, lang='ita')

        if full_text:
            known_exceptions = ["ditta Specializzata", "RAEE / Rivenditore"]
            lines = full_text.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                found_match = False
                for exception in known_exceptions:
                    if line.endswith(exception):
                        name = line[:-len(exception)].strip()
                        destination = exception
                        matched_pairs.append((name, destination))
                        found_match = True
                        break
                if found_match:
                    continue
                if ' ' in line:
                    parts = line.rsplit(' ', 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        destination = parts[1].strip()
                        if len(name) > 1 and len(destination) > 1:
                            matched_pairs.append((name, destination))
    except Exception as e:
        print(f"Errore durante il parsing OCR del PDF: {e}")
        raise e
    return matched_pairs


# --- Logica Principale dell'App ---

DATABASE = 'schedule.db'
app = Flask(__name__)
app.secret_key = 'una-chiave-segreta-a-caso-cambiami'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Rotte Calendario ---
@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        if 'add_item' in request.form:
            waste_type = request.form.get('waste_type')
            day = request.form.get('day')
            time_str = request.form.get('time')
            if waste_type and day and time_str:
                db.execute('INSERT INTO schedules (waste_type, day_of_week, time_of_day) VALUES (?, ?, ?)',
                           (waste_type, day, time_str))
                db.commit()
                flash(f"Aggiunto promemoria per {waste_type}", "success")
            else:
                flash("Tutti i campi sono obbligatori!", "danger")
        elif 'remove_item' in request.form:
            id_to_remove = request.form.get('remove_item')
            db.execute('DELETE FROM schedules WHERE id = ?', (id_to_remove,))
            db.commit()
            flash(f"Promemoria rimosso.", "info")
        return redirect(url_for('index'))
        
    query = """
    SELECT * FROM schedules 
    ORDER BY
        CASE day_of_week
            WHEN 'Lunedì' THEN 1 WHEN 'Martedì' THEN 2 WHEN 'Mercoledì' THEN 3 WHEN 'Giovedì' THEN 4
            WHEN 'Venerdì' THEN 5 WHEN 'Sabato' THEN 6 WHEN 'Domenica' THEN 7
        END, time_of_day """
    schedule_from_db = db.execute(query).fetchall()
    waste_types_from_db = db.execute('SELECT * FROM waste_types ORDER BY name').fetchall()

    return render_template(
        'index.html', 
        waste_types=waste_types_from_db, 
        days_of_week=["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"],
        schedule=schedule_from_db
    )

@app.route('/edit/<int:schedule_id>', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    db = get_db()
    schedule_item = db.execute('SELECT * FROM schedules WHERE id = ?', (schedule_id,)).fetchone()
    if schedule_item is None:
        abort(404)
    if request.method == 'POST':
        waste_type = request.form.get('waste_type')
        day = request.form.get('day')
        time_str = request.form.get('time')
        if not waste_type or not day or not time_str:
            flash('Tutti i campi sono obbligatori.', 'danger')
        else:
            db.execute('UPDATE schedules SET waste_type = ?, day_of_week = ?, time_of_day = ? WHERE id = ?',
                       (waste_type, day, time_str, schedule_id))
            db.commit()
            flash('Promemoria aggiornato con successo!', 'success')
            return redirect(url_for('index'))
    
    waste_types_from_db = db.execute('SELECT * FROM waste_types ORDER BY name').fetchall()
    return render_template(
        'edit_schedule.html',
        schedule_item=schedule_item,
        waste_types=waste_types_from_db,
        days_of_week=["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    )

@app.route('/sync', methods=['POST'])
def sync():
    db = get_db()
    schedule_list = db.execute("""
        SELECT s.*, wt.color_id 
        FROM schedules s 
        JOIN waste_types wt ON s.waste_type = wt.name
    """).fetchall()

    if not schedule_list:
        flash("Nessun promemoria da sincronizzare.", "warning")
        return redirect(url_for('index'))
    try:
        flash("Sincronizzazione in corso...", "info")
        service = google_calendar_manager.authenticate_google_calendar()
        deleted_count = google_calendar_manager.delete_all_waste_events(service)
        flash(f"Cancellati {deleted_count} eventi precedenti dal calendario.", "info")
        for item in schedule_list:
            google_calendar_manager.create_recurring_event(
                service, item['waste_type'], item['day_of_week'], item['time_of_day'], item['color_id']
            )
        flash("Sincronizzazione con Google Calendar completata!", "success")
    except Exception as e:
        print(f"Errore durante la sincronizzazione: {e}")
        flash(f"Si è verificato un errore: {e}", "danger")
    return redirect(url_for('index'))

# --- Rotte Tipi di Rifiuto ---
@app.route('/types')
def types():
    db = get_db()
    waste_types = db.execute('SELECT * FROM waste_types ORDER BY name').fetchall()
    return render_template('types.html', waste_types=waste_types, colors=GOOGLE_CALENDAR_COLORS)

@app.route('/types/add', methods=['POST'])
def types_add():
    name = request.form.get('name')
    color_id = request.form.get('color_id')
    db = get_db()
    try:
        db.execute('INSERT INTO waste_types (name, color_id) VALUES (?, ?)', (name, color_id))
        db.commit()
        flash('Nuovo tipo di rifiuto aggiunto.', 'success')
    except sqlite3.IntegrityError:
        flash(f"Il tipo di rifiuto '{name}' esiste già.", 'danger')
    return redirect(url_for('types'))

@app.route('/types/edit/<int:type_id>', methods=['GET', 'POST'])
def types_edit(type_id):
    db = get_db()
    type_item = db.execute('SELECT * FROM waste_types WHERE id = ?', (type_id,)).fetchone()
    if not type_item:
        abort(404)
    if request.method == 'POST':
        name = request.form.get('name')
        color_id = request.form.get('color_id')
        try:
            old_name = type_item['name']
            if old_name != name:
                db.execute('UPDATE schedules SET waste_type = ? WHERE waste_type = ?', (name, old_name))
            db.execute('UPDATE waste_types SET name = ?, color_id = ? WHERE id = ?', (name, color_id, type_id))
            db.commit()
            flash('Tipo di rifiuto aggiornato.', 'success')
            return redirect(url_for('types'))
        except sqlite3.IntegrityError:
            flash(f"Il tipo di rifiuto '{name}' esiste già.", 'danger')
    return render_template('edit_type.html', type_item=type_item, colors=GOOGLE_CALENDAR_COLORS)

@app.route('/types/delete', methods=['POST'])
def types_delete():
    type_id = request.form.get('id')
    db = get_db()
    type_item = db.execute('SELECT name FROM waste_types WHERE id = ?', (type_id,)).fetchone()
    if type_item:
        db.execute('DELETE FROM schedules WHERE waste_type = ?', (type_item['name'],))
        db.execute('DELETE FROM waste_types WHERE id = ?', (type_id,))
        db.commit()
        flash(f"Tipo '{type_item['name']}' e i suoi promemoria sono stati eliminati.", 'success')
    return redirect(url_for('types'))

# --- Rotte Dizionario Rifiuti ---
@app.route('/dictionary')
def dictionary():
    db = get_db()
    materials_list = db.execute('SELECT * FROM materials ORDER BY name COLLATE NOCASE ASC').fetchall()
    return render_template('dictionary.html', materials=materials_list)

@app.route('/dictionary/add', methods=['POST'])
def dictionary_add():
    name = request.form.get('name')
    destination = request.form.get('destination')
    if not name or not destination:
        flash("Entrambi i campi sono obbligatori!", "danger")
        return redirect(url_for('dictionary'))
    db = get_db()
    try:
        db.execute('INSERT INTO materials (name, destination) VALUES (?, ?)', (name, destination))
        db.commit()
        flash(f"'{name}' aggiunto al dizionario.", "success")
    except sqlite3.IntegrityError:
        flash(f"Il materiale '{name}' esiste già.", "warning")
    return redirect(url_for('dictionary'))

@app.route('/dictionary/delete', methods=['POST'])
def dictionary_delete():
    material_id = request.form.get('id')
    db = get_db()
    db.execute('DELETE FROM materials WHERE id = ?', (material_id,))
    db.commit()
    flash("Voce eliminata.", "info")
    return redirect(url_for('dictionary'))

@app.route('/dictionary/edit/<int:material_id>', methods=['GET', 'POST'])
def dictionary_edit(material_id):
    db = get_db()
    material_item = db.execute('SELECT * FROM materials WHERE id = ?', (material_id,)).fetchone()
    if material_item is None:
        abort(404)
    if request.method == 'POST':
        name = request.form.get('name')
        destination = request.form.get('destination')
        if not name or not destination:
            flash('Tutti i campi sono obbligatori.', 'danger')
        else:
            try:
                db.execute('UPDATE materials SET name = ?, destination = ? WHERE id = ?',
                           (name, destination, material_id))
                db.commit()
                flash('Voce del dizionario aggiornata.', 'success')
                return redirect(url_for('dictionary'))
            except sqlite3.IntegrityError:
                flash(f"Il nome '{name}' esiste già.", 'danger')
    return render_template('edit_material.html', material_item=material_item)

@app.route('/dictionary/upload_pdf', methods=['POST'])
def dictionary_upload_pdf():
    if 'pdf_file' not in request.files:
        flash('Nessun file selezionato.', 'danger')
        return redirect(url_for('dictionary'))
    file = request.files['pdf_file']
    if file.filename == '':
        flash('Nessun file selezionato.', 'danger')
        return redirect(url_for('dictionary'))
    if file and file.filename.lower().endswith('.pdf'):
        try:
            pdf_bytes = file.read()
            parsed_data = parse_pdf_with_ocr(pdf_bytes)
            if not parsed_data:
                flash("L'OCR non ha trovato dati strutturati nel PDF.", "warning")
                return redirect(url_for('dictionary'))
            db = get_db()
            new_items_count = 0
            for name, destination in parsed_data:
                cursor = db.execute('INSERT OR IGNORE INTO materials (name, destination) VALUES (?, ?)',
                                   (name, destination))
                if cursor.rowcount > 0:
                    new_items_count += 1
            db.commit()
            flash(f"Importazione OCR completata! Aggiunte {new_items_count} nuove voci.", "success")
        except Exception as e:
            flash(f"Errore durante l'elaborazione del PDF: {e}", "danger")
    else:
        flash('Formato file non valido. Caricare un .pdf', 'warning')
    return redirect(url_for('dictionary'))

if __name__ == '__main__':
    print("AVVIO IN MODALITA' TEST MANUALE. Per la produzione, usare run.py")
    app.run(host='0.0.0.0', port=5000, debug=True)