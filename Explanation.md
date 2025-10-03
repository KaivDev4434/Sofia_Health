# Technical Assessment Responses

## Question 1: Scaling to Thousands of Bookings Per Day

**If this had to handle thousands of bookings per day, what changes would I make first?**

The two most important changes I'd make are:

1. **Upgrade the Database**: Right now the system uses SQLite, which is perfect for testing but gets slow with lots of data. I'd switch to PostgreSQL (a more robust database) and add "indexes" - think of them like a book's index that helps you find pages quickly instead of reading every page. This would make searching appointments and filtering by provider or date much faster, even with millions of bookings.

2. **Move Slow Tasks to the Background**: Currently, when someone books an appointment, they have to wait for the confirmation email to send and the calendar to sync before seeing the success page. If we're handling thousands of bookings and the email server is slow, people would be stuck waiting. I'd move these tasks to run in the background - the booking saves instantly, people see confirmation right away, and emails/calendar updates happen behind the scenes. If something fails (like the email), it automatically retries without affecting the booking.

These changes would keep the booking experience fast and reliable even under heavy load, without changing how the system looks or works for users.

---

## Question 2: Communicating Progress and Blockers

**How would I communicate progress and blockers to a non-technical founder?**

I believe in **clear, regular updates with visuals**:

**Weekly Progress Reports** (every Friday):
- Show what's working: "This week I added the provider pricing system. You can now set different consultation and follow-up rates for each doctor. I've set up 5 test providers and the whole booking-to-payment flow is working smoothly."
- Share actual metrics: "The average booking takes 45 seconds from start to finish. Payment success rate in testing is 100%."
- Preview what's next: "Next week I'm building the analytics dashboard so you can track daily bookings, revenue, and see which providers are most popular."
- Include screenshots or short videos: It's much easier to show than explain.

**For Blockers** (communicate immediately):
I'd explain the problem, the impact, and my plan. For example: "Heads up - I hit a blocker with international payment testing. The Stripe test environment needs an upgrade to simulate international cards, which requires business verification and takes about 2 days. This means I can only test with US cards right now, but it won't affect real payments when we launch. I've submitted the verification request and will continue working on other features while we wait."

The key is being honest about obstacles while showing I have a plan. I avoid technical jargon and focus on what matters to the business: will it affect users, revenue, or timeline? And if I need a decision, I present options with clear trade-offs so you can choose what's best for the business.


