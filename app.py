"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import os

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import Service, Ticket, User, db

load_dotenv()

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"

db.init_app(app)
migrate = Migrate(app, db)


@app.cli.command("seed")
def seed():
    """Add the starting services if they are not there yet."""
    starting = [
        ("Buy tickets", 3),
        ("Claim reserved tickets", 3),
        ("Refund or exchange", 5),
    ]
    for name, minutes in starting:
        exists = db.session.scalar(db.select(Service).filter_by(name=name))
        if exists is None:
            db.session.add(Service(name=name, avg_minutes=minutes))
    db.session.commit()
    print("Services are ready.")

MINUTES_PER_TICKET = 3  # average time to serve one person


@app.route("/")
def index():
    # render_template looks inside the templates/ folder and passes
    # keyword arguments to the template as variables.
    return render_template("index.html")


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)
    ahead = [x for x in TICKETS
             if x["service_id"] == t["service_id"]
             and x["status"] == "waiting"
             and x["number"] < t["number"]]
    service = next(s for s in SERVICES if s["id"] == t["service_id"])
    wait_minutes = len(ahead) * MINUTES_PER_TICKET
    return render_template("ticket.html", ticket=t, service=service,
                           ahead=len(ahead), wait_minutes=wait_minutes)


@app.post("/queue/<int:ticket_id>/leave")
def leave_queue(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)
    if t["status"] in ("waiting", "called"):
        t["status"] = "no-show"
        flash(f"You left the queue. Ticket #{ticket_id} was cancelled.", "info")
    return redirect(url_for("index"))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)
    ahead = sum(1 for x in TICKETS
                if x["service_id"] == t["service_id"]
                and x["status"] == "waiting"
                and x["number"] < t["number"])
    return {"status": t["status"], "ahead": ahead,
            "wait_minutes": ahead * MINUTES_PER_TICKET}


def all_services():
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()


@app.get("/join")
def join_form():
    return render_template("join.html", services=all_services(), form={}, errors={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    service_id = form.get("service_id", type=int)
    party_size = form.get("party_size", type=int)
    service = db.session.get(Service, service_id) if service_id else None

    errors = {}
    if not name or len(name) > 80:
        errors["name"] = "Enter your name (up to 80 characters)."
    if email and ("@" not in email or "." not in email or len(email) > 120):
        errors["email"] = "Enter a valid email address, or leave it blank."
    if service is None:
        errors["service_id"] = "Choose a service."
    if party_size is None or not 1 <= party_size <= 10:
        errors["party_size"] = "Enter a party size from 1 to 10."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors=errors), 400

    user = None
    if email:
        user = db.session.scalar(db.select(User).filter_by(email=email))
    if user is None:
        user = User(name=name, email=email or None)  # empty email is stored as NULL
    else:
        user.name = name  # same email, latest name wins (schema review, entry 4)

    ticket = Ticket(user=user, service=service, party_size=party_size)
    db.session.add(ticket)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Something went wrong saving your ticket. Please try again.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors={}), 409

    flash(f"You joined the queue. Your ticket is #{ticket.id}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket.id))


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    queue = [t for t in TICKETS if t["status"] in ("waiting", "called")]
    waiting_counts = {
        s["id"]: sum(1 for t in queue
                     if t["service_id"] == s["id"] and t["status"] == "waiting")
        for s in SERVICES
    }
    total_waiting = sum(waiting_counts.values())
    if service_id:
        queue = [t for t in queue if t["service_id"] == service_id]
    names = {s["id"]: s["name"] for s in SERVICES}
    return render_template("staff.html", queue=queue, services=SERVICES,
                           names=names, selected=service_id,
                           waiting_counts=waiting_counts,
                           total_waiting=total_waiting)


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)
    nxt = next((t for t in TICKETS
                if t["status"] == "waiting"
                and (not service_id or t["service_id"] == service_id)), None)
    if nxt is None:
        flash("No one is waiting.", "warning")
    else:
        nxt["status"] = "called"
        flash(f"Calling ticket #{nxt['number']} ({nxt['name']}).", "info")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = {"serve": "served", "no-show": "no-show"}.get(action)
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None or new_status is None:
        abort(404)
    t["status"] = new_status
    flash(f"Ticket #{ticket_id} marked {new_status}.", "info")
    service_id = request.form.get("service_id", type=int)
    return redirect(url_for("staff_dashboard", service_id=service_id))


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)
