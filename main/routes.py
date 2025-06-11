from flask import render_template, request, redirect, url_for, session, flash
from . import main
from models import db, Schueler, Fahrstundenprotokoll, Fahrzeug, Fahrstundenbuchung, Slot
from datetime import datetime, date
from sqlalchemy import extract

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

@main.route("/slots-buchen/<int:schueler_id>", methods=["GET", "POST"])
def slots_buchen(schueler_id):
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    schueler = Schueler.query.get_or_404(schueler_id)
    aktuelle_woche = datetime.now().isocalendar().week
    buchungen_diese_woche = Fahrstundenbuchung.query.filter_by(schueler_id=schueler_id).filter(
        extract("week", Fahrstundenbuchung.datum) == aktuelle_woche
    ).count()

    heute = date.today()
    jetzt = datetime.now().time()
    slots = Slot.query.filter(
        (Slot.datum > heute) |
        ((Slot.datum == heute) & (Slot.uhrzeit > jetzt))
    ).filter_by(vergeben=False).order_by(Slot.datum, Slot.uhrzeit).all()

    return render_template("slots_buchen.html", schueler=schueler, slots=slots, buchungen_diese_woche=buchungen_diese_woche)

@main.route("/fahrstunde-buchen", methods=["POST"])
def fahrstunde_buchen():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    slot_id = request.form.get("slot_id")
    schueler_id = request.form.get("schueler_id")

    slot = Slot.query.get_or_404(slot_id)
    aktuelle_woche = datetime.now().isocalendar().week
    buchungen_diese_woche = Fahrstundenbuchung.query.filter_by(schueler_id=schueler_id).filter(
        extract("week", Fahrstundenbuchung.datum) == aktuelle_woche
    ).count()

    if buchungen_diese_woche >= 2:
        flash("❌ Du hast bereits 2 Fahrstunden für diese Woche gebucht.", "danger")
        return redirect(url_for("main.slots_buchen", schueler_id=schueler_id))

    neue_buchung = Fahrstundenbuchung(
        schueler_id=schueler_id,
        fahrzeug_id=slot.fahrzeug_id,
        datum=slot.datum,
        uhrzeit=slot.uhrzeit,
        status="pending",
        angefragt_am=datetime.now()
    )
    slot.vergeben = True

    db.session.add(neue_buchung)
    db.session.commit()

    flash("✅ Slot gebucht – Bestätigung durch Fahrlehrer ausstehend.", "success")
    return redirect(url_for("main.schueler_profil", schueler_id=schueler_id))
