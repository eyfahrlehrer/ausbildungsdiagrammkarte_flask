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
        return redirect(url_for("main.login"))  # Wenn nicht eingeloggt → Login-Seite
    return render_template("dashboard.html")     # Wenn eingeloggt → Dashboard zeigen

@main.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("main.login"))
    return render_template("dashboard.html")
