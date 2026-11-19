"""Exo 2 - ABCD Records (UML practice).

Members: Member (abstract) -> RoyalMember, RegularMember. NonMember is separate.
Items: Item (abstract) -> CD, Tape.
Payments: Payment (abstract) -> Cash, Check, BankDraft.
Documents: Order (with OrderLine), Invoice, ShippingList, MembershipApplication.
Staff: OrderProcessingClerk, CollectionDepartmentClerk.
"""

from abc import ABC, abstractmethod
from datetime import date


# ---------------------------------------------------------------- people
class Member(ABC):
    def __init__(self, member_id, name, address):
        self._id = member_id
        self._name = name
        self._address = address
        self._orders = []           # Member 1 --- 0..* Order

    @property
    def name(self):
        return self._name

    @property
    def orders(self):
        return self._orders

    @abstractmethod
    def discount_rate(self):
        """Fraction removed from the price (0.10 = 10%)."""

    @abstractmethod
    def can_order_unavailable(self):
        """Only Royal members may order items that are out of stock."""

    def __str__(self):
        return f"{self.__class__.__name__} {self._name} (id={self._id})"


class RoyalMember(Member):
    def discount_rate(self):
        return 0.10

    def can_order_unavailable(self):
        return True


class RegularMember(Member):
    def discount_rate(self):
        return 0.0

    def can_order_unavailable(self):
        return False


class NonMember:
    def __init__(self, name, address):
        self._name = name
        self._address = address

    @property
    def name(self):
        return self._name

    @property
    def address(self):
        return self._address


# ---------------------------------------------------------------- items
class Item(ABC):
    def __init__(self, item_id, title, artist, price, stock):
        self._id = item_id
        self._title = title
        self._artist = artist
        self._price = price
        self._stock = stock

    @property
    def title(self):
        return self._title

    @property
    def price(self):
        return self._price

    def is_available(self, quantity):
        return self._stock >= quantity

    def remove_stock(self, quantity):
        self._stock -= quantity

    def __str__(self):
        return f"{self.__class__.__name__} '{self._title}' ({self._price} EUR)"


class CD(Item):
    pass


class Tape(Item):
    pass


# ---------------------------------------------------------------- order
class OrderLine:
    """Composition: an OrderLine cannot exist without its Order."""

    def __init__(self, item, quantity, backordered=False):
        self.item = item                 # OrderLine * --- 1 Item
        self.quantity = quantity
        self.backordered = backordered   # unavailable item ordered by a Royal member

    def subtotal(self):
        return self.item.price * self.quantity


class Order:
    def __init__(self, member):
        self.member = member             # Order * --- 1 Member
        self.date = date.today()
        self.lines = []                  # Order 1 <>--- 1..* OrderLine
        self.status = "new"

    def add_line(self, item, quantity, backordered=False):
        self.lines.append(OrderLine(item, quantity, backordered))

    def total(self):
        gross = sum(line.subtotal() for line in self.lines)
        return round(gross * (1 - self.member.discount_rate()), 2)

    def __str__(self):
        return f"Order of {self.member.name} on {self.date} [{self.status}]"


class Invoice:
    def __init__(self, order):
        self.order = order               # Invoice 1 --- 1 Order
        self.amount = order.total()
        self.paid = False

    def print_invoice(self):
        print("  --- INVOICE ---")
        for line in self.order.lines:
            print(f"  {line.quantity} x {line.item.title}: {line.subtotal()} EUR")
        rate = int(self.order.member.discount_rate() * 100)
        print(f"  Discount: {rate}%")
        print(f"  TOTAL: {self.amount} EUR")


class ShippingList:
    def __init__(self, order):
        self.order = order
        self.lines = [l for l in order.lines if not l.backordered]

    def print_list(self):
        print("  --- SHIPPING LIST ---")
        for line in self.lines:
            print(f"  {line.quantity} x {line.item.title}")
        for line in self.order.lines:
            if line.backordered:
                print(f"  (later) {line.quantity} x {line.item.title}")


