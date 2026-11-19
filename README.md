# UML practice exercises

Two exercises from the OOP course: a Hospital Management System and ABCD Records.
Each one is modelled in UML and then implemented in Python.

## Files
- `diagrams.md`: class, sequence and use case diagrams (Mermaid, GitHub draws them)
- `hospital.py`: Python implementation of Exo 1 (Hospital)
- `abcd_records.py`: Python implementation of Exo 2 (ABCD Records)

Run an exercise with `python hospital.py` or `python abcd_records.py`.

## Exo 1: Hospital Management System

### Main design choices
- `User` is an abstract parent class (id, name, password, login, logout). `Patient`, `Doctor` and `Organizer` inherit from it.
- `Payment` is an abstract parent class. `CheckPayment`, `CashPayment` and `CreditCardPayment` implement `process()` in their own way.
- `HealthProblem` has a status (pending, in review, resolved) and timestamps.
- The `Organizer` sits between patients and doctors, and also acts as administrator (creates members, issues ids and passwords).

### Questions to consider

**1. How would you handle a patient consulting multiple doctors?**

The link between `HealthProblem` and `Doctor` becomes many-to-many (0..* on both sides). Since each doctor gives their own opinion, I would add an association class `Consultation` between them, with the doctor, the problem, a date, a status and notes. A `HealthProblem` then has 0..* `Consultation` objects, and each `Consultation` has at most one `Prescription`. The organizer decides what is sent to the patient: one prescription or several. In my code, the single `doctor` attribute of `HealthProblem` would become a list of consultations.

**2. Should prescriptions be reusable? How would you model that?**

Yes, for long-term treatments that are renewed. A prescription is a medical record, so I would never edit an old one. I would add `validUntil`, `renewable` and `renewalsLeft` to `Prescription`, and a method `renew()` that creates a new `Prescription` with a reference to the previous one (a 0..1 self-association `previousPrescription`). This keeps the full history, and it matches the "references to past prescriptions" requirement of Task 3.

**3. What design pattern fits the payment system?**

The Strategy pattern. `Payment` defines one interface, `process()`, and each payment type (check, cash, credit card) is a strategy with its own behaviour. The organizer calls `payment.process()` and does not need to know the type. A new payment type, for example a bank transfer, is just a new subclass, so existing code does not change (open/closed principle). A Factory could be added to create the right payment object from the patient's choice.

**4. How do you ensure data integrity when payments are processed?**

- Use a transaction: recording the payment and forwarding it to the doctor happen together, or not at all.
- Validate the data: the amount must be positive and match the fee of the prescription. A payment must reference an existing patient and prescription (foreign keys).
- Give each payment a unique id and a status (pending, completed, failed, refunded) with allowed transitions only. This prevents charging twice if the request is repeated.
- Only the organizer can forward a payment, and only after it is completed.
- Keep an audit log with timestamps, and store only the last 4 digits of a card number.

## Exo 2: ABCD Records

### Main design choices
- `Member` is abstract, with `RoyalMember` (10% discount, can order unavailable items) and `RegularMember`.
- `Item` is abstract, with `CD` and `Tape`.
- `Payment` is abstract, with `Cash`, `Check` and `BankDraft`.
- `Order` contains `OrderLine` objects (composition). `Invoice` and `ShippingList` are created when an order is processed.
- Non-members only receive a `MembershipApplication`. Orders are saved to the daily records file.


