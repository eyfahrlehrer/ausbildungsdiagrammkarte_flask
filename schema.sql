-- Benutzerrollen-Tabelle
CREATE TABLE rollen (
    id SERIAL PRIMARY KEY,
    bezeichnung VARCHAR(50) NOT NULL UNIQUE
);

-- Benutzer (Login-System)
CREATE TABLE benutzer (
    id SERIAL PRIMARY KEY,
    nutzername VARCHAR(50) NOT NULL UNIQUE,
    passwort_hash TEXT NOT NULL,
    rolle_id INTEGER NOT NULL REFERENCES rollen(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rolle VARCHAR(20) NOT NULL,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
