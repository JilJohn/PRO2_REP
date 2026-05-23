# Flask Framework für Web-App
from flask import Flask, render_template, request, redirect, url_for, session
# ORM für Datenbank (SQL)
from flask_sqlalchemy import SQLAlchemy
# Für Datums-/Zeitangaben
from datetime import datetime
# Passwort-Hashing (Sicherheit: keine Klartext-Passwörter speichern)
from bcrypt import hashpw, gensalt, checkpw
# Zugriff auf Betriebssystemfunktionen (z.B. Environment-Variablen)
import os
# Lädt Variablen aus einer .env Datei (z.B. Datenbank-URL, Secret Key)
from dotenv import load_dotenv

# lädt Variablen aus der .env Datei in die Umgebung z.B. SECRET_KEY, Datenbank-URLs, API-Keys
load_dotenv()

# erstellt die Flask-Anwendung (Web-App Instanz)
app = Flask(__name__)

# Konfiguration der Datenbank: hier wird SQLite als lokale Datei-Datenbank verwendet
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tagebuch.db'
# deaktiviert unnötiges Tracking von Änderungen (Performance + Warnungen vermeiden)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Secret Key für Sessions (Login-Cookies, Sicherheit), wird aus Umgebungsvariable geladen, sonst Fallback (nur für Entwicklung!)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
# initialisiert SQLAlchemy mit der Flask-App -> verbindet App mit Datenbank (ORM Layer)
db = SQLAlchemy(app)

# Datenbankmodell für Benutzer (User-Tabelle)
class User(db.Model):
    # eindeutige ID (Primärschlüssel, wird automatisch erhöht)
    id = db.Column(db.Integer, primary_key=True)
    # Benutzername: einzigartig, darf nicht leer sein, max 80 Zeichen
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Passwort: wird als Hash gespeichert, darf nicht leer sein
    password = db.Column(db.LargeBinary, nullable=False)
    # Einträge: Beziehung zu den Tagebucheinträgen des Benutzers
    entries = db.relationship('Entry', backref='user', lazy=True, cascade='all, delete-orphan')

# Datenbankmodell für Tagebucheinträge (Entry-Tabelle)
class Entry(db.Model):
    # eindeutige ID (Primärschlüssel, wird automatisch erhöht)
    id = db.Column(db.Integer, primary_key=True)
    # Fremdschlüssel: verweist auf die ID des Benutzers, dem der Eintrag gehört, darf nicht leer sein
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Titel des Eintrags: darf nicht leer sein, max 200 Zeichen
    title = db.Column(db.String(200), nullable=False)
    # Datum des Eintrags: darf nicht leer sein
    date = db.Column(db.Date, nullable=False)
    # Inhalt des Eintrags: darf nicht leer sein, als Text gespeichert (kann lang sein)
    content = db.Column(db.Text, nullable=False)

# erstellt die Datenbanktabellen basierend auf den definierten Modellen (User, Entry)
with app.app_context():
    db.create_all()
# Hilfsfunktion: aktueller Benutzername aus der Session (Login-Status) abrufen
def get_current_user():
    return session.get("user")

#   Hilfsfunktion: Benutzerobjekt aus der Session abrufen oder zur Login-Seite weiterleiten, wenn nicht eingeloggt
def get_user_or_redirect():
    """Get User object from session or redirect to login."""
    # 1. Aktuellen Benutzernamen aus der Session holen
    username = get_current_user()
    # 2. Wenn kein Benutzername in der Session ist, zur Login-Seite weiterleiten
    if not username:
        return redirect(url_for("login")), None
    # 3. Benutzerobjekt aus der Datenbank anhand des Benutzernamens abrufen
    user_obj = User.query.filter_by(username=username).first()
    # 4. Wenn kein Benutzerobjekt gefunden wird (z.B. Benutzer gelöscht), Session löschen und zur Login-Seite weiterleiten
    if not user_obj:
        session.clear()
        # 5. Zur Login-Seite weiterleiten
        return redirect(url_for("login")), None
    # 6. Wenn alles passt, Benutzerobjekt zurückgeben (kein Redirect nötig)
    return None, user_obj

