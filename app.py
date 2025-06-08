from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Fahrstundenprotokoll, Base
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

# Dummy-Benutzer
users = {
    "admin": generate_password_hash("admin123"),
    "fahrlehrer": generate_password_hash("passwort123")
}

# Datenbankverbindung (PostgreSQL auf Railway)
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session_db = DBSession()

# Startseite
@app.route("/")
def index():
    if 'username' in session:
        return f"✅ Willkommen {session['username']}! <a href='/logout'>Logout</a>"
    return redirect(url_for("login"))

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and check_password_hash(users[username], password):
            session["username"] = username
            return redirect(url_for("index"))
        error = "❌ Ungültige Zugangsdaten!"
    return render_template("login.html", error=error)


# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
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
    
