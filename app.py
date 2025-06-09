from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
    passwort_hash = db.Column(db.Text, nullable=False)
    rolle_id = db.Column(db.Integer, db.ForeignKey('rollen.id'), nullable=False)
    erstellt_am = db.Column(db.DateTime, default=datetime.utcnow)

class Schueler(db.Model):
    __tablename__ = "schueler"
    id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(50))
    name = db.Column(db.String(50))
    geburtsdatum = db.Column(db.String(50))
    adresse = db.Column(db.String(100))
    telefon = db.Column(db.String(30))
    sehhilfe = db.Column(db.String(10))

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
    result = db.session.execute(f"SELECT * FROM {table_name} WHERE schueler_id = :sid", {"sid": schueler_id}).fetchone()
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
        user = User.query.filter_by(nutzername=request.form["nutzername"]).first()
        if user and check_password_hash(user.passwort_hash, request.form["passwort"]):
            session["user_id"] = user.id
            session["rolle_id"] = user.rolle_id
            return redirect(url_for("dashboard"))
        return "Login fehlgeschlagen"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return "Dashboard – Zugang erfolgreich"

@app.route("/profil/<int:schueler_id>")
def profil(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)
    protokolle = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id).all()

    schalt_anzahl = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, schaltkompetenz=True).count()
    schalt_prozent = min(int((schalt_anzahl / 10) * 100), 100)

    sonderfahrten = {typ: Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, sonderfahrt_typ=typ).count() for typ in ["Überland", "Autobahn", "Dämmerung"]}

    bereiche = ["aufbaustufe", "leistungsstufe", "grundfahraufgaben", "reifestufe"]
    fortschritte = {bereich: get_checked_count(schueler_id, bereich) for bereich in bereiche}

    return render_template("profil.html", schueler=schueler, protokolle=protokolle,
                           schalt_anzahl=schalt_anzahl, schalt_prozent=schalt_prozent,
                           ueberland=sonderfahrten["Überland"], autobahn=sonderfahrten["Autobahn"],
                           daemmerung=sonderfahrten["Dämmerung"],
                           aufbaustufe_abgeschlossen=fortschritte["aufbaustufe"][0], aufbaustufe_prozent=fortschritte["aufbaustufe"][1],
                           leistungsstufe_abgeschlossen=fortschritte["leistungsstufe"][0], leistungsstufe_prozent=fortschritte["leistungsstufe"][1],
                           grundfahraufgaben_abgeschlossen=fortschritte["grundfahraufgaben"][0], grundfahraufgaben_prozent=fortschritte["grundfahraufgaben"][1],
                           reifestufe_abgeschlossen=fortschritte["reifestufe"][0], reifestufe_prozent=fortschritte["reifestufe"][1])

@app.route("/reifestufe/<int:schueler_id>", methods=["GET", "POST"])
def reifestufe(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)

    result = db.session.execute("""
        SELECT * FROM reifestufe WHERE schueler_id = :sid
    """, {"sid": schueler_id}).fetchone()

    if request.method == "POST":
        daten = {
            "mehrspuriges_abbiegen": "mehrspuriges_abbiegen" in request.form,
            "baustellen": "baustellen" in request.form,
            "verkehrsberuhigte_bereiche": "verkehrsberuhigte_bereiche" in request.form,
            "verkehrsfluss_anpassen": "verkehrsfluss_anpassen" in request.form,
            "starkes_verzoegern": "starkes_verzoegern" in request.form,
            "fremdverhalten_erkennen": "fremdverhalten_erkennen" in request.form,
            "situationsbeurteilung": "situationsbeurteilung" in request.form,
            "selbstkontrolle": "selbstkontrolle" in request.form,
            "notsituationen": "notsituationen" in request.form,
            "situationsgerechtes_handeln": "situationsgerechtes_handeln" in request.form,
            "sozialverhalten": "sozialverhalten" in request.form,
            "rücksichtnahme": "rücksichtnahme" in request.form,
            "situationen_bewerten": "situationen_bewerten" in request.form,
            "sicherheitsabstand": "sicherheitsabstand" in request.form,
            "abschluss": "abschluss" in request.form
        }

        if result:
            db.session.execute("""
                UPDATE reifestufe SET
                {} WHERE schueler_id = :sid
            """.format(", ".join([f"{k} = :{k}" for k in daten.keys()])), {**daten, "sid": schueler_id})
        else:
            db.session.execute("""
                INSERT INTO reifestufe (schueler_id, {}) VALUES (:schueler_id, {})
            """.format(", ".join(daten.keys()), ", ".join([f":{k}" for k in daten.keys()])), {"schueler_id": schueler_id, **daten})

        db.session.commit()
        return redirect(url_for("profil", schueler_id=schueler_id))

    return render_template("reifestufe.html", schueler=schueler, eintrag=result)


@app.route("/technik/<int:schueler_id>", methods=["GET", "POST"])
def technik(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)

    result = db.session.execute("""
        SELECT * FROM technik WHERE schueler_id = :sid
    """, {"sid": schueler_id}).fetchone()

    if request.method == "POST":
        daten = {
            "reifen": "reifen" in request.form,
            "beleuchtung": "beleuchtung" in request.form,
            "bremsanlage": "bremsanlage" in request.form,
            "lenkung": "lenkung" in request.form,
            "flüssigkeiten": "flüssigkeiten" in request.form,
            "kontrollleuchten": "kontrollleuchten" in request.form,
            "hupe": "hupe" in request.form,
            "scheibenwischer": "scheibenwischer" in request.form,
            "warnblinkanlage": "warnblinkanlage" in request.form,
            "motorraum": "motorraum" in request.form,
            "sicherungen": "sicherungen" in request.form,
            "verbandskasten": "verbandskasten" in request.form,
            "warndreieck": "warndreieck" in request.form,
            "warnweste": "warnweste" in request.form,
            "witterung": "witterung" in request.form
        }

        if result:
            db.session.execute("""
                UPDATE technik SET
                {} WHERE schueler_id = :sid
            """.format(", ".join([f"{k} = :{k}" for k in daten.keys()])), {**daten, "sid": schueler_id})
        else:
            db.session.execute("""
                INSERT INTO technik (schueler_id, {}) VALUES (:schueler_id, {})
            """.format(", ".join(daten.keys()), ", ".join([f":{k}" for k in daten.keys()])), {"schueler_id": schueler_id, **daten})

        db.session.commit()
        return redirect(url_for("profil", schueler_id=schueler_id))

    return render_template("technik.html", schueler=schueler, eintrag=result)
