from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import text
import os

# ---------------------- Flask App Setup ----------------------

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# Sichere und kompatible Datenbank-URL vorbereiten
raw_db_url = os.getenv("DATABASE_URL")
if not raw_db_url:
    raise RuntimeError("❌ DATABASE_URL ist nicht gesetzt!")

if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

if "?sslmode=" not in raw_db_url:
    raw_db_url += "?sslmode=require"
app.config["SQLALCHEMY_DATABASE_URI"] = raw_db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ---------------------- Datenbank Setup ----------------------

db = SQLAlchemy(app)

# ---------------------- Datenbankmodelle ----------------------

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
    plz = db.Column(db.String(10))           # NEU
    ort = db.Column(db.String(100))          # NEU
    telefon = db.Column(db.String(30))
    sehhilfe = db.Column(db.String(10))
    klasse = db.Column(db.String(10))        # NEU


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

# ---------------------- Hilfsfunktionen ----------------------

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

# ---------------------- Routen ----------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            nutzername = request.form["nutzername"]
            passwort = request.form["passwort"]

            print(f"[Login-DEBUG] Nutzername erhalten: {nutzername}")
            print("[Login-DEBUG] Starte DB-Abfrage...")
            user = db.session.query(User).filter_by(nutzername=nutzername).first()
            print("[Login-DEBUG] DB-Abfrage abgeschlossen")

            if not user:
                print("[Login-DEBUG] Nutzername nicht gefunden")
                return render_template("login.html", error="❌ Nutzername nicht gefunden")

            print("[Login-DEBUG] Passwort wird geprüft...")
            if not check_password_hash(user.password_hash, passwort):
                print("[Login-DEBUG] Passwort ist falsch")
                return render_template("login.html", error="❌ Passwort ist falsch")

            print("[Login-DEBUG] Login erfolgreich – Session wird gesetzt")
            session["user_id"] = user.id
            session["rolle_id"] = user.rolle_id
            return redirect(url_for("dashboard"))

        except Exception as e:
            print(f"[Login-FEHLER] {e}")
            return "Interner Serverfehler", 500

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user_id=session["user_id"], rolle_id=session["rolle_id"])

@app.route("/profil/<int:schueler_id>")
def profil(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)
    protokolle = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id).all()

    schalt_anzahl = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, schaltkompetenz=True).count()
    schalt_prozent = min(int((schalt_anzahl / 10) * 100), 100)

    sonderfahrten = {typ: Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, sonderfahrt_typ=typ).count() for typ in ["Überland", "Autobahn", "Dämmerung"]}

    bereiche = ["aufbaustufe", "leistungsstufe", "grundfahraufgaben", "reifestufe", "technik"]
    fortschritte = {bereich: get_checked_count(schueler_id, bereich) for bereich in bereiche}

    return re

@app.route("/stammdaten", methods=["GET", "POST"])
def stammdaten():
    if request.method == "POST":
        try:
            schueler = Schueler(
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
            db.session.add(schueler)
            db.session.commit()
            return redirect(url_for("dashboard"))
        except Exception as e:
            print(f"[Stammdaten-FEHLER] {e}")
            return "Fehler beim Speichern", 500

    return render_template("stammdaten.html")

