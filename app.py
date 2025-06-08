from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

# Dummy-Datenbank für Benutzer (später ersetzen mit DB)
users = {
    "admin": generate_password_hash("admin123"),
    "fahrlehrer": generate_password_hash("passwort123"),
}

# Startseite
@app.route('/')
def home():
    if "username" in session:
        return f"👋 Willkommen {session['username']}! <a href='/logout'>Logout</a>"
    return redirect(url_for('login'))

# Login-Seite
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('home'))
        return "❌ Ungültige Zugangsdaten!"
    return '''
        <h2>Login</h2>
        <form method="post">
            <input name="username" placeholder="Benutzername"><br>
            <input name="password" type="password" placeholder="Passwort"><br>
            <button type="submit">Login</button>
        </form>
    '''

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Healthcheck für Railway (optional)
@app.route('/healthz')
def healthz():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from models import Fahrstundenprotokoll, Base  # nicht vergessen zu importieren
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DB-Verbindung (Beispiel – anpassen mit deiner echten DB-URL)
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/protokoll_erstellen/<int:schueler_id>", methods=["GET", "POST"])
def protokoll_erstellen(schueler_id):
    if request.method == "POST":
        datum = request.form["datum"]
        inhalt = request.form["inhalt"]
        dauer = int(request.form["dauer_minuten"])
        schaltkompetenz = "schaltkompetenz" in request.form
        sonderfahrt_typ = request.form.get("sonderfahrt_typ")
        notiz = request.form.get("notiz")
        erstellt_am = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        eintrag = Fahrstundenprotokoll(
            schueler_id=schueler_id,
            datum=datum,
            inhalt=inhalt,
            dauer_minuten=dauer,
            schaltkompetenz=schaltkompetenz,
            sonderfahrt_typ=sonderfahrt_typ,
            notiz=notiz,
            erstellt_am=erstellt_am
        )

        session.add(eintrag)
        session.commit()

        return redirect(url_for("profil", schueler_id=schueler_id))  # Profilseite

    return render_template("protokoll_erstellen.html", schueler_id=schueler_id)
