from app import db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

nutzername = "admin"
passwort = "!4?}g<{MLM1jYKUtp%4!(Q4H\"}pi+$3"
rolle_id = 1  # ID aus Tabelle "rollen" (z. B. 1 = Superadmin)

# Bestehenden Nutzer mit gleichem Namen löschen (optional)
bestehend = User.query.filter_by(nutzername=nutzername).first()
if bestehend:
    db.session.delete(bestehend)
    db.session.commit()
    print(f"🧹 Alter Nutzer '{nutzername}' wurde entfernt.")

# Neuen User anlegen
neuer_user = User(
    nutzername=nutzername,
    password_hash=generate_password_hash(passwort),
    rolle_id=rolle_id,
    erstellt_am=datetime.utcnow()
)

db.session.add(neuer_user)
db.session.commit()

print(f"✅ Neuer Admin '{nutzername}' wurde erstellt.")
