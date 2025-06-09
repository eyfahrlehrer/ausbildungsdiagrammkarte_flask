# create_db.py

from app import app, db, User, Rolle
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    admin_rolle = Rolle.query.filter_by(bezeichnung="Admin").first()
    if not admin_rolle:
        admin_rolle = Rolle(bezeichnung="Admin")
        db.session.add(admin_rolle)
        db.session.commit()

    if not User.query.filter_by(nutzername="admin").first():
        admin_user = User(
            nutzername="admin",
            password_hash=generate_password_hash("1234567"),
            rolle_id=admin_rolle.id
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin wurde angelegt.")
    else:
        print("ℹ️ Admin existiert bereits.")
