from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from bcrypt import hashpw, gensalt, checkpw
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tagebuch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    entries = db.relationship('Entry', backref='user', lazy=True, cascade='all, delete-orphan')

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    content = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

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
        elif User.query.filter_by(username=username).first():
            fehler = "Benutzername bereits vergeben."
        else:
            hashed = hashpw(password.encode(), gensalt())
            user = User(username=username, password=hashed)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html", fehler=fehler)

@app.route("/login", methods=["GET", "POST"])
def login():
    fehler = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = User.query.filter_by(username=username).first()
        if user and checkpw(password.encode(), user.password):
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
    user_obj = User.query.filter_by(username=user).first()
    if not user_obj:
        session.clear()
        return redirect(url_for("login"))
    my_entries = Entry.query.filter_by(user_id=user_obj.id).order_by(Entry.date.desc()).all()
    return render_template("overview.html", user=user, entries=my_entries)

@app.route("/new", methods=["GET", "POST"])
def new_entry():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    user_obj = User.query.filter_by(username=user).first()
    if not user_obj:
        session.clear()
        return redirect(url_for("login"))
    fehler = ""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date = request.form.get("date", datetime.now().strftime("%Y-%m-%d"))
        content = request.form.get("content", "").strip()
        if not title or not content:
            fehler = "Titel und Inhalt dürfen nicht leer sein."
        else:
            entry = Entry(user_id=user_obj.id, title=title, date=datetime.strptime(date, "%Y-%m-%d").date(), content=content)
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("overview"))
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template("new_entry.html", user=user, today=today, fehler=fehler)

@app.route("/entry/<int:entry_id>")
def entry_detail(entry_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    user_obj = User.query.filter_by(username=user).first()
    if not user_obj:
        session.clear()
        return redirect(url_for("login"))
    entry = Entry.query.filter_by(id=entry_id, user_id=user_obj.id).first()
    if not entry:
        return "Eintrag nicht gefunden.", 404
    return render_template("entry_detail.html", user=user, entry=entry)

@app.route("/edit/<int:entry_id>", methods=["GET", "POST"])
def edit_entry(entry_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    user_obj = User.query.filter_by(username=user).first()
    if not user_obj:
        session.clear()
        return redirect(url_for("login"))
    entry = Entry.query.filter_by(id=entry_id, user_id=user_obj.id).first()
    if not entry:
        return "Eintrag nicht gefunden.", 404
    fehler = ""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        date = request.form.get("date", entry.date.strftime("%Y-%m-%d"))
        content = request.form.get("content", "").strip()
        if not title or not content:
            fehler = "Titel und Inhalt dürfen nicht leer sein."
        else:
            entry.title = title
            entry.date = datetime.strptime(date, "%Y-%m-%d").date()
            entry.content = content
            db.session.commit()
            return redirect(url_for("overview"))
    return render_template("edit_entry.html", user=user, entry=entry, fehler=fehler)

@app.route("/delete/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    user_obj = User.query.filter_by(username=user).first()
    if not user_obj:
        session.clear()
        return redirect(url_for("login"))
    entry = Entry.query.filter_by(id=entry_id, user_id=user_obj.id).first()
    if entry:
        db.session.delete(entry)
        db.session.commit()
    return redirect(url_for("overview"))

@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    user_obj = User.query.filter_by(username=user).first()
    if not user_obj:
        session.clear()
        return redirect(url_for("login"))
    my_entries = Entry.query.filter_by(user_id=user_obj.id).all()
    pro_monat = {}
    for e in my_entries:
        monat = e.date.strftime("%Y-%m")
        pro_monat[monat] = pro_monat.get(monat, 0) + 1
    return render_template("dashboard.html", user=user, total=len(my_entries), pro_monat=dict(sorted(pro_monat.items())))

if __name__ == "__main__":
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=debug, port=5002)