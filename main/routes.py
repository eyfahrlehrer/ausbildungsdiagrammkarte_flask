from flask import render_template, request, redirect, url_for, session, flash
from . import main
from models import db, Schueler, Fahrstundenprotokoll
from datetime import date, datetime

# Hilfsfunktion zur Altersberechnung
@main.app_template_global()
def berechne_alter(geburtsdatum):
    if not geburtsdatum:
        return "?"
    today = date.today()
    return today.year - geburtsdatum.year - ((today.month, today.day) < (geburtsdatum.month, geburtsdatum.day))

# Startseite leitet zum Login
@main.route("/")
def home():
    return redirect(url_for("main.login"))

# Login
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("nutzername")
        password = request.form.get("passwort")
        if username == "admin" and password == "admin":
            session["user_id"] = 1
            session["rolle_id"] = 1
            return redirect(url_for("main.dashboard"))
        else:
            flash("❌ Ungültige Anmeldedaten", "danger")
    return render_template("login.html")

# Dashboard mit Live-Daten
@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    anzahl_schueler = Schueler.query.count()
    bestandene = Schueler.query.filter_by(theorie_bestanden=True).count()
    offene_sonderfahrten = Fahrstundenprotokoll.query.filter(Fahrstundenprotokoll.sonderfahrt_typ != None).count()
    heutige_termine = Fahrstundenprotokoll.query.filter_by(datum=date.today().isoformat()).count()

    return render_template(
        "dashboard.html",
        anzahl_schueler=anzahl_schueler,
        bestandene=bestandene,
        offene_sonderfahrten=offene_sonderfahrten,
        heutige_termine=heutige_termine
    )

# Neue Schüler anlegen
@main.route("/create", methods=["GET", "POST"])
def create():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    if request.method == "POST":
        neuer_schueler = Schueler(
            vorname=request.form.get("vorname"),
            nachname=request.form.get("nachname"),
            geburtsdatum=request.form.get("geburtsdatum"),
            adresse=request.form.get("adresse"),
            plz=request.form.get("plz"),
            ort=request.form.get("ort"),
            mobilnummer=request.form.get("mobilnummer"),
            sehhilfe=request.form.get("sehhilfe") == "ja",
            theorie_bestanden=request.form.get("theorie_bestanden") == "ja",
            fahrerlaubnisklasse=request.form.get("fahrerlaubnisklasse"),
            geschlecht=request.form.get("geschlecht")
        )
        db.session.add(neuer_schueler)
        db.session.commit()
        return redirect(url_for("main.dashboard"))

    return render_template("create.html")

@main.route("/schueler")
def schueler_liste():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    schueler = Schueler.query.order_by(Schueler.nachname.asc()).all()

    def alter_berechnen(geburtsdatum):
        if not geburtsdatum:
            return "?"
        today = date.today()
        return today.year - geburtsdatum.year - (
            (today.month, today.day) < (geburtsdatum.month, geburtsdatum.day)
        )

    daten = []
    for s in schueler:
        daten.append({
            "id": s.id,
            "geschlecht": s.geschlecht,
            "alter": alter_berechnen(s.geburtsdatum),
            "vorname": s.vorname,
            "nachname": s.nachname,
            "klasse": s.fahrerlaubnisklasse
        })

    return render_template("alle_schueler.html", schueler=daten)


# Alle Schüler auflisten
@main.route("/schueler")
def schueler_liste():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    schueler = Schueler.query.order_by(Schueler.nachname.asc()).all()
    return render_template("alle_schueler.html", schueler=schueler)

# Schülerprofil anzeigen
@main.route("/profil/<int:schueler_id>")
def schueler_profil(schueler_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    schueler = Schueler.query.get_or_404(schueler_id)
    protokolle = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler.id).order_by(Fahrstundenprotokoll.datum.desc()).all()
    return render_template("profil.html", schueler=schueler, protokolle=protokolle)

# Logout
@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))
