"""Validation and SQLite storage, independent of the graphical interface."""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3

SHOW_TIMES = ('10:00 AM', '01:30 PM', '05:00 PM', '08:30 PM')
PRICES = {'Standard': 150, 'Premium': 250, 'VIP': 400}


@dataclass(frozen=True)
class Booking:
    booking_id: str
    customer_name: str
    movie_name: str
    tickets: int
    show_time: str
    category: str

    @property
    def total(self):
        return self.tickets * PRICES[self.category]


def validate_booking(booking_id, customer_name, movie_name, tickets, show_time, category):
    booking_id = str(booking_id).strip().upper()
    customer_name = str(customer_name).strip()
    movie_name = str(movie_name).strip()
    if not booking_id:
        raise ValueError('Booking ID is required.')
    if len(booking_id) > 30 or not all(c.isascii() and (c.isalnum() or c in '-_') for c in booking_id):
        raise ValueError('Booking ID must use 1–30 letters, digits, hyphens or underscores.')
    if not customer_name:
        raise ValueError('Customer name is required.')
    if not movie_name:
        raise ValueError('Movie name is required.')
    if any(len(value) > 100 or any(ord(c) < 32 for c in value) for value in (customer_name, movie_name)):
        raise ValueError('Names must be at most 100 characters and contain no control characters.')
    raw = str(tickets).strip()
    if not raw.isascii() or not raw.isdecimal() or len(raw) > 9 or int(raw) <= 0:
        raise ValueError('Number of tickets must be a positive whole number (maximum 999,999,999).')
    if show_time not in SHOW_TIMES:
        raise ValueError('Choose a valid show timing.')
    if category not in PRICES:
        raise ValueError('Choose a valid ticket category.')
    return Booking(booking_id, customer_name, movie_name, int(raw), show_time, category)


class BookingStore:
    def __init__(self, path):
        if str(path) != ':memory:':
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute('''CREATE TABLE IF NOT EXISTS bookings (
            booking_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            movie_name TEXT NOT NULL,
            tickets INTEGER NOT NULL CHECK(tickets > 0),
            show_time TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        )''')
        self.connection.commit()

    @staticmethod
    def _values(booking):
        checked = validate_booking(booking.booking_id, booking.customer_name, booking.movie_name,
                                   booking.tickets, booking.show_time, booking.category)
        return (checked.booking_id, checked.customer_name, checked.movie_name,
                checked.tickets, checked.show_time, checked.category)

    def add(self, booking):
        values = self._values(booking)
        try:
            with self.connection:
                self.connection.execute('INSERT INTO bookings VALUES (?, ?, ?, ?, ?, ?, ?)',
                                        (*values, datetime.now().isoformat(timespec='seconds')))
        except sqlite3.IntegrityError as exc:
            raise ValueError('This Booking ID already exists. Use another ID or search and update it.') from exc

    def get(self, booking_id):
        row = self.connection.execute('SELECT * FROM bookings WHERE booking_id = ?',
                                      (booking_id.strip().upper(),)).fetchone()
        return self._booking(row) if row else None

    def update(self, booking):
        values = self._values(booking)
        with self.connection:
            cursor = self.connection.execute('''UPDATE bookings SET customer_name=?, movie_name=?,
                tickets=?, show_time=?, category=? WHERE booking_id=?''', (*values[1:], values[0]))
            if cursor.rowcount == 0:
                raise ValueError('Booking not found. Search an existing Booking ID before updating.')

    def cancel(self, booking_id):
        with self.connection:
            cursor = self.connection.execute('DELETE FROM bookings WHERE booking_id=?',
                                              (booking_id.strip().upper(),))
            if cursor.rowcount == 0:
                raise ValueError('Booking not found.')

    def all(self):
        rows = self.connection.execute('SELECT * FROM bookings ORDER BY created_at DESC, booking_id ASC').fetchall()
        return [self._booking(row) for row in rows]

    @staticmethod
    def _booking(row):
        return Booking(*(row[key] for key in ('booking_id', 'customer_name', 'movie_name',
                                             'tickets', 'show_time', 'category')))

    def close(self):
        self.connection.close()
