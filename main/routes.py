from flask import render_template, request, redirect, url_for, session, flash, jsonify
from main import main  # <- Achtung: Kein relativer Import
from models import (
    db,
    Schueler,
    Fahrzeug,
    Fahrstundenprotokoll,
    FahrstundenSlot,
    FahrstundenBuchung,
    Slot
)
from datetime import datetime, date, timedelta
from sqlalchemy import extract

# Globale Altersfunktion
@main.app_template_global()
def berechne_alter(geburtsdatum):
    if not geburtsdatum:
        return "?"
    heute = date.today()
    return heute.year - geburtsdatum.year - ((heute.month, heute.day) < (geburtsdatum.month, geburtsdatum.day))

@main.route("/")
def home():
    return redirect(url_for("main.login"))

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("nutzername") == "admin" and request.form.get("passwort") == "admin":
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

    return render_template("dashboard.html",
        anzahl_schueler=Schueler.query.count(),
        bestandene=Schueler.query.filter_by(theorie_bestanden=True).count(),
        offene_sonderfahrten=Fahrstundenprotokoll.query.filter(Fahrstundenprotokoll.sonderfahrt_typ != None).count(),
        heutige_termine=Fahrstundenprotokoll.query.filter_by(datum=date.today().isoformat()).count(),
        letzte_protokolle=Fahrstundenprotokoll.query.order_by(Fahrstundenprotokoll.datum.desc()).limit(5).all()
    )

@main.route("/create", methods=["GET", "POST"])
def create():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    if request.method == "POST":
        vorname = request.form.get("vorname", "").strip()
        nachname = request.form.get("nachname", "").strip()
        geburtsdatum = request.form.get("geburtsdatum", "").strip()
        plz = request.form.get("plz", "").strip()

        errors = {}
        if not vorname: errors["vorname"] = "Vorname darf nicht leer sein."
        if not nachname: errors["nachname"] = "Nachname darf nicht leer sein."
        try:
            parsed_datum = date.fromisoformat(geburtsdatum)
        except ValueError:
            errors["geburtsdatum"] = "Ungültiges Datum (JJJJ-MM-TT)."
        if not plz.isdigit() or len(plz) != 5:
            errors["plz"] = "PLZ muss 5 Ziffern haben."

        if errors:
            for msg in errors.values(): flash(f"⚠️ {msg}", "warning")
            return render_template("create.html", errors=errors)

        schueler = Schueler(
            vorname=vorname, nachname=nachname, geburtsdatum=parsed_datum,
            adresse=request.form.get("adresse"), plz=plz, ort=request.form.get("ort"),
            mobilnummer=request.form.get("mobilnummer"),
            sehhilfe=request.form.get("sehhilfe") == "true",
            theorie_bestanden=request.form.get("theorie_bestanden") == "true",
            fahrerlaubnisklasse=request.form.get("fahrerlaubnisklasse"),
            geschlecht=request.form.get("geschlecht")
        )
        db.session.add(schueler)
        db.session.commit()
        flash("✅ Neuer Schüler erfolgreich angelegt!", "success")
        return redirect(url_for("main.schueler_profil", schueler_id=schueler.id))

    return render_template("create.html", errors={})

@main.route("/schueler")
def schueler_liste():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    schueler = Schueler.query.order_by(Schueler.nachname.asc()).all()
    return render_template("alle_schueler.html", schueler=[{
        "id": s.id, "geschlecht": s.geschlecht, "alter": berechne_alter(s.geburtsdatum),
        "vorname": s.vorname, "nachname": s.nachname, "klasse": s.fahrerlaubnisklasse
    } for s in schueler])

@main.route("/profil/<int:schueler_id>")
def schueler_profil(schueler_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    s = Schueler.query.get_or_404(schueler_id)
    protokolle = Fahrstundenprotokoll.query.filter_by(schueler_id=s.id).order_by(Fahrstundenprotokoll.datum.desc()).all()
    buchungen = FahrstundenBuchung.query.filter_by(schueler_id=s.id).order_by(FahrstundenBuchung.anfragezeit.desc()).all()
    return render_template("profil.html", schueler=s, protokolle=protokolle, buchungen=buchungen)

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
            slot = FahrstundenSlot(datum=datum, uhrzeit=uhrzeit, fahrzeug_id=fahrzeug_id,
                                   erstellt_von_user_id=session["user_id"], vergeben=False)
            db.session.add(slot)
            db.session.commit()
            flash("✅ Slot hinzugefügt", "success")
        except:
            flash("❗ Fehler beim Speichern", "danger")
        return redirect(url_for("main.slots_verwalten"))

    slots = FahrstundenSlot.query.order_by(FahrstundenSlot.datum, FahrstundenSlot.uhrzeit).all()
    return render_template("slots_verwalten.html", fahrzeuge=fahrzeuge, slots=slots, today=date.today().isoformat())

@main.route("/slots-verwalten/delete/<int:slot_id>", methods=["POST"])
def slot_loeschen(slot_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    db.session.delete(FahrstundenSlot.query.get_or_404(slot_id))
    db.session.commit()
    flash("🗑️ Slot gelöscht", "info")
    return redirect(url_for("main.slots_verwalten"))

@main.route("/api/slots")
def api_slots():
    if "user_id" not in session:
        return jsonify([])
    farben = { "offen": "#10b981", "reserviert": "#f59e0b", "bestätigt": "#ef4444" }
    events = []
    for slot in FahrstundenSlot.query.all():
        start = datetime.combine(slot.datum, slot.uhrzeit)
        end = start + timedelta(minutes=45)
        events.append({
            "id": slot.id,
            "title": f"{slot.fahrzeug.bezeichnung} ({slot.vergeben and 'reserviert' or 'offen'})",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "backgroundColor": farben["reserviert" if slot.vergeben else "offen"],
            "borderColor": "#111827",
            "textColor": "#fff",
            "url": url_for("main.schueler_profil", schueler_id=slot.schueler_id) if slot.schueler_id else None
        })
    return jsonify(events)

@main.route("/slot-buchen/<int:slot_id>")
def slot_buchen(slot_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    slot = FahrstundenSlot.query.get_or_404(slot_id)
    schueler_id = request.args.get("schueler_id", type=int)
    if not schueler_id:
        flash("❗ Kein Schüler angegeben", "danger")
        return redirect(url_for("main.dashboard"))
    # prüfen, ob der Schüler schon 2 Anfragen diese Woche hat
    woche = datetime.now().isocalendar().week
    buchungen = FahrstundenBuchung.query \
        .join(FahrstundenSlot) \
        .filter(FahrstundenBuchung.schueler_id == schueler_id) \
        .filter(extract("week", FahrstundenSlot.datum) == woche).count()
    if buchungen >= 2:
        flash("❌ Nur zwei Buchungen pro Woche erlaubt.", "warning")
        return redirect(url_for("main.schueler_profil", schueler_id=schueler_id))
    slot.vergeben = True
    buchung = FahrstundenBuchung(slot_id=slot.id, schueler_id=schueler_id, status="angefragt")
    db.session.add(buchung)
    db.session.commit()
    flash("📆 Anfrage gespeichert", "success")
    return redirect(url_for("main.schueler_profil", schueler_id=schueler_id))
