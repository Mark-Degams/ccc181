# CinemaTicketQ requirements

**Setting:** Cinema ticket booth at a mall (Robinsons Iligan Movie World), cinema days when the line can take about an hour. The app manages the waiting line only; tickets are still bought at the booth.
**People who wait:** Moviegoers such as Sandy, a 21-year-old student with one hand busy and slow mall data. See [Sandy in docs/week3/personas.md](week3/personas.md).
**People who serve:** Booth cashiers such as Wanda, who have only seconds between customers. See [Wanda in docs/week3/personas.md](week3/personas.md).

**Problem statement:** A moviegoer who arrives at a busy mall cinema needs a way to know when it is their turn without standing in line, because the line can take about an hour and they cannot leave it for food, a phone call or the restroom without losing their place.

## Functional requirements

| ID | Requirement | Priority | Stores data? | Status |
| --- | --- | --- | --- | --- |
| FR-01 | A person can join the queue by entering their name, an optional email, a service and a party size, and receive a ticket number in under 30 seconds. | Must | **Yes** | Built (Week 3) |
| FR-02 | A person can see their ticket number, status and how many people are ahead of them on one screen. | Must | **Yes** | Built (Week 3) |
| FR-03 | A person can see an estimated wait ("About X minutes") and the expected clock time for their ticket. | Must | **Yes** | Built (Week 3), changed this week |
| FR-04 | Staff can see the waiting list in the order people joined. | Must | **Yes** | Built (Week 3) |
| FR-05 | Staff can call the next waiting ticket, for all services or one service, with one tap. | Must | **Yes** | Built (Week 3) |
| FR-06 | Staff can mark a called ticket as served or no-show with one tap. | Must | **Yes** | Built (Week 3) |
| FR-07 | A person can leave the queue before being served, and the ticket is kept as "left". | Must | **Yes** | Built (Week 3), changed this week |
| FR-08 | Staff can filter the dashboard by service and see how many are waiting per service. | Should | No | Built (Week 3) |
| FR-09 | Staff can add, rename and switch off a service, and a switched-off service no longer appears on the join form. | Must | **Yes** | This week |
| FR-10 ★ | A group can join with a party size of 1 to 10, and staff see the party size on every ticket. | Must | **Yes** | Built (Week 3) |
| FR-11 ★ | A person can open the join page by scanning a QR code at the Movie World signboard. | Should | No | Later |
| FR-12 ★ | Staff can see how many people left before being served, per service, per day. | Should | **Yes** | Later (Week 5) |
| FR-13 | Staff can permanently delete a mistaken or test ticket, after a confirmation. | Could | **Yes** | This week |
| FR-14 | The estimate uses the average time per person of the last 10 served tickets for that service, and falls back to the service's `avg_minutes` when no ticket has been served yet. | Should | **Yes** | This week |
| FR-15 | A person is warned on My place when 3 or fewer people are ahead of them, with a visible banner and, where the phone supports it, a vibration or sound. | Should | No | Later |

## Non-functional requirements

| ID | Requirement | Category | Priority |
| --- | --- | --- | --- |
| NFR-01 | No ticket is lost when the Flask server or the database restarts. | Reliability | Must |
| NFR-02 | Two people can never get the same ticket number, even if they join at the same moment. | Data integrity | Must |
| NFR-03 | My place shows the number, position and wait within 3 seconds on slow mall data, without large images. | Performance | Should |
| NFR-04 | Every screen scores 90 or higher in the Lighthouse accessibility check (mobile). | Accessibility | Must |
| NFR-05 | No password or secret key is stored in the repository. | Security | Must |
| NFR-06 | Every staff button gives visible feedback within 1 second of a tap (disabled with "Please wait…"). | Usability | Should |

## MVP

**MVP:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-09, FR-10, NFR-01, NFR-02, NFR-04, NFR-05.

This is the smallest version that solves the problem: a person can join from their phone, see where they are and walk away, and the cashier can call, serve and close tickets in order, with nothing lost when the server restarts. Everything else (reports, QR code, deleting tickets, alerts) makes the app nicer but does not change whether the line works.

**Out of scope this semester:**

- **Online ticket payment or seat selection.** Tickets are still bought at the booth, and payment adds security and legal work far beyond this course.
- **SMS or push notifications** (in-page alerts only, see FR-15). They need paid services and phone-number storage; the page refreshing every 10 seconds is enough for now.
- **Staff login.** Planned for Week 11 (issue: "Protect staff routes (Week 11)"), so the staff pages are open until then.

## Check with a real person

| Who (role only, no full name) | What they said | What I changed |
| --- | --- | --- |
| The person waiting | "If my number is almost up, I want a notification or a vibration so I won't keep looking at my phone." | Added FR-15 (Should): My place shows a banner when 3 or fewer people are ahead, plus a vibration or sound where the phone allows it. SMS and push notifications stay out of scope. |
| The person waiting | "The estimate can be wrong when the movie is about to start." | Changed FR-03 so the estimate is calculated from the latest tickets staff finished serving, not a fixed number. Added FR-14: the app averages the time per person for the last 10 served tickets of that service and multiplies it by the people ahead. It shows the expected clock time, such as "About 20 minutes (around 2:35 PM)", and falls back to `avg_minutes` when no ticket has been served yet. Added `served_at` to the Part 2 schema so the time per person can be calculated. |
| The person waiting | "Most important: how many ahead, joining easily, leaving the line." | Checked that FR-01, FR-02 and FR-07 are Must and in the MVP. They are, so no change. |