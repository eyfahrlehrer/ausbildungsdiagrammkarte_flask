from flask import render_template, request, redirect, url_for, session, flash, jsonify
from . import main
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

@main.route("/kalender")
def kalender():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    return render_template("kalender.html")

@main.route("/api/slots")
def api_slots():
    if "user_id" not in session:
        return jsonify([])

    slots = FahrstundenSlot.query.order_by(FahrstundenSlot.datum, FahrstundenSlot.uhrzeit).all()

    farben = {
        "offen": "#10b981",
        "reserviert": "#f59e0b",
        "bestätigt": "#ef4444"
    }

    events = []
    for slot in slots:
        start = datetime.combine(slot.datum, slot.uhrzeit)
        end = start + timedelta(minutes=45)

        title = f"{slot.fahrzeug.bezeichnung} ({slot.status})"
        if slot.schueler:
            title += f" – {slot.schueler.vorname} {slot.schueler.nachname}"

        events.append({
            "id": slot.id,
            "title": title,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "backgroundColor": farben.get(slot.status, "#9ca3af"),
            "borderColor": "#111827",
            "textColor": "#ffffff",
            "url": url_for("main.schueler_profil", schueler_id=slot.schueler_id) if slot.schueler_id else None
        })

    return jsonify(events)
