from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from sqlalchemy.orm.exc import NoResultFound

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

def get_anzahl_aufbaustufe_checked(schueler_id):
    result = db.session.execute("""
        SELECT * FROM aufbaustufe WHERE schueler_id = :sid
    """, {"sid": schueler_id}).fetchone()

    if result:
        werte = dict(result)
        anzahl = sum(1 for key, value in werte.items() if key not in ('id', 'schueler_id') and value)
        gesamt = len(werte) - 2
        prozent = int((anzahl / gesamt) * 100)
        return anzahl, prozent
    return 0, 0

def get_anzahl_grundfahraufgaben_checked(schueler_id):
    result = db.session.execute("""
        SELECT * FROM grundfahraufgaben WHERE schueler_id = :sid
    """, {"sid": schueler_id}).fetchone()

    if result:
        werte = dict(result)
        anzahl = sum(1 for key, value in werte.items() if key not in ('id', 'schueler_id') and value)
        gesamt = len(werte) - 2
        prozent = int((anzahl / gesamt) * 100)
        return anzahl, prozent
    return 0, 0

# ---------------------- Routen ----------------------

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nutzername = request.form["nutzername"]
        passwort = request.form["passwort"]
        benutzer = User.query.filter_by(nutzername=nutzername).first()
        if benutzer and check_password_hash(benutzer.passwort_hash, passwort):
            session["user_id"] = benutzer.id
            session["rolle_id"] = benutzer.rolle_id
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

    ueberland = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, sonderfahrt_typ="Überland").count()
    autobahn = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, sonderfahrt_typ="Autobahn").count()
    daemmerung = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, sonderfahrt_typ="Dämmerung").count()

    aufbaustufe_abgeschlossen, aufbaustufe_prozent = get_anzahl_aufbaustufe_checked(schueler_id)
    grundfahraufgaben_abgeschlossen, grundfahraufgaben_prozent = get_anzahl_grundfahraufgaben_checked(schueler_id)

    return render_template(
        "profil.html",
        schueler=schueler,
        protokolle=protokolle,
        schalt_anzahl=schalt_anzahl,
        schalt_prozent=schalt_prozent,
        ueberland=ueberland,
        autobahn=autobahn,
        daemmerung=daemmerung,
        aufbaustufe_abgeschlossen=aufbaustufe_abgeschlossen,
        aufbaustufe_prozent=aufbaustufe_prozent,
        grundfahraufgaben_abgeschlossen=grundfahraufgaben_abgeschlossen,
        grundfahraufgaben_prozent=grundfahraufgaben_prozent
    )

@app.route("/ueberlandfahrt/<int:schueler_id>", methods=["GET", "POST"])
def ueberlandfahrt(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)

    result = db.session.execute("""
        SELECT * FROM ueberlandfahrt WHERE schueler_id = :sid
    """, {"sid": schueler_id}).fetchone()

    if request.method == "POST":
        daten = {
            "abstand_vorne": "abstand_vorne" in request.form,
            "abstand_hinten": "abstand_hinten" in request.form,
            "abstand_seitlich": "abstand_seitlich" in request.form,
            "beobachtung_spiegel": "beobachtung_spiegel" in request.form,
            "verkehrszeichen": "verkehrszeichen" in request.form,
            "kurven": "kurven" in request.form,
            "steigungen": "steigungen" in request.form,
            "gefaelle": "gefaelle" in request.form,
            "alleen": "alleen" in request.form,
            "ueberholen": "ueberholen" in request.form,
            "liegenbleiben_absichern": "liegenbleiben_absichern" in request.form,
            "fussgaenger": "fussgaenger" in request.form,
            "einfahren_ortschaft": "einfahren_ortschaft" in request.form,
            "wildtiere": "wildtiere" in request.form,
            "leistungsgrenze": "leistungsgrenze" in request.form,
            "ablenkung": "ablenkung" in request.form,
            "orientierung": "orientierung" in request.form
        }

        if result:
            update_stmt = """
                UPDATE ueberlandfahrt SET
                {}
                WHERE schueler_id = :sid
            """.format(", ".join([f"{k} = :{k}" for k in daten.keys()]))
            daten["sid"] = schueler_id
            db.session.execute(update_stmt, daten)
        else:
            feldnamen = ", ".join(["schueler_id"] + list(daten.keys()))
            werte_namen = ", ".join([":schueler_id"] + [f":{k}" for k in daten.keys()])
            daten["schueler_id"] = schueler_id
            db.session.execute(f"""
                INSERT INTO ueberlandfahrt ({feldnamen})
                VALUES ({werte_namen})
            """, daten)

        db.session.commit()
        return redirect(url_for("profil", schueler_id=schueler_id))

    return render_template("ueberlandfahrt.html", schueler=schueler, eintrag=result)

