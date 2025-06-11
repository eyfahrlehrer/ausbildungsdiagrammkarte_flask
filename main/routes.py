from flask import render_template, request, redirect, url_for, session, flash
from . import main
from models import db, Schueler, Fahrstundenprotokoll, Fahrzeug, Fahrstundenbuchung, FahrstundenSlot
from datetime import datetime, date
from sqlalchemy import extract

# Globale Template-Funktion zur Altersberechnung
@main.app_template_global()
def berechne_alter(geburtsdatum):
    if not geburtsdatum:
        return "?"
    today = date.today()
    return today.year - geburtsdatum.year - ((today.month, today.day) < (geburtsdatum.month, geburtsdatum.day))

@main.route("/")
def home():
    return redirect(url_for("main.login"))

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nutzername = request.form.get("nutzername")
        passwort = request.form.get("passwort")
        if nutzername == "admin" and passwort == "admin":
            session["user_id"] = 1
            session["rolle_id"] = 1
            flash("✅ Willkommen zurück!", "success")
            return redirect(url_for("main.dashboard"))
        flash("❌ Ungültige Anmeldedaten", "danger")
    return render_template("login.html")

@main.route("/logout")
def logout():
    session.clear()
    flash("🚪 Abgemeldet", "info")
    return redirect(url_for("main.login"))

@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    anzahl_schueler = Schueler.query.count()
    bestandene = Schueler.query.filter_by(theorie_bestanden=True).count()
    offene_sonderfahrten = Fahrstundenprotokoll.query.filter(Fahrstundenprotokoll.sonderfahrt_typ != None).count()
    heutige_termine = Fahrstundenprotokoll.query.filter_by(datum=date.today().isoformat()).count()
    letzte_protokolle = Fahrstundenprotokoll.query.order_by(Fahrstundenprotokoll.datum.desc()).limit(5).all()

    return render_template("dashboard.html", 
        anzahl_schueler=anzahl_schueler,
        bestandene=bestandene,
        offene_sonderfahrten=offene_sonderfahrten,
        heutige_termine=heutige_termine,
        letzte_protokolle=letzte_protokolle
    )

@main.route("/create", methods=["GET", "POST"])
def create():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    errors = {}
    if request.method == "POST":
        vorname = request.form.get("vorname", "").strip()
        nachname = request.form.get("nachname", "").strip()
        geburtsdatum = request.form.get("geburtsdatum", "").strip()
        plz = request.form.get("plz", "").strip()

        if not vorname:
            errors["vorname"] = "Vorname darf nicht leer sein."
        if not nachname:
            errors["nachname"] = "Nachname darf nicht leer sein."
        if not geburtsdatum:
            errors["geburtsdatum"] = "Geburtsdatum ist erforderlich."
        else:
            try:
                parsed_datum = date.fromisoformat(geburtsdatum)
            except ValueError:
                errors["geburtsdatum"] = "Ungültiges Datum. Format: JJJJ-MM-TT"
        if not plz.isdigit() or len(plz) != 5:
            errors["plz"] = "PLZ muss genau 5 Ziffern enthalten."

        if errors:
            for msg in errors.values():
                flash(f"⚠️ {msg}", "warning")
            return render_template("create.html", errors=errors)

        neuer_schueler = Schueler(
            vorname=vorname,
            nachname=nachname,
            geburtsdatum=parsed_datum,
            adresse=request.form.get("adresse"),
            plz=plz,
            ort=request.form.get("ort"),
            mobilnummer=request.form.get("mobilnummer"),
            sehhilfe=request.form.get("sehhilfe") == "true",
            theorie_bestanden=request.form.get("theorie_bestanden") == "true",
            fahrerlaubnisklasse=request.form.get("fahrerlaubnisklasse"),
            geschlecht=request.form.get("geschlecht")
        )
        db.session.add(neuer_schueler)
        db.session.commit()
        flash("✅ Neuer Schüler erfolgreich angelegt!", "success")
        return redirect(url_for("main.schueler_profil", schueler_id=neuer_schueler.id))

    return render_template("create.html", errors={})

@main.route("/schueler")
def schueler_liste():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    schueler = Schueler.query.order_by(Schueler.nachname.asc()).all()
    daten = [{
        "id": s.id,
        "geschlecht": s.geschlecht,
        "alter": berechne_alter(s.geburtsdatum),
        "vorname": s.vorname,
        "nachname": s.nachname,
        "klasse": s.fahrerlaubnisklasse
    } for s in schueler]

    return render_template("alle_schueler.html", schueler=daten)

