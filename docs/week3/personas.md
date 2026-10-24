## Sandy, the person waiting

> "I hate long line just to buy tickets" (interview)

| | |
| --- | --- |
| **Photo or sketch** | ![Sandy, the person waiting](personas/Sandy.jpg) |
| **Age, role and background** | 21, 3rd year BS Physics, Cinema Lover |
| **Goals** | Get tickets for a showing without standing in a long line; know roughly when her turn is; use the mall time (food, shopping) while waiting for the queue |
| **Frustrations** | The line at Robinsons Iligan Movie World can take about an hour on cinema days (observation); cannot leave the line in case of urgent calls such as needing to pee , unsure how long the line it will take |
| **Devices and context** | Phone, one hand holding food or bags, walking around the mall, mall Wi-Fi or mobile data |
| **Tech comfort** | High, as a college student technology is a friend that you need to master |
| **Accessibility needs** | One hand busy, slow data |

### Scenario

Sandy arrives at the robinsons mall in iligan at 10:00am, even at early arival the movie world is already packed with hundreds of people waiting to buy a ticket, She opens the app and scan the QRcode located at the sign board of the movieworld, picks "Buy Ticket" enter her name and party size, and get ticket #37 with estimated wait of about 47 minutes. She goes to buy something to eat and drink and even have time to play at the game center, 42 minutes later she goes back to the movie world and fall in line with just 3 people in her front and just 5 minutes, she brought a tickets for her party.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| Join the queue for a service | Join | FR-01 |
| Check my number and people ahead | My place | FR-02 |
| See the estimated wait | My place | FR-03 |
| Leave the queue | My place | FR-07 |

### What this means for my interface

1. Because cinema watcher want to buy foods and drinks before the movie start so there hands are mostly full, my interface must show the ticket number, position and wait time as the biggest on the screen. 
2. Because they roam around while waiting for their number, my interface must show live update wait time and position queue.
3. Because inside the building data can be slow, my interface must avoid large image to load and important details such as the wait number, wait time and position should be loaded even with slowest data.

## Wanda, the staff member

> "Why do people even cut in line? complains are so frustrating"

| | |
| --- | --- |
| **Photo or sketch** | ![Wanda, the staff member](personas/Wanda.jpg) |
| **Age, role and background** | 35, cashier at the cinema ticket booth, works long shifts |
| **Goals** | 	Keep the line moving; serve people in the right order; responding to people complaints   |
| **Frustrations** | people crowd the booth, people skip ahead, no clear order, people are complaining |
| **Devices and context** | Computers at the counter, customers talking to him at the same time, noisy, only a few seconds to a few minutes between customers |
| **Tech comfort** | Medium, as someone who use tech device everyday I mastered the on screen at the counter but aside from that most tech skills are low |
| **Accessibility needs** | Noisy and busy counter, glare, needs large buttons and one-click actions, shared device |

### Scenario

Wanda opens the staff dashboard at the start of her shift. The list shows who is waiting for each service, in order. She taps "Next", the customer walks up, and she sells the tickets. When she finishes she taps "Serve" then proceed to "Next". If a called customer does not show up after a few seconds, she taps "No-show" and calls the next one.

### Top tasks in the app

| Task | Screen | Requirement ID |
| --- | --- | --- |
| See the waiting list in order | Staff | FR-04 |
| Call the next person | Staff | FR-05 |
| Mark a ticket served or no-show | Staff | FR-05 |
| Filter by service | Staff | FR-06 |

### What this means for my interface

1.  Because the counter is busy and Wanda has majority only seconds between customers (interview), my interface must put a large "Next" button at the top of the dashboard.
2. Because she serves many people in a row, my interface must show the queue in order with Serve and No-show one tap away on each row.
3. Because refunds and ticket claims take different amounts of time, my interface must let her filter the list by service.
