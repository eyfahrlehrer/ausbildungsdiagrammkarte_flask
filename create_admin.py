from models import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

admin = session.query(User).filter_by(nutzername="admin").first()
if admin:
    admin.password_hash = generate_password_hash('!4?}g<{MLM1jYKUtp%4!(Q4H"}pi+$3')
    session.commit()
    print("✅ Passwort wurde aktualisiert.")
else:
    print("❌ Kein Admin gefunden.")
