from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabelle: Rollen (Superadmin, Fahrlehrer, Büro, Schüler)
class Rolle(db.Model):
    __tablename__ = 'rollen'
    id = db.Column(db.Integer, primary_key=True)
    bezeichnung = db.Column(db.String(50), unique=True, nullable=False)

# Tabelle: Benutzer mit Rollenzuweisung
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nutzername = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    rolle_id = db.Column(db.Integer, db.ForeignKey('rollen.id'), nullable=False)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

    rolle = db.relationship('Rolle', backref='nutzer')

# Tabelle: Fahrschüler-Stammdaten
class Schueler(db.Model):
    __tablename__ = 'schueler'
    id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(50), nullable=False)
    nachname = db.Column(db.String(50), nullable=False)
    geburtsdatum = db.Column(db.Date)
    adresse = db.Column(db.Text)
    plz = db.Column(db.String(10))
    ort = db.Column(db.String(100))
    mobilnummer = db.Column(db.String(20))
    sehhilfe = db.Column(db.Boolean, default=False)
    theorie_bestanden = db.Column(db.Boolean, default=False)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

# Tabelle: Fahrstundenprotokoll
class Fahrstundenprotokoll(db.Model):
    __tablename__ = 'fahrstundenprotokoll'
    id = db.Column(db.Integer, primary_key=True)
    schueler_id = db.Column(db.Integer, db.ForeignKey('schueler.id'), nullable=False)
    datum = db.Column(db.String(50), nullable=False)
    inhalt = db.Column(db.Text, nullable=False)
    dauer_minuten = db.Column(db.Integer, nullable=False)
    schaltkompetenz = db.Column(db.Boolean, default=False)
    sonderfahrt_typ = db.Column(db.String(50))
    notiz = db.Column(db.Text)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

    schueler = db.relationship('Schueler', backref='protokolle')
