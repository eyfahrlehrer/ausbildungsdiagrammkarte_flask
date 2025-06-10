from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# Datenbank-URL vorbereiten
raw_db_url = os.getenv("DATABASE_URL")
if not raw_db_url:
    raise RuntimeError("❌ DATABASE_URL ist nicht gesetzt!")

if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

if "?sslmode=" not in raw_db_url:
    raw_db_url += "?sslmode=require"

app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Datenbankmodelle
class Rolle(db.Model):
    __tablename__ = "rollen"
    id = db.Column(db.Integer, primary_key=True)
    bezeichnung = db.Column(db.String(50), unique=True, nullable=False)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    nutzername = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    rolle_id = db.Column(db.Integer, db.ForeignKey('rollen.id'), nullable=False)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

class Schueler(db.Model):
    __tablename__ = "schueler"
    id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(50))
    name = db.Column(db.String(50))
    geburtsdatum = db.Column(db.String(50))
    adresse = db.Column(db.String(100))
    plz = db.Column(db.String(10))
    ort = db.Column(db.String(50))
    telefon = db.Column(db.String(30))
    sehhilfe = db.Column(db.String(10))
    klasse = db.Column(db.String(10))

class Fahrstundenprotokoll(db.Model):
    __tablename__ = "fahrstundenprotokoll"
    id = db.Column(db.Integer, primary_key=True)
    schueler_id = db.Column(db.Integer, db.ForeignKey("schueler.id"), nullable=False)
    datum = db.Column(db.String(50), nullable=False)
    inhalt = db.Column(db.Text, nullable=False)
    dauer_minuten = db.Column(db.Integer, nullable=False)
    schaltkompetenz = db.Column(db.Boolean, default=False)
    sonderfahrt_typ = db.Column(db.String(50))
    notiz = db.Column(db.Text)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

# Fortschrittszähler
def get_checked_count(schueler_id, table_name):
    result = db.session.execute(
        f"SELECT * FROM {table_name} WHERE schueler_id = :sid", {"sid": schueler_id}
    ).fetchone()
    if result:
        werte = dict(result)
        anzahl = sum(1 for k, v in werte.items() if k not in ('id', 'schueler_id') and v)
        gesamt = len(werte) - 2
        return anzahl, int((anzahl / gesamt) * 100)
    return 0, 0

# Startseite
@app.route("/")
def home():
    return redirect(url_for("login"))

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nutzername = request.form["nutzername"]
        passwort = request.form["passwort"]

        user = db.session.query(User).filter_by(nutzername=nutzername).first()
        if not user:
            return render_template("login.html", error="❌ Nutzername nicht gefunden")

        if not check_password_hash(user.password_hash, passwort):
            return render_template("login.html", error="❌ Passwort ist falsch")

        session["user_id"] = user.id
        session["rolle_id"] = user.rolle_id
        return redirect(url_for("dashboard"))

    return render_template("login.html")

# Dashboard
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# Stammdaten-Formular
@app.route("/stammdaten", methods=["GET", "POST"])
def stammdaten():
    if request.method == "POST":
        neuer_schueler = Schueler(
            vorname=request.form["vorname"],
            name=request.form["name"],
            geburtsdatum=request.form["geburtsdatum"],
            adresse=request.form["adresse"],
            plz=request.form["plz"],
            ort=request.form["ort"],
            telefon=request.form["telefon"],
            sehhilfe=request.form["sehhilfe"],
            klasse=request.form["klasse"]
        )
        db.session.add(neuer_schueler)
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("stammdaten.html")

@app.route("/create")
def create_redirect():
    return redirect(url_for("stammdaten"))


# /create als Alias für /stammdaten
@app.route("/create", methods=["GET", "POST"])
def create():
    return stammdaten()

# Alle Schüler anzeigen
@app.route("/alle_schueler")
def alle_schueler():
    schueler_liste = Schueler.query.all()
    return render_template("alle_schueler.html", schueler=schueler_liste)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# App starten
if __name__ == "__main__":
    app.run(debug=True)
