from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Fahrschueler(db.Model):
    __tablename__ = 'fahrschueler'

    id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(100), nullable=False)
    nachname = db.Column(db.String(100), nullable=False)
    geburtsdatum = db.Column(db.String(50), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    plz = db.Column(db.String(10), nullable=False)
    ort = db.Column(db.String(100), nullable=False)
    mobilnummer = db.Column(db.String(50), nullable=False)
    sehhilfe = db.Column(db.Boolean, default=False)
    theorie_bestanden = db.Column(db.Boolean, default=False)
    geschlecht = db.Column(db.String(10))

    def __repr__(self):
        return f"<Fahrschueler {self.vorname} {self.nachname}>"

class Fahrstundenprotokoll(db.Model):
    __tablename__ = 'fahrstundenprotokoll'

    id = db.Column(db.Integer, primary_key=True)
    schueler_id = db.Column(db.Integer, db.ForeignKey('fahrschueler.id'), nullable=False)
    datum = db.Column(db.String(50), nullable=False)
    inhalt = db.Column(db.Text, nullable=False)
    dauer_minuten = db.Column(db.Integer, nullable=False)
    schaltkompetenz = db.Column(db.Boolean, default=False)
    sonderfahrt_typ = db.Column(db.String(50))
    notiz = db.Column(db.Text)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    rolle = db.Column(db.String(20), nullable=False)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