@app.route("/autobahnfahrt/<int:schueler_id>", methods=["GET", "POST"])
def autobahnfahrt(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)

    result = db.session.execute("""
        SELECT * FROM autobahnfahrt WHERE schueler_id = :sid
    """, {"sid": schueler_id}).fetchone()

    if request.method == "POST":
        daten = {
            "fahrtplanung": "fahrtplanung" in request.form,
            "einfahren_bab": "einfahren_bab" in request.form,
            "fahrstreifenwechsel": "fahrstreifenwechsel" in request.form,
            "geschwindigkeit": "geschwindigkeit" in request.form,
            "abstand_vorne": "abstand_vorne" in request.form,
            "abstand_hinten": "abstand_hinten" in request.form,
            "abstand_seitlich": "abstand_seitlich" in request.form,
            "ueberholen": "ueberholen" in request.form,
            "schilder_markierungen": "schilder_markierungen" in request.form,
            "vorbeifahren_anschlussstellen": "vorbeifahren_anschlussstellen" in request.form,
            "rastplaetze": "rastplaetze" in request.form,
            "verhalten_unfaelle": "verhalten_unfaelle" in request.form,
            "dichter_verkehr": "dichter_verkehr" in request.form,
            "besondere_situationen": "besondere_situationen" in request.form,
            "leistungsgrenze": "leistungsgrenze" in request.form,
            "ablenkung": "ablenkung" in request.form,
            "konfliktsituation": "konfliktsituation" in request.form,
            "verlassen_bab": "verlassen_bab" in request.form
        }

        if result:
            update_stmt = """
                UPDATE autobahnfahrt SET
                {}
                WHERE schueler_id = :sid
            """.format(", ".join([f"{k} = :{k}" for k in daten.keys()]))
            daten["sid"] = schueler_id
            db.session.execute(update_stmt, daten)
        else:
            feldnamen = ", ".join(["schueler_id"] + list(daten.keys()))
            werte_namen = ", ".join([":schueler_id"] + [f":{k}" for k in daten.keys()])
            daten["schueler_id"] = schueler_id
            db.session.execute(f"""
                INSERT INTO autobahnfahrt ({feldnamen})
                VALUES ({werte_namen})
            """, daten)

        db.session.commit()
        return redirect(url_for("profil", schueler_id=schueler_id))

    return render_template("autobahnfahrt.html", schueler=schueler, eintrag=result)

@app.route("/daemmerungfahrt/<int:schueler_id>", methods=["GET", "POST"])
def daemmerungfahrt(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)

    result = db.session.execute("""
        SELECT * FROM daemmerungfahrt WHERE schueler_id = :sid
    """, {"sid": schueler_id}).fetchone()

    if request.method == "POST":
        daten = {
            "beleuchtung": "beleuchtung" in request.form,
            "kontrolle": "kontrolle" in request.form,
            "benutzung": "benutzung" in request.form,
            "einstellen": "einstellen" in request.form,
            "fernlicht": "fernlicht" in request.form,
            "beleuchtete_strassen": "beleuchtete_strassen" in request.form,
            "unbeleuchtete_strassen": "unbeleuchtete_strassen" in request.form,
            "parken": "parken" in request.form,
            "schlechte_witterung": "schlechte_witterung" in request.form,
            "bahnuebergaenge": "bahnuebergaenge" in request.form,
            "tiere": "tiere" in request.form,
            "unbeleuchtete_verkehrsteilnehmer": "unbeleuchtete_verkehrsteilnehmer" in request.form,
            "blendung": "blendung" in request.form,
            "orientierung": "orientierung" in request.form,
            "abschlussbesprechung": "abschlussbesprechung" in request.form
        }

        if result:
            update_stmt = """
                UPDATE daemmerungfahrt SET
                {}
                WHERE schueler_id = :sid
            """.format(", ".join([f"{k} = :{k}" for k in daten.keys()]))
            daten["sid"] = schueler_id
            db.session.execute(update_stmt, daten)
        else:
            feldnamen = ", ".join(["schueler_id"] + list(daten.keys()))
            werte_namen = ", ".join([":schueler_id"] + [f":{k}" for k in daten.keys()])
            daten["schueler_id"] = schueler_id
            db.session.execu
