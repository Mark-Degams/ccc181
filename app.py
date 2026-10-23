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
]

MINUTES_PER_TICKET = 3  # average time to serve one person


@app.route("/")
def index():
    # render_template looks inside the templates/ folder and passes
    # keyword arguments to the template as variables.
    return render_template("index.html")


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # <int:ticket_id> only matches numbers, so /queue/abc returns 404.
    return render_template("ticket.html", ticket_id=ticket_id)


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
    if "@" not in email or "." not in email:
        errors["email"] = "Enter a valid email address."
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


@app.route("/staff")
def staff_dashboard():
    return "Staff dashboard coming soon"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)
