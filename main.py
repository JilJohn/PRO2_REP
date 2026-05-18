from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "dein-geheimer-schluessel-2026"

users = {}
entries = []
next_id = [1]

def get_current_user():
    return session.get("user")

@app.route("/")
def start():
    return redirect(url_for("overview" if get_current_user() else "login"))

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
            users[username] = password
            return redirect(url_for("login"))
    return render_template("register.html", fehler=fehler)

@app.route("/login", methods=["GET", "POST"])
def login():
    fehler = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if users.get(username) == password:
            session["user"] = username
            return redirect(url_for("overview"))
        else:
            fehler = "Falscher Benutzername oder Passwort."
    return render_template("login.html", fehler=fehler)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/overview")
def overview():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    my_entries = sorted([e for e in entries if e["username"] == user], key=lambda e: e["date"], reverse=True)
    return render_template("overview.html", user=user, entries=my_entries)

@app.route("/new", methods=["GET", "POST"])
def new_entry():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    fehler = ""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date = request.form.get("date", datetime.now().strftime("%Y-%m-%d"))
        content = request.form.get("content", "").strip()
        if not title or not content:
            fehler = "Titel und Inhalt dürfen nicht leer sein."
        else:
            entries.append({
                "id": next_id[0],
                "username": user,
                "title": title,
                "date": date,
                "content": content,
            })
            next_id[0] += 1
            return redirect(url_for("overview"))
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("new_entry.html", user=user, today=today, fehler=fehler)

@app.route("/entry/<int:entry_id>")
def entry_detail(entry_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    entry = next((e for e in entries if e["id"] == entry_id), None)
    if not entry or entry["username"] != user:
        return "Eintrag nicht gefunden.", 404
    return render_template("entry_detail.html", user=user, entry=entry)

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
        title = request.form.get("title", "").strip()
        date = request.form.get("date", entry["date"])
        content = request.form.get("content", "").strip()
        if not title or not content:
            fehler = "Titel und Inhalt dürfen nicht leer sein."
        else:
            entry["title"] = title
            entry["date"] = date
            entry["content"] = content
            return redirect(url_for("overview"))
    return render_template("edit_entry.html", user=user, entry=entry, fehler=fehler)

@app.route("/delete/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    global entries
    entries = [e for e in entries if e["id"] != entry_id or e["username"] != user]
    return redirect(url_for("overview"))

@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    my_entries = [e for e in entries if e["username"] == user]
    pro_monat = {}
    for e in my_entries:
        monat = e["date"][:7]
        pro_monat[monat] = pro_monat.get(monat, 0) + 1
    return render_template("dashboard.html", user=user, total=len(my_entries), pro_monat=dict(sorted(pro_monat.items())))

if __name__ == "__main__":
    app.run(debug=True, port=5001)