@main.route("/profil/<int:schueler_id>")
def schueler_profil(schueler_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    schueler = Schueler.query.get_or_404(schueler_id)
    protokolle = Fahrstundenprotokoll.query.filter_by(schueler_id=schueler.id).order_by(Fahrstundenprotokoll.datum.desc()).all()
    buchungen = Fahrstundenbuchung.query.filter_by(schueler_id=schueler_id).order_by(Fahrstundenbuchung.datum, Fahrstundenbuchung.uhrzeit).all()
    return render_template("profil.html", schueler=schueler, protokolle=protokolle, buchungen=buchungen)

@main.route("/fahrzeuge", methods=["GET", "POST"])
def fahrzeuge_verwalten():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    bearbeite = None
    edit_id = request.args.get("edit")
    if edit_id:
        bearbeite = Fahrzeug.query.get(edit_id)

    if request.method == "POST":
        fahrzeug_id = request.form.get("fahrzeug_id")
        bezeichnung = request.form.get("bezeichnung")
        typ = request.form.get("typ")
        kennzeichen = request.form.get("kennzeichen")

        if not bezeichnung:
            flash("❗Bezeichnung ist erforderlich.", "warning")
        else:
            if fahrzeug_id:
                fzg = Fahrzeug.query.get(fahrzeug_id)
                if fzg:
                    fzg.bezeichnung = bezeichnung
                    fzg.typ = typ
                    fzg.kennzeichen = kennzeichen
                    flash("✏️ Fahrzeug aktualisiert!", "success")
            else:
                neues_fahrzeug = Fahrzeug(bezeichnung=bezeichnung, typ=typ, kennzeichen=kennzeichen)
                db.session.add(neues_fahrzeug)
                flash("🚗 Neues Fahrzeug hinzugefügt!", "success")
            db.session.commit()
            return redirect(url_for("main.fahrzeuge_verwalten"))

    fahrzeuge = Fahrzeug.query.all()
    return render_template("fahrzeuge.html", fahrzeuge=fahrzeuge, bearbeite=bearbeite)

@main.route("/fahrzeuge/delete/<int:fahrzeug_id>", methods=["POST"])
def fahrzeug_loeschen(fahrzeug_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    fzg = Fahrzeug.query.get_or_404(fahrzeug_id)
    db.session.delete(fzg)
    db.session.commit()
    flash("🗑️ Fahrzeug gelöscht.", "info")
    return redirect(url_for("main.fahrzeuge_verwalten"))

@main.route("/slots-verwalten", methods=["GET", "POST"])
def slots_verwalten():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    fahrzeuge = Fahrzeug.query.all()

    if request.method == "POST":
        try:
            datum = date.fromisoformat(request.form.get("datum"))
            uhrzeit = datetime.strptime(request.form.get("uhrzeit"), "%H:%M").time()
            fahrzeug_id = int(request.form.get("fahrzeug_id"))

            neuer_slot = FahrstundenSlot(
                datum=datum,
                uhrzeit=uhrzeit,
                fahrzeug_id=fahrzeug_id,
                erstellt_von_user_id=session["user_id"],
                vergeben=False
            )
            db.session.add(neuer_slot)
            db.session.commit()
            flash("✅ Neuer Slot angelegt!", "success")
        except Exception as e:
            flash("❗ Fehler beim Erstellen des Slots", "danger")

        return redirect(url_for("main.slots_verwalten"))

    slots = FahrstundenSlot.query.order_by(FahrstundenSlot.datum.asc(), FahrstundenSlot.uhrzeit.asc()).all()
    today = date.today().strftime("%Y-%m-%d")

    return render_template("slots_verwalten.html", slots=slots, fahrzeuge=fahrzeuge, today=today)

@main.route("/slots-verwalten/delete/<int:slot_id>", methods=["POST"])
def slot_loeschen(slot_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    slot = FahrstundenSlot.query.get_or_404(slot_id)
    db.session.delete(slot)
    db.session.commit()
    flash("🗑️ Slot gelöscht.", "info")
    return redirect(url_for("main.slots_verwalten"))
