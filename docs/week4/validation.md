# Validation in three layers: CinemaTicketQ

The same rule can live in three places. The browser gives fast feedback to users, Flask is the real gatekeeper, and the database is the last line of defense against any bug.

## Browser layer

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| Name is limited to 80 characters (`maxlength="80"`) | Browser | Opened `/join` and typed more than 80 characters into "Your name" | The field stopped accepting characters at 80. |
| Email is limited to 120 characters (`maxlength="120"`) | Browser | Opened `/join` and typed more than 120 characters into "Email (optional)" | The field stopped accepting characters at 120. |

## Flask layer (curl, skipping the form)

How I ran these: Flask running in terminal 1 (`flask --app app run --debug`), and the commands below in a second PowerShell window, using `curl.exe` (not `curl`).

Ticket count, from `docker compose exec db psql -U cinemaq -c "SELECT count(*) FROM tickets;"`.

Tickets before the tests: 6. Tickets after all five tests: 6 (the same number, so none of the bad requests saved anything).

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| Empty name, bad email and unknown service are refused | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=" -d "email=not-an-email" -d "service_id=999" -d "party_size=1"` | HTTP/1.1 400 BAD REQUEST, nothing saved |
| Name longer than 80 characters is refused | Flask | `$n = "a" * 200` then `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=$n" -d "service_id=1" -d "party_size=1"` | HTTP/1.1 400 BAD REQUEST, nothing saved |
| Party size must be 1 to 10 | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=Test" -d "service_id=1" -d "party_size=11"` | HTTP/1.1 400 BAD REQUEST, nothing saved |
| Email must contain @ and a dot | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=Test" -d "email=ana@x" -d "service_id=1" -d "party_size=1"` | HTTP/1.1 400 BAD REQUEST, nothing saved |
| A switched-off service is refused | Flask | `SELECT id, name, active FROM services;` showed "Claim reserved tickets" (id 2) with `active = f`, then `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=Test" -d "service_id=2" -d "party_size=1"` | HTTP/1.1 400 BAD REQUEST, nothing saved (ticket count stayed at 6). My first attempt used id 3, which was still active, and Flask correctly accepted it, so I cleaned up that test ticket and repeated the test with id 2. |

## Database layer (psql, skipping Flask)

How I ran these: `docker compose exec db psql -U cinemaq`, then typed each statement at the `cinemaq=#` prompt. I first looked up real ids with `SELECT id, status FROM tickets ORDER BY id;`, `SELECT id, email FROM users;` and `SELECT id, name FROM services;`.

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| Service must exist | Database (FOREIGN KEY) | `INSERT INTO tickets (user_id, service_id) VALUES (1, 999);` (user 1 exists, service 999 does not) | ERROR:  insert or update on table "tickets" violates foreign key constraint "tickets_service_id_fkey" <br> DETAIL:  Key (service_id)=(999) is not present in table "services". |
| Email must be unique | Database (UNIQUE) | Ran `INSERT INTO users (name, email) VALUES ('Copy', 'ana@email.com');` twice. The first run added the row, so the second run used an email that already existed. | ERROR:  duplicate key value violates unique constraint "users_email_key" <br> DETAIL:  Key (email)=(ana@email.com) already exists. |
| Status must be one of five values | Database (CHECK) | `UPDATE tickets SET status = 'lost' WHERE id = 1;` (ticket 1 exists) | ERROR:  new row for relation "tickets" violates check constraint "ck_tickets_status" <br> DETAIL:  Failing row contains (1, 1, lost, 2026-11-01 14:27:37.303387+00, 2026-11-01 14:40:01.909684+00, 2026-11-01 14:43:01.909684+00, 1, 1). |
| Party size must be 1 to 10 | Database (CHECK) | `UPDATE tickets SET party_size = 11 WHERE id = 1;` | ERROR:  new row for relation "tickets" violates check constraint "ck_tickets_party_size" <br> DETAIL:  Failing row contains (1, 11, served, 2026-11-01 14:27:37.303387+00, 2026-11-01 14:40:01.909684+00, 2026-11-01 14:43:01.909684+00, 1, 1). |
| Minutes per person must be above 0 | Database (CHECK) | `INSERT INTO services (name, avg_minutes) VALUES ('Test', 0);` | ERROR:  new row for relation "services" violates check constraint "ck_services_avg_minutes" <br> DETAIL:  Failing row contains (4, Test, 0, t) |
| A served ticket must have its times | Database (CHECK) | `UPDATE tickets SET status = 'served' WHERE id = 2;` (ticket 2 was a ticket with no `called_at` or `served_at`) | ERROR:  new row for relation "tickets" violates check constraint "ck_tickets_called_time" <br> DETAIL:  Failing row contains (2, 2, served, 2026-11-01 14:28:50.361462+00, null, null, 2, 1). |
| A person must have a name | Database (NOT NULL) | `INSERT INTO users (email) VALUES ('x@y.com');` | ERROR:  null value in column "name" of relation "users" violates not-null constraint <br> DETAIL:  Failing row contains (10, null, x@y.com) |
| A service with tickets cannot be deleted | Database (ON DELETE RESTRICT) | `DELETE FROM services WHERE id = 1;` (service 1 has tickets) | ERROR:  update or delete on table "services" violates foreign key constraint "tickets_service_id_fkey" on table "tickets" <br> DETAIL:  Key (id)=(1) is still referenced from table "tickets". |
| A good row gets its defaults | Database (defaults) | `INSERT INTO tickets (user_id, service_id) VALUES (1, 1) RETURNING id, status, party_size, created_at;`, then removed the test ticket with `DELETE FROM tickets WHERE id = 11;` | Succeeded (`INSERT 0 1`). The database filled in the defaults: id 11, status `waiting`, party_size `1`, created_at `2026-11-02 00:48:01.300651+00`. |

## SQL injection check

| Rule | Layer | How I tested it | What happened |
| --- | --- | --- | --- |
| No SQL is built with f-strings | Code | In the project folder: `git grep -nE 'f".*(SELECT\|INSERT\|UPDATE\|DELETE)' -- '*.py'` and `git grep -nE "f'.*(SELECT\|INSERT\|UPDATE\|DELETE)" -- '*.py'` | Both commands printed nothing, so no SQL is built from f-strings. `git grep -n "db.select" -- "*.py"` lists every query in `app.py`, and all of them use `db.select(...)` with bound parameters. |