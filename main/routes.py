from flask import render_template, request, redirect, url_for, session, flash
from . import main
from models import db, Schueler

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
            fahrerlaubnisklasse=request.form.get("fahrerlaubnisklasse")
        )
        db.session.add(neuer_schueler)
        db.session.commit()
        return redirect(url_for("main.dashboard"))

    return render_template("create.html")

@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("main.login"))

    # Live-Daten laden
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
