# Schema self-review: CinemaTicketQ

I put the ERD away for an hour, then reviewed it against the six questions in Part 3.

## 1. Works well

**Works well:** `tickets` stores only facts (`created_at`, `called_at`, `served_at`) and no position or estimated wait.
**Problem:** none here. This answers question 3 (facts, not results).
**Change:** none. The position is counted from `created_at`, and the estimate is the average of `served_at - called_at` over the last 10 served tickets, so neither can go out of date. It also lets FR-14 work without any extra column.

## 2. Unused column

**Works well:** every table traces back to a requirement marked *Stores data? = Yes*, and every other column is used by one.
**Problem:** `users.role` is not needed by any requirement this week, because staff login is planned for Week 11. This was found by question 1 (coverage).
**Change:** I removed `role` from the ERD, `schema.md` and the models. In Week 11, when staff accounts become a requirement, it will be added with a new migration. This also keeps the schema matching the requirements exactly.

## 3. Status and times can disagree

**Works well:** `status` already has a CHECK that allows only five values, so a typo like `'lost'` cannot be saved.
**Problem:** nothing forces the times to match the status. A ticket could be `called` with no `called_at`, or `served` with no `served_at`, which would break the FR-14 average. This was found by question 4 (bad data).
**Change:** I added two CHECK constraints to `tickets`:

- `ck_tickets_called_time`: `status NOT IN ('called', 'served') OR called_at IS NOT NULL`
- `ck_tickets_served_time`: `status <> 'served' OR served_at IS NOT NULL`

My Week 3 dashboard also lets staff press Serve on a ticket that is still waiting. Under the new rule, the app must set `called_at` and `served_at` together in that case. Those instant services would give a time per person of 0, so the FR-14 average should only use tickets where `served_at` is later than `called_at`.

## 4. Same email, new name

**Works well:** `users.email` is UNIQUE, so one person with an email can never have two accounts.
**Problem:** if the same email joins again with a different name (for example a nickname), the old name stays and staff would call the wrong name. This was found by question 2 (one fact in one place).
**Change:** no schema change. In the `join` route, when the email already exists, I update `users.name` to the name just typed, so the latest name is the only one stored.

## Kept on purpose

People who give no email get a new `users` row each visit, because there is nothing to match them on (question 2). I kept this because FR-01 makes email optional after my usability test, and joining quickly matters more than linking anonymous visits.