from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Schülerdaten
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
    geschlecht = db.Column(db.String(20))
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

# Fahrzeugdaten
class Fahrzeug(db.Model):
    __tablename__ = 'fahrzeuge'
    id = db.Column(db.Integer, primary_key=True)
    bezeichnung = db.Column(db.String(100), nullable=False)
    typ = db.Column(db.String(50))  # Schalter oder Automatik
    kennzeichen = db.Column(db.String(20))

# Fahrstunden-Protokoll
class Fahrstundenprotokoll(db.Model):
    __tablename__ = 'fahrstundenprotokoll'

    id = db.Column(db.Integer, primary_key=True)
    schueler_id = db.Column(db.Integer, db.ForeignKey('schueler.id'), nullable=False)
    datum = db.Column(db.Date, nullable=False)
    uhrzeit = db.Column(db.Time)
    dauer = db.Column(db.Integer)
    besonderheiten = db.Column(db.String(255))
    sonderfahrt_typ = db.Column(db.String(100))
    fahrzeug_id = db.Column(db.Integer, db.ForeignKey('fahrzeuge.id'))
    zahlungsstatus = db.Column(db.String(20))  # z. B. bar, EC, offen
    preis = db.Column(db.Numeric(6, 2))
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

    schueler = db.relationship('Schueler', backref='protokolle')
    fahrzeug = db.relationship('Fahrzeug', backref='einsatzzeiten')

class FahrstundenSlot(db.Model):
    __tablename__ = 'fahrstunden_slots'

    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.Date, nullable=False)
    uhrzeit = db.Column(db.Time, nullable=False)
    fahrzeug_id = db.Column(db.Integer, db.ForeignKey('fahrzeuge.id'))
    erstellt_von_user_id = db.Column(db.Integer)  # Fahrlehrer, der den Slot erstellt hat
    vergeben = db.Column(db.Boolean, default=False)

    fahrzeug = db.relationship('Fahrzeug', backref='slots')

class FahrstundenBuchung(db.Model):
    __tablename__ = 'fahrstunden_buchungen'

    id = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('fahrstunden_slots.id'), nullable=False)
    schueler_id = db.Column(db.Integer, db.ForeignKey('schueler.id'), nullable=False)
    status = db.Column(db.String(20), default="angefragt")  # angefragt, bestätigt, abgelehnt
    anfragezeit = db.Column(db.DateTime, default=datetime.utcnow)

    slot = db.relationship('FahrstundenSlot', backref='buchungen')
    schueler = db.relationship('Schueler', backref='buchungen')


class Slot(db.Model):
    __tablename__ = 'slots'

    id = db.Column(db.Integer, primary_key=True)
    datum = db.Column(db.Date, nullable=False)
    uhrzeit = db.Column(db.Time, nullable=False)
    fahrzeug_id = db.Column(db.Integer, db.ForeignKey('fahrzeuge.id'), nullable=False)
    status = db.Column(db.String(20), default='offen')  # offen, reserviert, bestätigt
    schueler_id = db.Column(db.Integer, db.ForeignKey('schueler.id'), nullable=True)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

    fahrzeug = db.relationship('Fahrzeug', backref='slots')
    schueler = db.relationship('Schueler', backref='slots')



