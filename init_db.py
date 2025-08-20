# init_db.py

import sqlite3

connection = sqlite3.connect('schedule.db')

# Schema aggiornato con la nuova tabella 'waste_types'
schema_sql = """
DROP TABLE IF EXISTS schedules;
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waste_type TEXT NOT NULL,
    day_of_week TEXT NOT NULL,
    time_of_day TEXT NOT NULL
);

DROP TABLE IF EXISTS materials;
CREATE TABLE materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    destination TEXT NOT NULL
);

-- NUOVA TABELLA PER I TIPI DI RIFIUTO --
DROP TABLE IF EXISTS waste_types;
CREATE TABLE waste_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color_id TEXT NOT NULL DEFAULT '1'
);
"""

connection.executescript(schema_sql)

# Inseriamo i dati di esempio nel dizionario (invariato)
print("Inserimento dati di esempio nel dizionario...")
cursor = connection.cursor()
sample_materials = [
    ('Accendino', 'Indifferenziato'), ('Bottiglia di plastica', 'Plastica e Lattine'),
    ('Bottiglia di vetro', 'Vetro'), ('Cartone della pizza (pulito)', 'Carta e Cartone'),
    ('Cartone della pizza (sporco)', 'Organico'), ('Fazzoletto di carta usato', 'Organico'),
    ('Lattina di alluminio', 'Plastica e Lattine'), ('Scontrino fiscale', 'Indifferenziato')
]
cursor.executemany('INSERT INTO materials (name, destination) VALUES (?, ?)', sample_materials)

# Inseriamo i tipi di rifiuto di default nella nuova tabella
print("Inserimento tipi di rifiuto di default...")
default_waste_types = [
    ('Organico', '2'), # Verde Salvia
    ('Plastica e Lattine', '11'), # Rosso Pomodoro
    ('Carta e Cartone', '5'), # Giallo Banana
    ('Vetro', '8'), # Grigio Grafite
    ('Indifferenziato', '1') # Blu Mirtillo
]
cursor.executemany('INSERT INTO waste_types (name, color_id) VALUES (?, ?)', default_waste_types)

connection.commit()
connection.close()

print("Database 'schedule.db' inizializzato con la tabella 'waste_types'.")