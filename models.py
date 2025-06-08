from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Fahrschueler(Base):
    __tablename__ = 'fahrschueler'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vorname = Column(String, nullable=False)
    nachname = Column(String, nullable=False)
    geburtsdatum = Column(String, nullable=False)
    adresse = Column(String, nullable=False)
    plz = Column(String, nullable=False)
    ort = Column(String, nullable=False)
    mobilnummer = Column(String, nullable=False)
    sehhilfe = Column(Boolean, default=False)
    theorie_bestanden = Column(Boolean, default=False)
    geschlecht = Column(String, nullable=True)  # Optional: z. B. „männlich“, „weiblich“, „divers“

    def __repr__(self):
        return f"<Fahrschueler {self.vorname} {self.nachname}>"

class Fahrstundenprotokoll(Base):
    __tablename__ = 'fahrstundenprotokoll'

    id = Column(Integer, primary_key=True, autoincrement=True)
    schueler_id = Column(Integer, nullable=False)  # Verknüpft mit Fahrschueler.id
    datum = Column(String, nullable=False)
    inhalt = Column(String, nullable=False)
    dauer_minuten = Column(Integer, nullable=False)
    schaltkompetenz = Column(Boolean, default=False)  # z. B. für B197
    sonderfahrt_typ = Column(String, nullable=True)  # z. B. Überland, Autobahn
    notiz = Column(String, nullable=True)
    erstellt_am = Column(String, nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    rolle = Column(String, nullable=False)  # z. B. 'superadmin', 'fahrlehrer'
    erstellt_am = Column(DateTime, default=datetime.datetime.utcnow)

class Schueler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    vorname = db.Column(db.String(100))
    geburtsdatum = db.Column(db.String(50))
    adresse = db.Column(db.String(200))
    telefon = db.Column(db.String(50))
    sehhilfe = db.Column(db.Boolean)

class Fahrstundenprotokoll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schueler_id = db.Column(db.Integer, db.ForeignKey('schueler.id'))
    datum = db.Column(db.String(50))
    inhalt = db.Column(db.Text)
    dauer_minuten = db.Column(db.Integer)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

