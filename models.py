from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Fahrschueler(db.Model):
    __tablename__ = 'fahrschueler'
    
    id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(100), nullable=False)
    nachname = db.Column(db.String(100), nullable=False)
    geburtsdatum = db.Column(db.Date, nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    plz = db.Column(db.String(10), nullable=False)
    ort = db.Column(db.String(100), nullable=False)
    mobilnummer = db.Column(db.String(20), nullable=True)
    sehhilfe = db.Column(db.Boolean, default=False)
    theorie_bestanden = db.Column(db.Boolean, default=False)
    erstellt_am = db.Column(db.Date, default=date.today)

    def __repr__(self):
        return f"<Fahrschueler {self.vorname} {self.nachname}>"
