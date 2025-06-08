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
        else:
            return "Login fehlgeschlagen"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return "Dashboard – Zugang erfolgreich"

@app.route("/profil/<int:schueler_id>")
def profil(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)
    protokolle = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id).all()

    # Fortschrittslogik
    schalt_anzahl = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, schaltkompetenz=True).count()
    schalt_prozent = min(int((schalt_anzahl / 10) * 100), 100)

    ueberland = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, sonderfahrt_typ="Überland").count()
    autobahn = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, sonderfahrt_typ="Autobahn").count()
    daemmerung = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler_id, sonderfahrt_typ="Dämmerung").count()

    return render_template(
        "profil.html",
        schueler=schueler,
        protokolle=protokolle,
        schalt_anzahl=schalt_anzahl,
        schalt_prozent=schalt_prozent,
        ueberland=ueberland,
        autobahn=autobahn,
        daemmerung=daemmerung
    )

@app.route("/protokoll_neu/<int:schueler_id>", methods=["GET", "POST"])
def protokoll_neu(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)

    if request.method == "POST":
        datum = request.form["datum"]
        inhalt = request.form["inhalt"]
        dauer = int(request.form["dauer_minuten"])
        schalt = "schaltkompetenz" in request.form
        sonder = request.form.get("sonderfahrt_typ", "")
        notiz = request.form.get("notiz", "")

        eintrag = Fahrstundenprotokoll(
            schueler_id=schueler.id,
            datum=datum,
            inhalt=inhalt,
            dauer_minuten=dauer,
            schaltkompetenz=schalt,
            sonderfahrt_typ=sonder,
            notiz=notiz,
            erstellt_am=datetime.utcnow()
        )

        db.session.add(eintrag)
        db.session.commit()

        return redirect(url_for("profil", schueler_id=schueler.id))

    return render_template("protokoll_erstellen.html", schueler=schueler)

@app.route("/protokoll_bearbeiten/<int:protokoll_id>", methods=["GET", "POST"])
def protokoll_bearbeiten(protokoll_id):
    eintrag = Fahrstundenprotokoll.query.get_or_404(protokoll_id)
    schueler = Schueler.query.get_or_404(eintrag.schueler_id)

    if request.method == "POST":
        eintrag.datum = request.form["datum"]
        eintrag.inhalt = request.form["inhalt"]
        eintrag.dauer_minuten = int(request.form["dauer_minuten"])
        eintrag.schaltkompetenz = "schaltkompetenz" in request.form
        eintrag.sonderfahrt_typ = request.form.get("sonderfahrt_typ", "")
        eintrag.notiz = request.form.get("notiz", "")

        db.session.commit()
        return redirect(url_for("profil", schueler_id=schueler.id))

    return render_template("protokoll_bearbeiten.html", eintrag=eintrag, schueler=schueler)

@app.route("/protokoll_loeschen/<int:protokoll_id>", methods=["POST"])
def protokoll_loeschen(protokoll_id):
    eintrag = Fahrstundenprotokoll.query.get_or_404(protokoll_id)
    schueler_id = eintrag.schueler_id
    db.session.delete(eintrag)
    db.session.commit()
    return redirect(url_for("profil", schueler_id=schueler_id))

from flask import Flask, render_template, request, redirect, url_for
from models import db, Grundstufe, Schueler
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)

# --- ROUTE: Grundstufe anzeigen + speichern ---
@app.route('/grundstufe/<int:schueler_id>', methods=['GET', 'POST'])
def grundstufe(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)

    try:
        eintrag = Grundstufe.query.filter_by(schueler_id=schueler_id).one()
    except NoResultFound:
        eintrag = None

    if request.method == 'POST':
        daten = {feld: (feld in request.form) for feld in [
            'einsteigen', 'sitz_einstellen', 'spiegel_einstellen', 'lenkrad_einstellen', 'kopfstuetze_einstellen',
            'lenkradhaltung', 'pedale', 'gurt_anlegen', 'schalthebel', 'zuendschloss', 'motor_starten', 'anfahren_anhalt',
            'hoch_1_2', 'hoch_2_3', 'hoch_3_4', 'hoch_4_5', 'hoch_5_6',
            'runter_4_3', 'runter_3_2', 'runter_2_1',
            'ueber_4_2', 'ueber_4_1', 'ueber_3_1']}

        if eintrag:
            for feld, wert in daten.items():
                setattr(eintrag, feld, wert)
        else:
            eintrag = Grundstufe(schueler_id=schueler_id, **daten)
            db.session.add(eintrag)

        db.session.commit()
        return redirect(url_for('profil', schueler_id=schueler_id))

    return render_template('grundstufe.html', schueler=schueler, eintrag=eintrag)


# ---------------------- Hauptausführung ----------------------

if __name__ == "__main__":
    app.run(debug=True)
