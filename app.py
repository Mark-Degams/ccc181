"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "dev-only-change-me"  # Week 11 moves this into an environment variable

# Sample data for the demo. A real app would load this from a database later.
SERVICES = [
    {"id": 1, "name": "Buy tickets"},
    {"id": 2, "name": "Claim reserved tickets"},
    {"id": 3, "name": "Refund or exchange"},
]

TICKETS = [
    {"number": 1, "name": "Ana", "email": "ana@email.com", "service_id": 1,
     "party_size": 2, "status": "waiting"},
    {"number": 2, "name": "Ben", "email": "ben@email.com", "service_id": 2,
     "party_size": 4, "status": "waiting"},
    {"number": 3, "name": "Carla", "email": "carla@email.com", "service_id": 1,
     "party_size": 3, "status": "waiting"},
    {"number": 4, "name": "Dino", "email": "dino@email.com", "service_id": 1,
     "party_size": 1, "status": "waiting"},
    {"number": 5, "name": "Ella", "email": "ella@email.com", "service_id": 3,
     "party_size": 2, "status": "waiting"},
    {"number": 6, "name": "Francis", "email": "francis@email.com", "service_id": 1,
     "party_size": 5, "status": "waiting"},
    {"number": 7, "name": "Gina", "email": "gina@email.com", "service_id": 2,
     "party_size": 2, "status": "waiting"},
    {"number": 8, "name": "Henry", "email": "henry@email.com", "service_id": 1,
     "party_size": 2, "status": "waiting"},
    {"number": 9, "name": "Iris", "email": "iris@email.com", "service_id": 1,
     "party_size": 4, "status": "waiting"},
    {"number": 10, "name": "Jonas", "email": "jonas@email.com", "service_id": 1,
     "party_size": 1, "status": "waiting"},
]

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


@app.get("/join")
def join_form():
    return render_template("join.html", services=SERVICES, form={}, errors={})


@app.post("/join")
def join():
    form = request.form
    name = form.get("name", "").strip()
    email = form.get("email", "").strip().lower()
    service_id = form.get("service_id", type=int)
    party_size = form.get("party_size", type=int)

    errors = {}
    if not name:
        errors["name"] = "Enter your name."
    if email and ("@" not in email or "." not in email):
        errors["email"] = "Enter a valid email address, or leave it blank."
    if service_id not in [s["id"] for s in SERVICES]:
        errors["service_id"] = "Choose a service."
    if party_size is None or not 1 <= party_size <= 10:
        errors["party_size"] = "Enter a party size from 1 to 10."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=SERVICES, form=form,
                               errors=errors), 400

    number = TICKETS[-1]["number"] + 1 if TICKETS else 1
    TICKETS.append({"number": number, "name": name, "email": email,
                    "service_id": service_id, "party_size": party_size,
                    "status": "waiting"})
    flash(f"You joined the queue. Your ticket is #{number}.", "success")
    return redirect(url_for("ticket", ticket_id=number))


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
