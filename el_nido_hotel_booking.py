"""
El Nido Paradise Hotel — Booking System
El Nido, Palawan, Philippines
"""

from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────

@dataclass
class Room:
    room_number: str
    room_type: str          # "standard", "deluxe", "suite"
    rate_per_night: float
    is_available: bool = True
    max_guests: int = 2


@dataclass
class Guest:
    name: str
    email: str
    phone: str
    guest_id: str = field(default_factory=lambda: str(uuid4())[:8])


@dataclass
class Booking:
    guest: Guest
    room: Room
    check_in: date
    check_out: date
    booking_id: str = field(default_factory=lambda: str(uuid4())[:8])

    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days


# ─────────────────────────────────────────
# BOOKING ENGINE
# ─────────────────────────────────────────

class BookingEngine:
    def __init__(self):
        self.bookings: list[Booking] = []

    def make_booking(self, guest: Guest, room: Room,
                     check_in: date, check_out: date) -> Booking:
        if not room.is_available:
            raise ValueError(f"Room {room.room_number} is not available.")
        if check_out <= check_in:
            raise ValueError("Check-out must be after check-in.")

        booking = Booking(guest, room, check_in, check_out)
        room.is_available = False
        self.bookings.append(booking)
        return booking

    def cancel_booking(self, booking_id: str) -> None:
        for booking in self.bookings:
            if booking.booking_id == booking_id:
                booking.room.is_available = True
                self.bookings.remove(booking)
                return
        raise ValueError(f"Booking ID {booking_id!r} not found.")

    def find_booking(self, booking_id: str) -> Booking | None:
        return next(
            (b for b in self.bookings if b.booking_id == booking_id), None
        )

    def list_bookings(self) -> None:
        if not self.bookings:
            print("  Walang aktibong booking.")
            return
        for b in self.bookings:
            print(f"  [{b.booking_id}] {b.guest.name} — Room {b.room.room_number} "
                  f"({b.check_in} to {b.check_out}, {b.nights} nights)")


# ─────────────────────────────────────────
# PRICING & BILLING
# ─────────────────────────────────────────

PEAK_MONTHS = {12, 1, 2, 3}   # December–March: El Nido high season


def seasonal_rate(booking: Booking) -> float:
    month = booking.check_in.month
    multiplier = 1.3 if month in PEAK_MONTHS else 1.0
    return booking.room.rate_per_night * multiplier


def calculate_total(booking: Booking, discount: float = 0.0) -> float:
    nightly = seasonal_rate(booking)
    subtotal = nightly * booking.nights
    return round(subtotal * (1 - discount), 2)


def print_receipt(booking: Booking, discount: float = 0.0) -> None:
    nightly = seasonal_rate(booking)
    total = calculate_total(booking, discount)
    peak = booking.check_in.month in PEAK_MONTHS

    print(f"\n{'='*42}")
    print(f"   El Nido Paradise Hotel — Receipt")
    print(f"{'='*42}")
    print(f"  Booking ID : {booking.booking_id}")
    print(f"  Guest      : {booking.guest.name}")
    print(f"  Email      : {booking.guest.email}")
    print(f"  Phone      : {booking.guest.phone}")
    print(f"  Room       : {booking.room.room_number} ({booking.room.room_type})")
    print(f"  Check-in   : {booking.check_in}")
    print(f"  Check-out  : {booking.check_out}  ({booking.nights} nights)")
    print(f"  Rate/night : PHP {nightly:,.2f}" + (" [peak season]" if peak else ""))
    if discount:
        print(f"  Discount   : {discount*100:.0f}%")
    print(f"  {'─'*38}")
    print(f"  TOTAL      : PHP {total:,.2f}")
    print(f"{'='*42}\n")


# ─────────────────────────────────────────
# ROOM CATALOG
# ─────────────────────────────────────────

ROOMS: list[Room] = [
    Room("101", "standard", 3_500, max_guests=2),
    Room("102", "standard", 3_500, max_guests=2),
    Room("201", "deluxe",   5_500, max_guests=3),
    Room("202", "deluxe",   5_500, max_guests=3),
    Room("301", "suite",    9_800, max_guests=4),
]


def show_rooms() -> None:
    print(f"\n  {'No.':<6} {'Type':<12} {'Rate/night':>12}  {'Status'}")
    print(f"  {'─'*44}")
    for room in ROOMS:
        status = "✓ Available" if room.is_available else "✗ Booked"
        print(f"  {room.room_number:<6} {room.room_type:<12} PHP {room.rate_per_night:>8,.0f}  {status}")
    print()


def get_room(room_no: str) -> Room | None:
    return next((r for r in ROOMS if r.room_number == room_no), None)


# ─────────────────────────────────────────
# CLI
# ─────────────────────────────────────────

engine = BookingEngine()


def menu_make_booking() -> None:
    print("\n--- Bagong Booking ---")
    name  = input("  Pangalan ng bisita : ").strip()
    email = input("  Email              : ").strip()
    phone = input("  Phone              : ").strip()
    guest = Guest(name, email, phone)

    show_rooms()
    room_no = input("  Room number        : ").strip()
    room = get_room(room_no)
    if not room:
        print("  Room hindi nahanap.")
        return

    try:
        check_in  = date.fromisoformat(input("  Check-in  (YYYY-MM-DD) : ").strip())
        check_out = date.fromisoformat(input("  Check-out (YYYY-MM-DD) : ").strip())
    except ValueError:
        print("  Mali ang format ng petsa. Gamitin ang YYYY-MM-DD.")
        return

    try:
        booking = engine.make_booking(guest, room, check_in, check_out)
        print(f"\n  Booking confirmed! ID: {booking.booking_id}")
        print_receipt(booking)
    except ValueError as e:
        print(f"  Error: {e}")


def menu_cancel_booking() -> None:
    print("\n--- I-cancel ang Booking ---")
    engine.list_bookings()
    bid = input("\n  Booking ID na i-cancel: ").strip()
    try:
        engine.cancel_booking(bid)
        print("  Booking successfully cancelled.")
    except ValueError as e:
        print(f"  Error: {e}")


def menu_view_booking() -> None:
    print("\n--- Tingnan ang Booking ---")
    bid = input("  Booking ID: ").strip()
    booking = engine.find_booking(bid)
    if booking:
        print_receipt(booking)
    else:
        print("  Booking hindi nahanap.")


def run() -> None:
    print("\n" + "="*42)
    print("   El Nido Paradise Hotel")
    print("   El Nido, Palawan, Philippines 🌴")
    print("="*42)

    while True:
        print("\n  1. Tingnan ang mga kwarto")
        print("  2. Mag-book ng kwarto")
        print("  3. I-cancel ang booking")
        print("  4. Tingnan ang lahat ng booking")
        print("  5. Hanapin ang booking")
        print("  6. Lumabas")

        choice = input("\n  Piliin (1-6): ").strip()

        if choice == "1":
            show_rooms()
        elif choice == "2":
            menu_make_booking()
        elif choice == "3":
            menu_cancel_booking()
        elif choice == "4":
            print("\n--- Lahat ng Booking ---")
            engine.list_bookings()
        elif choice == "5":
            menu_view_booking()
        elif choice == "6":
            print("\n  Salamat! Kita-kits sa El Nido! 🌊\n")
            break
        else:
            print("  Mali ang pinili. Subukang muli.")


# ─────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────

if __name__ == "__main__":
    run()
