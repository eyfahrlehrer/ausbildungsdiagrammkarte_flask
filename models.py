from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

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
