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
        aufbaustufe_prozent=aufbaustufe_prozent
    )

@app.route("/leistungsstufe/<int:schueler_id>", methods=["GET", "POST"])
def leistungsstufe(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)

    result = db.session.execute("SELECT * FROM leistungsstufe WHERE schueler_id = :sid", {"sid": schueler_id}).fetchone()

    if request.method == "POST":
        daten = {feld: feld in request.form for feld in [
            "fahrbahnbenutzung", "einordnen", "markierungen",
            "fahrstreifen_links", "fahrstreifen_rechts", "vorbeifahren",
            "abbiegen_rechts", "abbiegen_links", "abbiegen_mehrspurig",
            "abbiegen_radweg", "abbiegen_sonder", "abbiegen_strassenbahn", "abbiegen_einbahn",
            "vorfahrt", "rechts_vor_links", "verkehrszeichen", "lichtzeichenanlage", "polizeibeamter",
            "geschwindigkeit", "fussgaenger", "kinder", "oepnv", "behinderte", "bus", "schulbus", "radfahrer", "einbahn_rad",
            "verkehrsberuhigt", "schwierige_fuehrung", "engpass", "kreisverkehr", "bahnuebergang",
            "kritische_situationen", "hauptverkehr", "partnerschaft", "schwung", "fussgaengerbereich"
        ]}

        if result:
            # Update
            update_stmt = """
                UPDATE leistungsstufe SET
                {}
                WHERE schueler_id = :sid
            """.format(", ".join([f"{k} = :{k}" for k in daten.keys()]))

            daten["sid"] = schueler_id
            db.session.execute(update_stmt, daten)
        else:
            # Insert
            feldnamen = ", ".join(["schueler_id"] + list(daten.keys()))
            werte_namen = ", ".join([":schueler_id"] + [f":{k}" for k in daten.keys()])
            daten["schueler_id"] = schueler_id

            db.session.execute(f"""
                INSERT INTO leistungsstufe ({feldnamen})
                VALUES ({werte_namen})
            """, daten)

        db.session.commit()
        return redirect(url_for("profil", schueler_id=schueler_id))

    return render_template("leistungsstufe.html", schueler=schueler, eintrag=result)


@app.route("/grundfahraufgaben/<int:schueler_id>", methods=["GET", "POST"])
def grundfahraufgaben(schueler_id):
    schueler = Schueler.query.get_or_404(schueler_id)

    result = db.session.execute("""
        SELECT * FROM grundfahraufgaben WHERE schueler_id = :sid
    """, {"sid": schueler_id}).fetchone()

    if request.method == "POST":
        daten = {
            'rechts_rueckwaerts_ecke': 'rechts_rueckwaerts_ecke' in request.form,
            'umkehren': 'umkehren' in request.form,
            'gefahrbremsung': 'gefahrbremsung' in request.form,
            'rechts_quer_rueck': 'rechts_quer_rueck' in request.form,
            'rechts_laengs_rueck': 'rechts_laengs_rueck' in request.form,
            'rechts_quer_vor': 'rechts_quer_vor' in request.form,
            'rechts_laengs_vor': 'rechts_laengs_vor' in request.form,
        }

        if result:
            db.session.execute("""
                UPDATE grundfahraufgaben SET
                    rechts_rueckwaerts_ecke = :rechts_rueckwaerts_ecke,
                    umkehren = :umkehren,
                    gefahrbremsung = :gefahrbremsung,
                    rechts_quer_rueck = :rechts_quer_rueck,
                    rechts_laengs_rueck = :rechts_laengs_rueck,
                    rechts_quer_vor = :rechts_quer_vor,
                    rechts_laengs_vor = :rechts_laengs_vor
                WHERE schueler_id = :sid
            """, {**daten, "sid": schueler_id})
        else:
            db.session.execute("""
                INSERT INTO grundfahraufgaben (
                    schueler_id, rechts_rueckwaerts_ecke, umkehren, gefahrbremsung,
                    rechts_quer_rueck, rechts_laengs_rueck, rechts_quer_vor, rechts_laengs_vor
                ) VALUES (
                    :sid, :rechts_rueckwaerts_ecke, :umkehren, :gefahrbremsung,
                    :rechts_quer_rueck, :rechts_laengs_rueck, :rechts_quer_vor, :rechts_laengs_vor
                )
            """, {**daten, "sid": schueler_id})

        db.session.commit()
        return redirect(url_for("profil", schueler_id=schueler_id))

    return render_template("grundfahraufgaben.html", schueler=schueler, eintrag=result)

