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
