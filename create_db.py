# create_db.py

from app import app, db

# Falls deine Models separat sind:
# from models import User, ...

with app.app_context():
    db.create_all()
    print("📦 Datenbanktabellen erfolgreich erstellt.")
