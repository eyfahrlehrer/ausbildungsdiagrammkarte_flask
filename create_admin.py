from models import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import os

# Datenbankverbindung herstellen
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Bestehenden Admin-Nutzer entfernen (optional)
session.query(User).filter_by(nutzername="admin").delete()

# Neuen Admin-Nutzer anlegen
admin = User(
    nutzername="admin",
    password_hash=generate_password_hash("Test!2024@Admin"),  # sicheres Testpasswort
    rolle_id=1
)

session.add(admin)
session.commit()

print("✅ Neuer Admin wurde angelegt. Login: admin | Passwort: Test!2024@Admin")