# Root-Route der Anwendung (/): leitet je nach Login-Status entweder zur Übersicht oder zur Login-Seite weiter
            # FALL 1: User eingeloggt -> gehe zur Übersicht
            # FALL 2: kein User -> gehe zur Login-Seite
@app.route("/")
def start():
    return redirect(url_for("overview" if get_current_user() else "login"))

# Route für die Registrierung neuer Benutzer (/register): zeigt Registrierungsformular an und verarbeitet die Registrierung
@app.route("/register", methods=["GET", "POST"])
def register():
    fehler = ""
    # 1. Wenn die Anfrage eine POST-Anfrage ist (Formular wurde abgeschickt)
    if request.method == "POST":
        # 2. Benutzereingaben aus dem Formular abrufen (username, password) und Whitespace entfernen
        username = request.form.get("username", "").strip()
        # 3. Passwort aus dem Formular abrufen und Whitespace entfernen
        password = request.form.get("password", "").strip()
        # 4. Validierung: Überprüfen, ob alle Felder ausgefüllt sind und ob der Benutzername bereits existiert
        if not username or not password:
            # 5. Fehler: Wenn Felder leer sind, Fehlermeldung setzen
            fehler = "Bitte alle Felder ausfüllen."
            # 6. Fehler: Wenn Benutzername bereits existiert, Fehlermeldung setzen
        elif User.query.filter_by(username=username).first():
            # 7. Fehler: Benutzername ist schon vergeben, Fehlermeldung setzen
            fehler = "Benutzername bereits vergeben."
        else:
            # 8. Wenn alles passt, Benutzer registrieren
            hashed = hashpw(password.encode(), gensalt())
            # 9. Neues Benutzerobjekt erstellen mit Benutzernamen und gehashtem Passwort
            user = User(username=username, password=hashed)
            # 10. Benutzerobjekt zur Datenbank hinzufügen und Änderungen speichern
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
        # 11. Wenn es Fehler gab, Registrierungsseite mit Fehlermeldung neu laden
    return render_template("register.html", fehler=fehler)

@app.route("/login", methods=["GET", "POST"])
def login():
    fehler = ""
    # FALL: Login-Formular wurde abgesendet
    if request.method == "POST":
        # Eingaben aus Formular holen
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        # Benutzer mit diesem Benutzernamen aus der Datenbank holen
        user = User.query.filter_by(username=username).first()
        # Überprüfen, ob Benutzer existiert und ob das eingegebene Passwort zum gespeicherten Passwort-Hash passt
        if user and checkpw(password.encode(), user.password):
            session["user"] = username
            # Login erfolgreich, zur Übersicht weiterleiten
            return redirect(url_for("overview"))
        else:
            fehler = "Falscher Benutzername oder Passwort."
    return render_template("login.html", fehler=fehler)

# Route für Logout: löscht die Session (entfernt Login-Status) und leitet zur Login-Seite weiter
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Route für die Übersicht der Einträge (/overview): zeigt alle Einträge des aktuellen Benutzers an, sortiert nach Datum (neueste zuerst)
@app.route("/overview")
def overview():
    # 1. Überprüfen, ob der Benutzer eingeloggt ist und Benutzerobjekt abrufen, sonst zur Login-Seite weiterleiten
    redirect_response, user_obj = get_user_or_redirect()
    # 2. Wenn get_user_or_redirect eine Weiterleitung zurückgibt (weil kein Benutzer eingeloggt ist), diese Weiterleitung ausführen
    if redirect_response:
        # 3. Wenn Benutzerobjekt erfolgreich abgerufen wurde, Einträge dieses Benutzers aus der Datenbank holen, sortieren und an die Übersichtsvorlage übergeben
        return redirect_response
    # 4. Einträge des aktuellen Benutzers abrufen, sortiert nach ID in absteigender Reihenfolge (neueste Einträge zuerst)   
    entries = Entry.query.filter_by(user_id=user_obj.id).order_by(Entry.id.desc()).all()
    return render_template("overview.html", entries=entries)

