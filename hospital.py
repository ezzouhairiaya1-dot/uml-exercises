"""Exo 1 - Hospital Management System (UML practice).

Classes: User (abstract), Patient, Doctor, Organizer,
HealthProblem, Prescription, ProblemStatus (enum),
Payment (abstract), CheckPayment, CashPayment, CreditCardPayment.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


# ---------------------------------------------------------------- enum
class ProblemStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in review"
    RESOLVED = "resolved"


# ---------------------------------------------------------------- users
class User(ABC):
    """Shared attributes and behaviour of Patient, Doctor and Organizer."""

    def __init__(self, user_id, name, password):
        self._id = user_id
        self._name = name
        self._password = password
        self._logged_in = False

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def password(self):
        return self._password

    def login(self, password):
        self._logged_in = (password == self._password)
        return self._logged_in

    def logout(self):
        self._logged_in = False

    @abstractmethod
    def role(self):
        """Each subclass names its role."""

    def __str__(self):
        return f"{self.role()} {self._name} (id={self._id})"


class Patient(User):
    def __init__(self, user_id, name, password, address):
        super().__init__(user_id, name, password)
        self._address = address
        self._problems = []         # Patient 1 --- 0..* HealthProblem
        self._prescriptions = []    # past prescriptions

    def role(self):
        return "Patient"

    @property
    def problems(self):
        return self._problems

    @property
    def prescriptions(self):
        return self._prescriptions

    def post_problem(self, organizer, description):
        problem = HealthProblem(description, self)
        self._problems.append(problem)
        organizer.receive_problem(problem)
        return problem

    def receive_prescription(self, prescription):
        self._prescriptions.append(prescription)

    def pay(self, organizer, payment):
        payment.process()
        organizer.receive_payment(payment)


class Doctor(User):
    def __init__(self, user_id, name, password, speciality):
        super().__init__(user_id, name, password)
        self._speciality = speciality
        self._cases = []            # Doctor 1 --- 0..* HealthProblem
        self._fees = []             # payments forwarded by the organizer

    def role(self):
        return "Doctor"

    def consult(self, problem):
        problem.doctor = self
        problem.status = ProblemStatus.IN_REVIEW
        self._cases.append(problem)

    def write_prescription(self, problem, text):
        prescription = Prescription(text, self, problem)
        problem.prescription = prescription
        problem.status = ProblemStatus.RESOLVED
        return prescription

    def receive_fee(self, payment):
        self._fees.append(payment)


class Organizer(User):
    """Acts as intermediary AND as administrator."""

    def __init__(self, user_id, name, password):
        super().__init__(user_id, name, password)
        self._members = {}          # Organizer 1 --- 0..* User
        self._pending = []          # problems waiting for a doctor
        self._payments = []
        self._next_id = 1

    def role(self):
        return "Organizer"

    # ---- administrator side
    def _issue_credentials(self, name):
        user_id = self._next_id
        self._next_id += 1
        password = f"{name.lower()}{user_id}pw"
        return user_id, password

    def create_patient(self, name, address):
        user_id, password = self._issue_credentials(name)
        patient = Patient(user_id, name, password, address)
        self._members[user_id] = patient
        return patient

    def create_doctor(self, name, speciality):
        user_id, password = self._issue_credentials(name)
        doctor = Doctor(user_id, name, password, speciality)
        self._members[user_id] = doctor
        return doctor

    # ---- intermediary side
    def receive_problem(self, problem):
        self._pending.append(problem)

    def assign_to_doctor(self, problem, doctor):
        self._pending.remove(problem)
        doctor.consult(problem)

    def send_prescription(self, prescription):
        patient = prescription.problem.patient
        patient.receive_prescription(prescription)

    def receive_payment(self, payment):
        self._payments.append(payment)

    def forward_payment(self, payment, doctor):
        doctor.receive_fee(payment)


# ---------------------------------------------------------------- problem / prescription
class HealthProblem:
    _counter = 0

    def __init__(self, description, patient):
        HealthProblem._counter += 1
        self._id = HealthProblem._counter
        self._description = description
        self._created_at = datetime.now()
        self.status = ProblemStatus.PENDING
        self.patient = patient          # HealthProblem 0..* --- 1 Patient
        self.doctor = None              # HealthProblem 0..* --- 0..1 Doctor
        self.prescription = None        # HealthProblem 1 --- 0..1 Prescription

    def __str__(self):
        return (f"Problem #{self._id} '{self._description}' "
                f"[{self.status.value}]")


class Prescription:
    _counter = 0

    def __init__(self, text, doctor, problem):
        Prescription._counter += 1
        self._id = Prescription._counter
        self._text = text
        self._created_at = datetime.now()
        self.doctor = doctor
        self.problem = problem

    def __str__(self):
        return f"Prescription #{self._id}: {self._text}"


# ---------------------------------------------------------------- payments (strategy)
class Payment(ABC):
    def __init__(self, amount):
        self._amount = amount
        self._date = datetime.now()
        self._processed = False

    @property
    def amount(self):
        return self._amount

    @abstractmethod
    def process(self):
        """Each payment type processes itself differently."""

    def __str__(self):
        return f"{self.__class__.__name__} of {self._amount} EUR"


class CheckPayment(Payment):
    def __init__(self, amount, check_number):
        super().__init__(amount)
        self._check_number = check_number

    def process(self):
        self._processed = True
        print(f"  Check no. {self._check_number} cashed: {self._amount} EUR")


class CashPayment(Payment):
    def process(self):
        self._processed = True
        print(f"  Cash received: {self._amount} EUR")


class CreditCardPayment(Payment):
    def __init__(self, amount, card_number):
        super().__init__(amount)
        self._last4 = card_number[-4:]  # never store the full number

    def process(self):
        self._processed = True
        print(f"  Card **** {self._last4} charged: {self._amount} EUR")


# ---------------------------------------------------------------- demo scenario
if __name__ == "__main__":
    organizer = Organizer(0, "Admin", "admin-pw")

    # Registration: the organizer creates new members
    aya = organizer.create_patient("Aya", "12 rue des Lilas")
    dr_martin = organizer.create_doctor("Martin", "dermatology")
    print(aya)
    print(dr_martin)

    # Consultation flow
    print("\n1. Patient posts a problem")
    problem = aya.post_problem(organizer, "Red skin on my arm")
    print(" ", problem)

    print("2. Organizer reads it and consults a doctor")
    organizer.assign_to_doctor(problem, dr_martin)
    print(" ", problem)

    print("3. Doctor provides a prescription")
    prescription = dr_martin.write_prescription(problem, "Apply cream twice a day")
    print(" ", prescription)
    print(" ", problem)

    print("4. Organizer sends the prescription to the patient")
    organizer.send_prescription(prescription)
    print("  Patient now has", len(aya.prescriptions), "prescription(s)")

    # Payment processing (polymorphism: same call, different behaviour)
    print("5. Patient pays")
    for payment in [CheckPayment(40, "CHK-001"),
                    CashPayment(40),
                    CreditCardPayment(40, "4111111111111234")]:
        aya.pay(organizer, payment)

    print("6. Organizer forwards a payment to the doctor")
    organizer.forward_payment(payment, dr_martin)
    print("  Done.")
