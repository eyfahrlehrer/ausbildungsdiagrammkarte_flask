-- Benutzerrollen-Tabelle
CREATE TABLE rollen (
    id SERIAL PRIMARY KEY,
    bezeichnung VARCHAR(50) NOT NULL UNIQUE
);

-- Benutzer (Login-System) – saubere Version mit Rollenbezug
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nutzername VARCHAR(50) NOT NULL UNIQUE,
    passwort_hash TEXT NOT NULL,
    rolle_id INTEGER NOT NULL REFERENCES rollen(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fahrstundenprotokoll
CREATE TABLE fahrstundenprotokoll (
    id SERIAL PRIMARY KEY,
    schueler_id INTEGER NOT NULL,
    datum VARCHAR(50) NOT NULL,
    inhalt TEXT NOT NULL,
    dauer_minuten INTEGER NOT NULL,
    schaltkompetenz BOOLEAN DEFAULT FALSE,
    sonderfahrt_typ VARCHAR(50),
    notiz TEXT,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
