# UML exercises: diagrams

Diagrams are written in Mermaid. GitHub draws them automatically when you open this file.

## Exo 1: Hospital Management System

### Class diagram (Task 1, 2 and 3)

```mermaid
classDiagram
    class User {
        <<abstract>>
        -int id
        -string name
        -string password
        +login()
        +logout()
    }
    class Patient {
        -string address
        +postProblem()
        +pay()
        +viewPrescription()
    }
    class Doctor {
        -string speciality
        +consult()
        +writePrescription()
    }
    class Organizer {
        +receiveProblem()
        +assignToDoctor()
        +sendPrescription()
        +forwardPayment()
        +createMember()
    }
    class HealthProblem {
        -string description
        -datetime createdAt
        -ProblemStatus status
    }
    class ProblemStatus {
        <<enumeration>>
        PENDING
        IN_REVIEW
        RESOLVED
    }
    class Prescription {
        -string text
        -datetime createdAt
    }
    class Payment {
        <<abstract>>
        -float amount
        -datetime date
        +process()
    }
    class CheckPayment {
        -string checkNumber
    }
    class CashPayment
    class CreditCardPayment {
        -string last4Digits
    }

    User <|-- Patient
    User <|-- Doctor
    User <|-- Organizer
    Payment <|-- CheckPayment
    Payment <|-- CashPayment
    Payment <|-- CreditCardPayment

    Organizer "1" --> "0..*" Patient : registers
    Organizer "1" --> "0..*" Doctor : registers
    Patient "1" --> "0..*" HealthProblem : posts
    HealthProblem "0..*" --> "0..1" Doctor : reviewed by
    HealthProblem "1" --> "0..1" Prescription : answered by
    Doctor "1" --> "0..*" Prescription : writes
    Prescription "1" --> "0..*" Payment : is paid by
    Patient "1" --> "0..*" Payment : makes
    Doctor "1" --> "0..*" Payment : receives
    HealthProblem --> ProblemStatus
```

### Sequence diagram (Task 2: submit a problem, receive a prescription, pay)

```mermaid
sequenceDiagram
    actor P as Patient
    participant O as Organizer
    actor D as Doctor
    P->>O: postProblem(description)
    Note over O: status = PENDING
    O->>D: consult(problem)
    Note over D: status = IN_REVIEW
    D-->>O: writePrescription(problem)
    Note over D: status = RESOLVED
    O->>P: sendPrescription(prescription)
    P->>O: pay(payment)
    O->>O: process payment (check, cash or card)
    O->>D: forwardPayment(payment)
```

## Exo 2: ABCD Records

### Use case diagram (Level 1 and 2)

```mermaid
flowchart LR
    M([Member])
    NM([Non-Member])
    OPC([Order Processing Clerk])
    CDC([Collection Department Clerk])

    subgraph sys["ABCD Records System"]
        PO((Place Order))
        VM((Verify Membership))
        VA((Verify Item Availability))
        PR((Process Order))
        AD((Apply Discount))
        PI((Print Invoice))
        PS((Print Shipping List))
        OU((Order Unavailable Items))
        SA((Send Membership Application))
        MP((Make Payment))
    end

    M --- PO
    M --- MP
    NM --- SA
    OPC --- VM
    OPC --- PR
    OPC --- SA
    CDC --- MP

    PO -. "include" .-> VM
    PO -. "include" .-> VA
    PR -. "include" .-> AD
    PR -. "include" .-> PI
    PR -. "include" .-> PS
    OU -. "extend" .-> PO
    SA -. "extend" .-> VM
```

### Class diagram (Level 1 and 2)

```mermaid
classDiagram
    class Member {
        <<abstract>>
        -int id
        -string name
        -string address
        +placeOrder()
        +discountRate()*
        +canOrderUnavailable()*
    }
    class RoyalMember
    class RegularMember
    class NonMember {
        -string name
        -string address
        +applyForMembership()
    }
    class MembershipApplication {
        -date sentDate
        -string status
    }
    class Item {
        <<abstract>>
        -int id
        -string title
        -string artist
        -float price
        -int stock
        +isAvailable()
    }
    class CD
    class Tape
    class Order {
        -date orderDate
        -string status
        +addLine()
        +total()
    }
    class OrderLine {
        -int quantity
        -boolean backordered
        +subtotal()
    }
    class Invoice {
        -float amount
        -boolean paid
        +print()
    }
    class ShippingList {
        -date shipDate
        +print()
    }
    class Payment {
        <<abstract>>
        -float amount
        +process()*
    }
    class Cash
    class Check {
        -string checkNumber
    }
    class BankDraft {
        -string draftNumber
    }
    class OrderProcessingClerk {
        +verifyMembership()
        +processOrder()
        +saveToDailyRecords()
    }
    class CollectionDepartmentClerk {
        +collectPayment()
    }

    Member <|-- RoyalMember
    Member <|-- RegularMember
    Item <|-- CD
    Item <|-- Tape
    Payment <|-- Cash
    Payment <|-- Check
    Payment <|-- BankDraft

    Member "1" --> "0..*" Order : places
    Order "1" *-- "1..*" OrderLine : contains
    OrderLine "*" --> "1" Item : refers to
    Order "1" --> "0..1" Invoice : billed by
    Order "1" --> "0..1" ShippingList : shipped with
    Invoice "1" --> "0..*" Payment : paid by
    OrderProcessingClerk "1" --> "0..*" Order : processes
    CollectionDepartmentClerk "1" --> "0..*" Payment : collects
    NonMember "1" --> "0..*" MembershipApplication : receives
```
