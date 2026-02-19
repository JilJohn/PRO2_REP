# PRO2_REP – Digitales Tagebuch

## Projektidee
**Digitales Tagebuch – Deine persönliche Eintragsbibliothek**

Viele Menschen möchten ihre Gedanken, Erlebnisse und Reflexionen regelmässig festhalten. Häufig werden Einträge jedoch in verschiedenen Notizbüchern, Apps oder einzelnen Dokumenten gespeichert, wodurch der Überblick verloren geht.

Diese Web-App bietet eine zentrale, digitale Lösung, um Tagebucheinträge strukturiert zu erfassen, zu verwalten und jederzeit wieder abzurufen.

---

## Ausgangslage

Das **Digitale Tagebuch** ist eine Web-App, mit der Nutzer ihre persönlichen Tagebucheinträge erstellen und verwalten können.

Der Nutzer kann:

- neue Einträge verfassen
- bestehende Einträge bearbeiten oder löschen
- vergangene Gedanken chronologisch einsehen

---

## Problemstellung

Gedanken und persönliche Notizen sind oft verstreut gespeichert.  
Die App löst dieses Problem durch eine **zentrale Sammlung aller Tagebucheinträge** in einer übersichtlichen digitalen Umgebung.

---

## Ansichten der App

### Übersicht
- Liste aller Tagebucheinträge
- Anzeige von Titel und Datum
- Schnelle Navigation zu einzelnen Einträgen

### Eintragsdetails
- Vollständiger Tagebucheintrag
- Titel
- Datum
- Inhalt / Text

### Journal / Einträge
- Freitextfeld zum Schreiben persönlicher Gedanken
- Bearbeiten bestehender Einträge

### Dashboard
- Grafische Darstellung der Einträge
- Anzahl Einträge insgesamt
- Visualisierung nach Zeitraum (z. B. pro Monat)

---

## Daten

### Eingelesen
- Titel des Eintrags
- Textinhalt
- Datum

### Gespeichert
- Eintragsdatum
- Inhalt des Tagebucheintrags
- Benutzerzuordnung

### Ausgegeben
- Eintragsübersicht
- Detailansicht eines Eintrags
- Statistische Darstellung im Dashboard

---

## Funktionen für den Nutzer

- Registrierung eines Benutzerkontos
- Login und Logout
- Einträge hinzufügen
- Einträge bearbeiten
- Einträge löschen
- Einträge lesen
- Übersicht aller Einträge anzeigen

---

## Umsetzung mit Flask

### Backend
- Flask (Python)
- Routing
- Datenverarbeitung
- Benutzer-Authentifizierung

### Frontend
- HTML
- CSS
- Einfache Benutzeroberfläche

---

## Benutzerführung & Funktionen der App

### Registrierung
Bei der erstmaligen Nutzung registriert sich der Nutzer mit:

- Benutzername
- Passwort

Nach erfolgreicher Registrierung kann sich der Nutzer anmelden.

---

### Login
Der Nutzer meldet sich mit Benutzername und Passwort an und wird anschliessend auf die Hauptseite weitergeleitet.

---

## Navigation (4 Hauptbereiche)

### 1. Neuer Eintrag
Der Nutzer erstellt einen neuen Tagebucheintrag mit:

- Titel
- Datum (automatisch oder manuell)
- Textinhalt

---

### 2. Übersicht
- Anzeige aller bisherigen Einträge
- Chronologische Liste

---

### 3. Dashboard
Grafische Übersicht über:

- Anzahl Einträge
- Einträge pro Zeitraum

---

### 4. Logout
- Nutzer kann sich jederzeit abmelden
- Weiterleitung zur Login-Seite

---

## Installation (geplant)

```bash
git clone https://github.com/JilJohn/PRO2_REP.git
cd PRO2_REP
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python run.py
