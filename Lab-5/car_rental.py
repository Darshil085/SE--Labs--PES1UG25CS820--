"""Demonstration car rental system with safer input handling."""

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

# Global rental state.
fleet = {}
bookings = []

conn = sqlite3.connect(":memory:")
conn.execute(
    "CREATE TABLE customers "
    "(name TEXT NOT NULL, licence TEXT NOT NULL, phone TEXT NOT NULL)"
)

ADMIN_USERNAME = "admin"
PROMO_DISCOUNTS = {"SAVE10": 0.10}


def add_car(plate, model="Unknown", daily_rate=0, features=None):
    """Add a car to the fleet after validating its details."""
    if not is_valid_plate(plate):
        raise ValueError("Invalid number plate.")
    if not isinstance(daily_rate, (int, float)) or daily_rate < 0:
        raise ValueError("Daily rate must be non-negative.")

    car_features = list(features) if features is not None else []
    fleet[plate] = {
        "model": model,
        "rate": daily_rate,
        "available": True,
        "features": car_features,
    }
    return fleet[plate]


def register_customer(name, licence, phone):
    """Register a customer using a parameterized SQL statement."""
    if not all(
        isinstance(value, str) and value.strip()
        for value in (name, licence, phone)
    ):
        raise ValueError("Name, licence and phone are required.")

    conn.execute(
        "INSERT INTO customers (name, licence, phone) VALUES (?, ?, ?)",
        (name.strip(), licence.strip(), phone.strip()),
    )


def find_customer(name):
    """Find customers by exact name without executing user input."""
    return conn.execute(
        "SELECT name, licence, phone FROM customers WHERE name = ?",
        (name,),
    ).fetchall()


def rent_car(plate, customer, start, end):
    """Book an available car for a registered customer."""
    if plate not in fleet:
        raise ValueError("Unknown car.")
    if not fleet[plate]["available"]:
        raise ValueError("Car is not available.")
    if not find_customer(customer):
        raise ValueError("Customer not registered.")

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError("Dates must use YYYY-MM-DD format.") from error

    days = (end_date - start_date).days
    if days <= 0:
        raise ValueError("End date must be after start date.")

    cost = days * fleet[plate]["rate"]
    booking = {
        "code": booking_code(),
        "plate": plate,
        "customer": customer,
        "start": start,
        "end": end,
        "days": days,
        "cost": cost,
    }
    bookings.append(booking)
    fleet[plate]["available"] = False
    return cost


def return_car(plate, km_driven):
    """Return a known car and calculate the excess-kilometre charge."""
    if plate not in fleet:
        raise ValueError("Unknown car.")
    if not isinstance(km_driven, (int, float)) or km_driven < 0:
        raise ValueError("Kilometres must be non-negative.")

    fleet[plate]["available"] = True
    return max(0, km_driven - 300) * 5


def booking_code():
    """Generate a booking reference using a secure random source."""
    return f"BK-{secrets.token_hex(4).upper()}"


def licence_hash(licence):
    """Return a SHA-256 digest of a licence string."""
    return hashlib.sha256(licence.encode("utf-8")).hexdigest()


def apply_promo(rule, amount):
    """Apply an approved promo code without executing arbitrary code."""
    if not isinstance(amount, (int, float)) or amount < 0:
        raise ValueError("Amount must be non-negative.")
    if rule not in PROMO_DISCOUNTS:
        raise ValueError("Unknown promo code.")
    return amount * (1 - PROMO_DISCOUNTS[rule])


def is_valid_plate(plate):
    """Check whether a plate matches the expected format."""
    return bool(
        re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}", plate)
    )


def write_receipt(booking):
    """Write a receipt to a securely created temporary file."""
    receipt_text = (
        f"Booking {booking['code']}: {booking['plate']} for "
        f"{booking['days']} days = Rs.{booking['cost']:.2f}\n"
    )

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".txt",
        prefix="car_rental_receipt_",
        delete=False,
    ) as receipt:
        receipt.write(receipt_text)
        path = Path(receipt.name)

    try:
        path.chmod(0o600)
    except OSError:
        # Some platforms do not support POSIX permission bits.
        pass

    return str(path)


def admin_login(user, password=None):
    """Authenticate against a password supplied through the environment."""
    expected_password = os.environ.get("CAR_RENTAL_ADMIN_PASSWORD")

    if not expected_password or user != ADMIN_USERNAME or password is None:
        return False

    # Compare password-derived values without a direct string comparison.
    salt = b"car-rental-demo-salt"
    supplied_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 200_000
    )
    expected_hash = hashlib.pbkdf2_hmac(
        "sha256", expected_password.encode("utf-8"), salt, 200_000
    )
    return hmac.compare_digest(supplied_hash, expected_hash)


def available_cars():
    """Return the number plates of all available cars."""
    return [
        plate for plate, car in fleet.items()
        if car["available"]
    ]


def main():
    """Run a demonstration of the car rental functions."""
    add_car("KA01AB1234", "Swift", 1500)
    add_car("KA02CD5678", "Innova", 3000)
    add_car("KA03EF9999", "Nexon", 500)

    register_customer("Ravi", "DL-0420110012345", "9845012345")
    register_customer("Meera", "DL-0420110099999", "9845099999")

    print(
        "Rent Swift:",
        rent_car("KA01AB1234", "Ravi", "2026-11-01", "2026-11-04"),
    )
    print("Lookup injection:", find_customer("x' OR '1'='1"))
    print("Extra km charge:", return_car("KA01AB1234", 420))
    print("Promo price:", apply_promo("SAVE10", 4500))
    print("Plate valid?", is_valid_plate("KA01AB1234"))
    print("Licence hash:", licence_hash("DL-0420110012345"))
    print("Admin:", admin_login("admin"))
    print("Available:", available_cars())
    print("Receipt saved to:", write_receipt(bookings[0]))


if __name__ == "__main__":
    main()