@app.route("/new", methods=["GET", "POST"])
def new_entry():
    #   1. Überprüfen, ob der Benutzer eingeloggt ist und Benutzerobjekt abrufen, sonst zur Login-Seite weiterleiten
    redirect_response, user_obj = get_user_or_redirect()
    if redirect_response:
        return redirect_response
    
    #   2. Wenn die Anfrage eine POST-Anfrage ist (Formular wurde abgeschickt), Eingaben aus dem Formular abrufen, validieren und neuen Eintrag erstellen
    if request.method == "POST":
        # 3. Benutzereingaben aus dem Formular abrufen (title, date, content) und Whitespace entfernen
        title = request.form.get("title", "").strip()
        date_str = request.form.get("date", "")
        content = request.form.get("content", "").strip()
        
        #   4. Validierung: Überprüfen, ob alle Felder ausgefüllt sind (Titel, Datum, Inhalt)
        if not all([title, date_str, content]):
            #  5. Fehler: Wenn Felder leer sind, Formular mit Fehlermeldung neu laden
            return render_template("new_entry.html", today=datetime.now().strftime("%Y-%m-%d"))
        #   6. Wenn alles passt, neuen Eintrag erstellen und zur Übersicht weiterleiten
        try:
            #   Datum aus String in Date-Objekt umwandeln (Format: YYYY-MM-DD)
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            #   Neues Eintragsobjekt erstellen mit Titel, Datum, Inhalt und Verknüpfung zum aktuellen Benutzer
            entry = Entry(user_id=user_obj.id, title=title, date=date, content=content)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("overview"))
        #   7. Fehler: Wenn Datum nicht im richtigen Format ist, Formular mit Fehlermeldung neu laden
        except ValueError:
            return render_template("new_entry.html", today=datetime.now().strftime("%Y-%m-%d"))
    #   8. Wenn es eine GET-Anfrage ist (Formular soll angezeigt werden), einfach die Vorlage für den neuen Eintrag rendern, dabei das heutige Datum als Standardwert übergeben
    return render_template("new_entry.html", today=datetime.now().strftime("%Y-%m-%d"))

#   Route für die Detailansicht eines Eintrags (/entry/<entry_id>): zeigt die Details eines einzelnen Eintrags an, wenn er zum aktuellen Benutzer gehört, sonst Weiterleitung zur Übersicht
@app.route("/entry/<int:entry_id>")
#   1. Überprüfen, ob der Benutzer eingeloggt ist und Benutzerobjekt abrufen, sonst zur Login-Seite weiterleiten
def entry_detail(entry_id):
    redirect_response, user_obj = get_user_or_redirect()
    if redirect_response:
        return redirect_response
    
    #   2. Eintrag mit der angegebenen ID abrufen, aber nur, wenn er zum aktuellen Benutzer gehört
    entry = Entry.query.filter_by(id=entry_id, user_id=user_obj.id).first()
    #   3. Wenn kein Eintrag gefunden wird (z.B. falsche ID oder Eintrag gehört nicht zum Benutzer), zur Übersicht weiterleiten
    if not entry:
        return redirect(url_for("overview"))
    return render_template("entry_detail.html", entry=entry)

