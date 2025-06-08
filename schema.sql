-- Benutzerrollen-Tabelle (z. B. Superadmin, Fahrlehrer, Bürokraft, Schüler)
CREATE TABLE rollen (
    id SERIAL PRIMARY KEY,
    bezeichnung VARCHAR(50) NOT NULL UNIQUE
);

-- Benutzer (Login-System) mit Rollenzuordnung
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nutzername VARCHAR(50) NOT NULL UNIQUE,
    passwort_hash TEXT NOT NULL,
    rolle_id INTEGER NOT NULL REFERENCES rollen(id),
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fahrstundenprotokoll für Dokumentation jeder Fahrt
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

-- Beispielhafte Tabelle für Fahrschüler-Stammdaten (optional erweiterbar)
CREATE TABLE schueler (
    id SERIAL PRIMARY KEY,
    vorname VARCHAR(50) NOT NULL,
    nachname VARCHAR(50) NOT NULL,
    geburtsdatum DATE,
    adresse TEXT,
    plz VARCHAR(10),
    ort VARCHAR(100),
    mobilnummer VARCHAR(20),
    sehhilfe BOOLEAN DEFAULT FALSE,
    theorie_bestanden BOOLEAN DEFAULT FALSE,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
