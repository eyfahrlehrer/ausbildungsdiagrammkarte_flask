from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fahrstundenprotokoll, Base

# Flask App starten
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

# Dummy-Benutzer
users = {
    "admin": generate_password_hash("admin123"),
    "fahrlehrer": generate_password_hash("passwort123"),
}

# Datenbankverbindung (PostgreSQL auf Railway)
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session_db = DBSession()

# Login-Seite
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and check_password_hash(users[username], password):
            session["username"] = username
            return redirect(url_for("home"))
        return "❌ Ungültige Zugangsdaten!"
    return '''
        <h2>Login</h2>
        <form method="post">
            <input name="username" placeholder="Benutzername"><br>
            <input name="password" type="password" placeholder="Passwort"><br>
            <button type="submit">Login</button>
        </form>
    '''

# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# Startseite
@app.route("/")
def home():
    if "username" in session:
        return f'✅ Willkommen {session["username"]}! <a href="/logout">Logout</a>'
    return redirect(url_for("login"))

# Protokoll erstellen
@app.route("/protokoll_erstellen/<int:schueler_id>", methods=["GET", "POST"])
def protokoll_erstellen(schueler_id):
    if request.method == "POST":
        datum = request.form["datum"]
        inhalt = request.form["inhalt"]
        dauer = int(request.form["dauer_minuten"])
        schaltkompetenz = "schaltkompetenz" in request.form
        sonderfahrt_typ = request.form.get("sonderfahrt_typ")
        notiz = request.form.get("notiz")
        erstellt_am = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        eintrag = Fahrstundenprotokoll(
            schueler_id=schueler_id,
            datum=datum,
            inhalt=inhalt,
            dauer_minuten=dauer,
            schaltkompetenz=schaltkompetenz,
            sonderfahrt_typ=sonderfahrt_typ,
            notiz=notiz,
            erstellt_am=erstellt_am
        )

        session_db.add(eintrag)
        session_db.commit()

        return redirect(url_for("profil", schueler_id=schueler_id))

    return render_template("protokoll_erstellen.html", schueler_id=schueler_id)

# Profil anzeigen
@app.route("/profil/<int:schueler_id>")
def profil(schueler_id):
    eintraege = session_db.query(Fahrstundenprotokoll)\
        .filter_by(schueler_id=schueler_id)\
        .order_by(Fahrstundenprotokoll.datum.desc())\
        .all()
    return render_template("profil.html", schueler_id=schueler_id, eintraege=eintraege)

# App starten
if __name__ == "__main__":
    app.run(debug=True)