#   Route für die Bearbeitung eines Eintrags (/edit/<entry_id>): ermöglicht das Bearbeiten eines Eintrags, wenn er zum aktuellen Benutzer gehört, sonst Weiterleitung zur Übersicht
@app.route("/edit/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    #   1. Überprüfen, ob der Benutzer eingeloggt ist und Benutzerobjekt abrufen, sonst zur Login-Seite weiterleiten
    redirect_response, user_obj = get_user_or_redirect()
    if redirect_response:
        return redirect_response
    
    #   2. Eintrag mit der angegebenen ID abrufen, aber nur, wenn er zum aktuellen Benutzer gehört
    entry = Entry.query.filter_by(id=entry_id, user_id=user_obj.id).first()
    if not entry:
        return redirect(url_for("overview"))
    
    #   3. Wenn die Anfrage eine POST-Anfrage ist (Formular wurde abgeschickt), Eingaben aus dem Formular abrufen, validieren und Eintrag aktualisieren
    if request.method == "POST":
        #   4. Benutzereingaben aus dem Formular abrufen (title, date, content) und Whitespace entfernen
        title = request.form.get("title", "").strip()
        date_str = request.form.get("date", "")
        content = request.form.get("content", "").strip()
        
        #   5. Validierung: Überprüfen, ob alle Felder ausgefüllt sind (Titel, Datum, Inhalt)
        if not all([title, date_str, content]):
            return render_template("edit_entry.html", entry=entry)
        
        #   6. Wenn alles passt, Eintrag aktualisieren und zur Detailansicht weiterleiten
        try:
            #   Datum aus String in Date-Objekt umwandel (Format: YYYY-MM-DD)
            entry.title = title
            entry.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            entry.content = content
            db.session.commit()
            return redirect(url_for("entry_detail", entry_id=entry.id))
        except ValueError:
            return render_template("edit_entry.html", entry=entry)
    
    return render_template("edit_entry.html", entry=entry)

#   Route für die Löschung eines Eintrags (/delete/<entry_id>): ermöglicht das Löschen eines Eintrags, wenn er zum aktuellen Benutzer gehört, sonst Weiterleitung zur Übersicht
@app.route("/delete/<int:entry_id>", methods=["POST"])
#   1. Überprüfen, ob der Benutzer eingeloggt ist und Benutzerobjekt abrufen, sonst zur Login-Seite weiterleiten
def delete_entry(entry_id):
    #   2. Eintrag mit der angegebenen ID abrufen, aber nur, wenn er zum aktuellen Benutzer gehört
    redirect_response, user_obj = get_user_or_redirect()
    if redirect_response:
        return redirect_response
    #   3. Wenn Eintrag gefunden wird, diesen Eintrag aus der Datenbank löschen und Änderungen speichern, danach zur Übersicht weiterleiten
    entry = Entry.query.filter_by(id=entry_id, user_id=user_obj.id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return redirect(url_for("overview"))

@app.route("/dashboard")
def dashboard():
    #   1. Überprüfen, ob der Benutzer eingeloggt ist und Benutzerobjekt abrufen, sonst zur Login-Seite weiterleiten
    redirect_response, user_obj = get_user_or_redirect()
    if redirect_response:
        return redirect_response
    #   2. Alle Einträge des aktuellen Benutzers abrufen
    entries = Entry.query.filter_by(user_id=user_obj.id).all()
    #   3. Gesamtanzahl der Einträge berechnen
    total = len(entries)
    
    #   4. Anzahl der Einträge pro Monat berechnen (z.B. {"Januar 2024": 3, "Februar 2024": 5})
    months = {}
    #   5. Für jeden Eintrag das Monat-Jahr-Format aus dem Datum extrahieren und die Anzahl der Einträge pro Monat hochzählen
    for entry in entries:
        #   Monat und Jahr aus dem Datum des Eintrags extrahieren (z.B. "Januar 2024")
        month = entry.date.strftime("%B %Y")
        #   6. Anzahl der Einträge für dieses Monat-Jahr in einem Dictionary hochzählen
        months[month] = months.get(month, 0) + 1
    
    #   7. Durchschnittliche Anzahl der Einträge pro Monat 
    active_months = len(months)
    #   8. Durchschnitt berechnen: Gesamtanzahl der Einträge 
    avg_per_month = round(total / active_months, 1) if active_months > 0 else 0
    
    return render_template("dashboard.html", total=total, active_months=active_months, avg_per_month=avg_per_month, months=months)

#   Hauptfunktion: startet die Flask-Anwendung
if __name__ == "__main__":
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug, port=5002)