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
from datetime import datetime, timedelta, timezone
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


@app.route("/")
def index():
    # render_template looks inside the templates/ folder and passes
    # keyword arguments to the template as variables.
    return render_template("index.html")


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    ahead = people_ahead(t)
    wait, eta = estimate(t, ahead)
    return render_template("ticket.html", ticket=t, service=t.service,
                           ahead=ahead, wait_minutes=wait, eta=eta)


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    ahead = people_ahead(t)
    wait, eta = estimate(t, ahead)
    return {"status": t.status, "ahead": ahead,
            "wait_minutes": wait, "eta": clock_text(eta)}


def all_services():
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()


def active_services():
    stmt = db.select(Service).filter_by(active=True).order_by(Service.name)
    return db.session.scalars(stmt).all()


PH_TIME = timezone(timedelta(hours=8))  # Philippine time has no daylight saving


@app.template_filter("local")
def local_time(value):
    """Show a database time in Philippine time, e.g. Nov 01, 08:01 PM."""
    return value.astimezone(PH_TIME).strftime("%b %d, %I:%M %p") if value else ""


@app.template_filter("clock")
def clock_text(value):
    """Clock time only, e.g. 2:35 PM."""
    return value.astimezone(PH_TIME).strftime("%I:%M %p").lstrip("0")


def people_ahead(t):
    """Count tickets still waiting for the same service that joined before t."""
    stmt = (db.select(func.count())
            .select_from(Ticket)
            .where(Ticket.service_id == t.service_id,
                   Ticket.status == "waiting",
                   Ticket.created_at < t.created_at))
    return db.session.scalar(stmt)


def minutes_per_person(service):
    """FR-14: average of the last 10 served tickets, else the service's avg_minutes."""
    stmt = (db.select(Ticket.called_at, Ticket.served_at)
            .where(Ticket.service_id == service.id,
                   Ticket.status == "served",
                   Ticket.served_at > Ticket.called_at)
            .order_by(Ticket.served_at.desc())
            .limit(10))
    rows = db.session.execute(stmt).all()
    if not rows:
        return service.avg_minutes
    seconds = sum((served - called).total_seconds() for called, served in rows)
    return seconds / len(rows) / 60


def estimate(t, ahead):
    """Return (wait in minutes, expected clock time) for a ticket."""
    wait = round(ahead * minutes_per_person(t.service))
    eta = datetime.now(timezone.utc) + timedelta(minutes=wait)
    return wait, eta


@app.get("/join")
def join_form():
    return render_template("join.html", services=active_services(), form={}, errors={})


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
    if service is None or not service.active:
        errors["service_id"] = "Choose a service."
    if party_size is None or not 1 <= party_size <= 10:
        errors["party_size"] = "Enter a party size from 1 to 10."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=active_services(),
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
        return render_template("join.html", services=active_services(),  # CHANGED
                               form=form, errors={}), 409

    flash(f"You joined the queue. Your ticket is #{ticket.id}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket.id))


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    stmt = (db.select(Ticket)
            .where(Ticket.status.in_(["waiting", "called"]))
            .order_by(Ticket.created_at))
    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)
    queue = db.session.scalars(stmt).all()

    services = all_services()
    counts = dict(db.session.execute(
        db.select(Ticket.service_id, func.count())
        .where(Ticket.status == "waiting")
        .group_by(Ticket.service_id)).all())
    waiting_counts = {s.id: counts.get(s.id, 0) for s in services}
    selected_service = db.session.get(Service, service_id) if service_id else None

    return render_template("staff.html", queue=queue, services=services,
                           selected=service_id, selected_service=selected_service,
                           waiting_counts=waiting_counts,
                           total_waiting=sum(waiting_counts.values()))


STAFF_ACTIONS = {"serve": "served", "no-show": "no-show"}


@app.post("/staff/call-next")
def call_next():
    service_id = request.form.get("service_id", type=int)
    stmt = (db.select(Ticket)
            .where(Ticket.status == "waiting")
            .order_by(Ticket.created_at)
            .limit(1))
    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)
    nxt = db.session.scalar(stmt)
    if nxt is None:
        flash("No one is waiting.", "warning")
    else:
        nxt.status = "called"
        nxt.called_at = func.now()  # the database fills in the time
        db.session.commit()
        flash(f"Calling ticket #{nxt.id} ({nxt.user.name}).", "info")
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    new_status = STAFF_ACTIONS.get(action)
    if new_status is None:
        abort(404)
    t = db.get_or_404(Ticket, ticket_id)
    if t.status in ("waiting", "called"):
        if new_status == "served":
            if t.called_at is None:
                t.called_at = func.now()  # served straight from waiting: set both times
            t.served_at = func.now()
        t.status = new_status
        db.session.commit()
        flash(f"Ticket #{ticket_id} marked {new_status}.", "info")
    else:
        flash(f"Ticket #{ticket_id} is already {t.status}.", "warning")
    service_id = request.form.get("service_id", type=int)
    return redirect(url_for("staff_dashboard", service_id=service_id))


@app.post("/queue/<int:ticket_id>/leave")
def leave_queue(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    if t.status in ("waiting", "called"):
        t.status = "left"  # soft delete: the row stays for reports (FR-12)
        db.session.commit()
        flash("You left the queue.", "info")
    return redirect(url_for("index"))


@app.post("/staff/tickets/<int:ticket_id>/delete")
def delete_ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    db.session.delete(t)  # hard delete: the row is gone for good
    db.session.commit()
    flash(f"Ticket #{ticket_id} was deleted.", "warning")
    return redirect(url_for("staff_dashboard"))


@app.get("/staff/services")
def services_list():
    return render_template("services.html", services=all_services())


@app.post("/staff/services")
def service_create():
    name = request.form.get("name", "").strip()
    minutes = request.form.get("avg_minutes", type=int)
    if not name or len(name) > 60 or not minutes or minutes <= 0:
        flash("Enter a name (up to 60 characters) and minutes greater than 0.", "danger")
        return redirect(url_for("services_list"))
    db.session.add(Service(name=name, avg_minutes=minutes))
    try:
        db.session.commit()
        flash(f"Service “{name}” added.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A service named “{name}” already exists.", "danger")
    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>/edit")
def service_edit(service_id):
    s = db.get_or_404(Service, service_id)
    name = request.form.get("name", "").strip()
    minutes = request.form.get("avg_minutes", type=int)
    if not name or len(name) > 60 or not minutes or minutes <= 0:
        flash("Enter a name (up to 60 characters) and minutes greater than 0.", "danger")
        return redirect(url_for("services_list"))
    s.name = name
    s.avg_minutes = minutes
    s.active = request.form.get("active") == "on"  # an unticked box is not sent at all
    try:
        db.session.commit()
        flash(f"Service “{name}” saved.", "success")
    except IntegrityError:
        db.session.rollback()
        flash(f"A service named “{name}” already exists.", "danger")
    return redirect(url_for("services_list"))


@app.post("/staff/services/<int:service_id>/delete")
def service_delete(service_id):
    s = db.get_or_404(Service, service_id)
    if s.tickets:
        flash(f"“{s.name}” has tickets, so it cannot be deleted. Turn it off instead.", "danger")
        return redirect(url_for("services_list"))
    name = s.name
    db.session.delete(s)
    db.session.commit()
    flash(f"Service “{name}” deleted.", "warning")
    return redirect(url_for("services_list"))


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)