class MembershipApplication:
    def __init__(self, applicant):
        self.applicant = applicant

    def __str__(self):
        return f"Membership application form sent to {self.applicant.name}"


# ---------------------------------------------------------------- payments
class Payment(ABC):
    def __init__(self, amount):
        self._amount = amount

    @property
    def amount(self):
        return self._amount

    @abstractmethod
    def process(self):
        """Each payment type is handled differently."""


class Cash(Payment):
    def process(self):
        print(f"  Cash received: {self._amount} EUR")


class Check(Payment):
    def __init__(self, amount, check_number):
        super().__init__(amount)
        self._check_number = check_number

    def process(self):
        print(f"  Check {self._check_number} deposited: {self._amount} EUR")


class BankDraft(Payment):
    def __init__(self, amount, draft_number):
        super().__init__(amount)
        self._draft_number = draft_number

    def process(self):
        print(f"  Bank draft {self._draft_number} cleared: {self._amount} EUR")


# ---------------------------------------------------------------- daily records
class DailyRecords:
    """All orders are saved to the daily records file."""

    def __init__(self):
        self._orders = []

    def add(self, order):
        self._orders.append(order)

    def save_to_file(self, filename="daily_records.txt"):
        with open(filename, "a", encoding="utf-8") as f:
            for order in self._orders:
                f.write(f"{order} | total={order.total()} EUR\n")


# ---------------------------------------------------------------- staff
class OrderProcessingClerk:
    def __init__(self, name, records):
        self._name = name
        self._records = records

    def send_membership_application(self, non_member):
        application = MembershipApplication(non_member)
        print(" ", application)
        return application

    def verify_membership(self, person):
        return isinstance(person, Member)

    def process_request(self, person, wanted):
        """wanted = list of (item, quantity). Returns (order, invoice) or None."""
        if not self.verify_membership(person):
            self.send_membership_application(person)
            return None

        order = Order(person)
        for item, quantity in wanted:
            if item.is_available(quantity):
                item.remove_stock(quantity)
                order.add_line(item, quantity)
            elif person.can_order_unavailable():
                order.add_line(item, quantity, backordered=True)
                print(f"  '{item.title}' unavailable: ordered for later (Royal).")
            else:
                print(f"  '{item.title}' unavailable: line refused.")

        if not order.lines:
            return None

        order.status = "processed"
        person.orders.append(order)
        self._records.add(order)

        invoice = Invoice(order)
        invoice.print_invoice()
        ShippingList(order).print_list()
        return order, invoice


class CollectionDepartmentClerk:
    def collect_payment(self, invoice, payment):
        payment.process()
        if payment.amount >= invoice.amount:
            invoice.paid = True
            invoice.order.status = "paid"


# ---------------------------------------------------------------- demo scenario
if __name__ == "__main__":
    records = DailyRecords()
    clerk = OrderProcessingClerk("Sam", records)
    collector = CollectionDepartmentClerk()

    cd1 = CD(1, "Kind of Blue", "Miles Davis", 15.0, stock=5)
    cd2 = CD(2, "Rare Album", "Unknown", 25.0, stock=0)   # unavailable
    tape = Tape(3, "Mixtape 90s", "Various", 8.0, stock=2)

    print("Scenario 1: a non-member tries to order")
    clerk.process_request(NonMember("Lea", "5 rue Verte"), [(cd1, 1)])

    print("\nScenario 2: Royal member orders 2 CDs (one unavailable), pays by check")
    royal = RoyalMember(10, "Aya", "12 rue des Lilas")
    result = clerk.process_request(royal, [(cd1, 1), (cd2, 1)])
    if result:
        order, invoice = result
        collector.collect_payment(invoice, Check(invoice.amount, "CHK-77"))
        print(" ", order)

    print("\nScenario 3: Regular member orders the same unavailable CD")
    regular = RegularMember(11, "Tom", "3 av. Foch")
    clerk.process_request(regular, [(cd2, 1), (tape, 1)])

    records.save_to_file()
    print("\nOrders saved to daily_records.txt")
