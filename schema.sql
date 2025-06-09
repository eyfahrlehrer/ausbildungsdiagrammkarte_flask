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

-- Tabelle für die Grundstufe
CREATE TABLE grundstufe (
    id SERIAL PRIMARY KEY,
    schueler_id INTEGER REFERENCES schueler(id),
    einsteigen BOOLEAN,
    sitz_einstellen BOOLEAN,
    spiegel_einstellen BOOLEAN,
    lenkrad_einstellen BOOLEAN,
    kopfstuetze_einstellen BOOLEAN,
    lenkradhaltung BOOLEAN,
    pedale BOOLEAN,
    gurt_anlegen BOOLEAN,
    schalthebel BOOLEAN,
    zuendschloss BOOLEAN,
    motor_starten BOOLEAN,
    anfahren_anhalt BOOLEAN,
    hoch_1_2 BOOLEAN,
    hoch_2_3 BOOLEAN,
    hoch_3_4 BOOLEAN,
    hoch_4_5 BOOLEAN,
    hoch_5_6 BOOLEAN,
    runter_4_3 BOOLEAN,
    runter_3_2 BOOLEAN,
    runter_2_1 BOOLEAN,
    ueber_4_2 BOOLEAN,
    ueber_4_1 BOOLEAN,
    ueber_3_1 BOOLEAN
);

CREATE TABLE aufbaustufe (
    id SERIAL PRIMARY KEY,
    schueler_id INTEGER REFERENCES schueler(id),
    rollen_schalten BOOLEAN,
    abbremsen_schalten BOOLEAN,
    bremsen_degressiv BOOLEAN,
    bremsen_ziel BOOLEAN,
    bremsen_gefahr BOOLEAN,
    gefaelle_anfahren BOOLEAN,
    gefaelle_anhalten BOOLEAN,
    gefaelle_rueckwaerts BOOLEAN,
    gefaelle_sichern BOOLEAN,
    gefaelle_schalten BOOLEAN,
    steig_anfahren BOOLEAN,
    steig_anhalten BOOLEAN,
    steig_rueckwaerts BOOLEAN,
    steig_sichern BOOLEAN,
    steig_schalten BOOLEAN,
    tastgeschwindigkeit BOOLEAN,
    bedienung_kontrolle BOOLEAN,
    oertliche_besonderheiten BOOLEAN,
    erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leistungsstufe (
    id SERIAL PRIMARY KEY,
    schueler_id INTEGER REFERENCES schueler(id),
    fahrbahnbenutzung BOOLEAN,
    einordnen BOOLEAN,
    markierungen BOOLEAN,
    fahrstreifen_links BOOLEAN,
    fahrstreifen_rechts BOOLEAN,
    vorbeifahren BOOLEAN,
    abbiegen_rechts BOOLEAN,
    abbiegen_links BOOLEAN,
    abbiegen_mehrspurig BOOLEAN,
    abbiegen_radweg BOOLEAN,
    abbiegen_sonder BOOLEAN,
    abbiegen_strassenbahn BOOLEAN,
    abbiegen_einbahn BOOLEAN,
    vorfahrt BOOLEAN,
    rechts_vor_links BOOLEAN,
    verkehrszeichen BOOLEAN,
    lichtzeichenanlage BOOLEAN,
    polizeibeamter BOOLEAN,
    geschwindigkeit BOOLEAN,
    fussgaenger BOOLEAN,
    kinder BOOLEAN,
    oepnv BOOLEAN,
    behinderte BOOLEAN,
    bus BOOLEAN,
    schulbus BOOLEAN,
    radfahrer BOOLEAN,
    einbahn_rad BOOLEAN,
    verkehrsberuhigt BOOLEAN,
    schwierige_fuehrung BOOLEAN,
    engpass BOOLEAN,
    kreisverkehr BOOLEAN,
    bahnuebergang BOOLEAN,
    kritische_situationen BOOLEAN,
    hauptverkehr BOOLEAN,
    partnerschaft BOOLEAN,
    schwung BOOLEAN,
    fussgaengerbereich BOOLEAN
);

CREATE TABLE IF NOT EXISTS grundfahraufgaben (
    id SERIAL PRIMARY KEY,
    schueler_id INTEGER REFERENCES schueler(id) ON DELETE CASCADE,
    rechts_rueckwaerts_ecke BOOLEAN DEFAULT FALSE,
    umkehren BOOLEAN DEFAULT FALSE,
    gefahrbremsung BOOLEAN DEFAULT FALSE,
    rechts_quer_rueck BOOLEAN DEFAULT FALSE,
    rechts_laengs_rueck BOOLEAN DEFAULT FALSE,
    rechts_quer_vor BOOLEAN DEFAULT FALSE,
    rechts_laengs_vor BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS ueberlandfahrt (
    id SERIAL PRIMARY KEY,
    schueler_id INTEGER REFERENCES schueler(id) ON DELETE CASCADE,
    
    abstand_vorne BOOLEAN DEFAULT FALSE,
    abstand_hinten BOOLEAN DEFAULT FALSE,
    abstand_seitlich BOOLEAN DEFAULT FALSE,

    beobachtung_spiegel BOOLEAN DEFAULT FALSE,
    verkehrszeichen BOOLEAN DEFAULT FALSE,
    kurven BOOLEAN DEFAULT FALSE,
    steigungen BOOLEAN DEFAULT FALSE,
    gefaelle BOOLEAN DEFAULT FALSE,
    alleen BOOLEAN DEFAULT FALSE,
    ueberholen BOOLEAN DEFAULT FALSE,

    liegenbleiben_absichern BOOLEAN DEFAULT FALSE,
    fussgaenger BOOLEAN DEFAULT FALSE,
    einfahrt_ortschaft BOOLEAN DEFAULT FALSE,
    wildtiere BOOLEAN DEFAULT FALSE,

    leistungsgrenze BOOLEAN DEFAULT FALSE,
    ablenkung BOOLEAN DEFAULT FALSE,
    orientierung BOOLEAN DEFAULT FALSE
);
