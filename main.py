from flask import Flask, render_template, request, redirect, url_for, make_response
from datetime import datetime

app = Flask(__name__)

# ──────────────────────────────────────────────────────
# DATENSPEICHER (temporär – kein Datenbank)
# ──────────────────────────────────────────────────────



# ──────────────────────────────────────────────────────
# HILFSFUNKTION – eingeloggten User aus Cookie lesen
# ──────────────────────────────────────────────────────
def get_current_user():
    return request.cookies.get("user")

# ══════════════════════════════════════════════════════
# STARTSEITE
# ══════════════════════════════════════════════════════
@app.route("/")
def start():
    user = get_current_user()

    if user:
        return redirect(url_for("overview"))   # wenn eingeloggt → Übersicht
    else:
        return redirect(url_for("login"))      # sonst → Login

# ══════════════════════════════════════════════════════
# REGISTRIERUNG
# ══════════════════════════════════════════════════════
@app.route("/register", methods=["GET", "POST"])
def register():
    fehler = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            fehler = "Bitte alle Felder ausfüllen."
        elif username in users:
            fehler = "Benutzername bereits vergeben."
        else:
            users[username] = password                      # User speichern
            return redirect(url_for("login"))               # → zum Login

    return render_template("register.html", fehler=fehler)


# ══════════════════════════════════════════════════════
# LOGIN
# ══════════════════════════════════════════════════════
@app.route("/login", methods=["GET", "POST"])
def login():
    fehler = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if users.get(username) == password:
            resp = make_response(redirect(url_for("overview")))
            resp.set_cookie("user", username, max_age=3600)  # 1 Stunde
            return resp
        else:
            fehler = "Falscher Benutzername oder Passwort."

    return render_template("login.html", fehler=fehler)


# ══════════════════════════════════════════════════════
# LOGOUT
# ══════════════════════════════════════════════════════
@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie("user", "", expires=0)                  # Cookie löschen
    return resp


# ══════════════════════════════════════════════════════
# ÜBERSICHT – alle Einträge des eingeloggten Users
# ══════════════════════════════════════════════════════
@app.route("/overview")
def overview():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))                   # nicht eingeloggt

    # Nur Einträge dieses Users, neueste zuerst
    my_entries = [e for e in entries if e["username"] == user]
    my_entries = sorted(my_entries, key=lambda e: e["date"], reverse=True)

    return render_template("overview.html", user=user, entries=my_entries)


# ══════════════════════════════════════════════════════
# NEUER EINTRAG
# ══════════════════════════════════════════════════════
@app.route("/new", methods=["GET", "POST"])
def new_entry():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    fehler = ""
    if request.method == "POST":
        title   = request.form.get("title", "").strip()
        date    = request.form.get("date", datetime.now().strftime("%Y-%m-%d"))
        content = request.form.get("content", "").strip()

        if not title or not content:
            fehler = "Titel und Inhalt dürfen nicht leer sein."
        else:
            entries.append({
                "id":       next_id[0],
                "username": user,
                "title":    title,
                "date":     date,
                "content":  content,
            })
            next_id[0] += 1                                 # ID hochzählen
            return redirect(url_for("overview"))

    # Heutiges Datum als Standardwert
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("new_entry.html", user=user, today=today, fehler=fehler)


# ══════════════════════════════════════════════════════
# EINTRAGSDETAIL – einzelnen Eintrag lesen
# ══════════════════════════════════════════════════════
@app.route("/entry/<int:entry_id>")
def entry_detail(entry_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    # Eintrag mit dieser ID suchen
    entry = next((e for e in entries if e["id"] == entry_id), None)

    if not entry or entry["username"] != user:
        return "Eintrag nicht gefunden.", 404               # Fehlercode 404

    return render_template("entry_detail.html", user=user, entry=entry)


# ══════════════════════════════════════════════════════
# EINTRAG BEARBEITEN
# ══════════════════════════════════════════════════════
@app.route("/edit/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    entry = next((e for e in entries if e["id"] == entry_id), None)

    if not entry or entry["username"] != user:
        return "Eintrag nicht gefunden.", 404

    fehler = ""
    if request.method == "POST":
        title   = request.form.get("title", "").strip()
        date    = request.form.get("date", entry["date"])
        content = request.form.get("content", "").strip()

        if not title or not content:
            fehler = "Titel und Inhalt dürfen nicht leer sein."
        else:
            entry["title"]   = title                        # Eintrag aktualisieren
            entry["date"]    = date
            entry["content"] = content
            return redirect(url_for("overview"))

    return render_template("edit_entry.html", user=user, entry=entry, fehler=fehler)


# ══════════════════════════════════════════════════════
# EINTRAG LÖSCHEN
# ══════════════════════════════════════════════════════
@app.route("/delete/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    global entries
    entries = [e for e in entries if not (e["id"] == entry_id and e["username"] == user)]
    # ↑ Alle Einträge behalten AUSSER den zu löschenden

    return redirect(url_for("overview"))


# ══════════════════════════════════════════════════════
# DASHBOARD – Statistiken
# ══════════════════════════════════════════════════════
@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    my_entries = [e for e in entries if e["username"] == user]

    # Einträge pro Monat zählen
    pro_monat = {}
    for e in my_entries:
        monat = e["date"][:7]                               # "2025-03"
        pro_monat[monat] = pro_monat.get(monat, 0) + 1     # Zähler +1

    pro_monat_sorted = dict(sorted(pro_monat.items()))      # chronologisch

    return render_template("dashboard.html",
                           user=user,
                           total=len(my_entries),
                           pro_monat=pro_monat_sorted)


# ──────────────────────────────────────────────────────
# START
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5001)