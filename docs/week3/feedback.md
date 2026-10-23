# Self-review: CinemaTicketQ wireframes

Reviewed against the personas Sandy (person waiting) and Wanda (staff member), on both the phone and laptop frames.

## Screen 1: Join the queue (Sandy, phone; FR-01)

**Works well:** The form has only four fields (name, email, service, party size) and one large "Get a ticket" button. Sandy can finish it in seconds with one hand, which follows my rule that her hands are often full.

**Problem:** Sandy has to type her email on a phone keyboard while holding food or bags, and a wrong entry would only show up after she submits. This breaks *error prevention*.

**Change:** Keep fields few, use the right input types (email, number) so the phone shows the right keyboard, and show the error text under each wrong field while keeping what she typed. I will also set "Buy tickets" as the first option in the service list because it is the most common service.

## Screen 2: My place (Sandy, phone; FR-02, FR-03, FR-07)

**Works well:** The ticket number is the biggest element, followed by the status, people ahead and estimated wait. This follows my rule that the number, position and wait time must be the biggest thing on screen.

**Problem:** The estimated wait could be read as a promise, and if the line moves slower than expected Sandy may lose trust. This breaks *visibility of system status*. The "Leave the queue" button also sits close to the info and could be tapped by mistake, which breaks *error prevention*.

**Change:** Word the estimate as "About 5 minutes", not an exact time. Move "Leave the queue" to the bottom of the card, away from the main info, and make the status show text ("Waiting", "Called"), not just color, so Sandy can see she has been called even from a distance.

## Screen 3: Staff dashboard (Wanda, laptop; FR-04, FR-05, FR-06)

**Works well:** "Next" is a large button at the top and each row has Serve and No-show buttons, so Wanda can act in one tap between customers. This follows my rule that her counter is busy and she has only seconds.

**Problem:** Serve and No-show sit side by side on every row, so on a busy counter she could tap the wrong one. This breaks *error prevention*. The button wording must also match what she says at the counter ("Next", "Serve"), which is *match between the system and the real world*.

**Change:** Give Serve and No-show different colors and wording (green "Serve", outlined red "No-show") and keep them well apart. Use one name for the main action, "Next", across the whole app and in the personas.