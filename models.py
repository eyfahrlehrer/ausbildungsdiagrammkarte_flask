from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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
    fahrerlaubnisklasse = db.Column(db.String(10))
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)
