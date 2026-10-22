"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
from flask import Flask, render_template

app = Flask(__name__)

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
    return render_template("index.html", name="Ana", tickets=TICKETS)


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # <int:ticket_id> only matches numbers, so /queue/abc returns 404.
    return render_template("ticket.html", ticket_id=ticket_id)


@app.route("/hello")
def hello():
    # The plain-string version from the Routes slide.
    return "Hello, CCC181!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)
