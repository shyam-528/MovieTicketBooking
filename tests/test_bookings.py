import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from booking_store import Booking, BookingStore, validate_booking


class BookingTests(unittest.TestCase):
    def setUp(self):
        self.store = BookingStore(':memory:')
        self.booking = validate_booking('bk001', 'Shyam S', 'Interstellar', '2', '05:00 PM', 'Premium')

    def tearDown(self):
        self.store.close()

    def test_complete_booking_lifecycle(self):
        self.store.add(self.booking)
        self.assertEqual(self.store.get(' bk001 '), self.booking)
        self.assertEqual(self.store.all(), [self.booking])
        changed = Booking('BK001', 'Shyam S', 'Inception', 3, '08:30 PM', 'VIP')
        self.store.update(changed)
        self.assertEqual(self.store.get('BK001').total, 1200)
        self.assertEqual(self.store.get('BK001').movie_name, 'Inception')
        self.store.cancel('bk001')
        self.assertIsNone(self.store.get('BK001'))
        self.assertEqual(self.store.all(), [])

    def test_duplicate_preserves_existing_record(self):
        self.store.add(self.booking)
        with self.assertRaises(ValueError):
            self.store.add(self.booking)
        self.assertEqual(self.store.all(), [self.booking])

    def test_invalid_ticket_counts(self):
        for tickets in ('', '0', '-1', '2.5', 'abc', '1e3', '²', '1000000000'):
            with self.subTest(tickets=tickets), self.assertRaises(ValueError):
                validate_booking('BK1', 'A', 'Movie', tickets, '10:00 AM', 'Standard')

    def test_required_and_selection_fields(self):
        values = ['BK1', 'Name', 'Movie', '1', '10:00 AM', 'Standard']
        for index in (0, 1, 2, 4, 5):
            changed = values.copy()
            changed[index] = ' '
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate_booking(*changed)

    def test_missing_update_and_cancel(self):
        with self.assertRaises(ValueError):
            self.store.update(self.booking)
        with self.assertRaises(ValueError):
            self.store.cancel('missing')

    def test_parameterized_sql_handles_apostrophes(self):
        booking = validate_booking('BK2', "O'Brien", "Movie'); DROP TABLE bookings; --", '1', '10:00 AM', 'Standard')
        self.store.add(booking)
        self.assertEqual(self.store.get('BK2'), booking)
        self.store.add(self.booking)
        self.assertEqual(len(self.store.all()), 2)

    def test_store_revalidates_direct_dataclass_input(self):
        with self.assertRaises(ValueError):
            self.store.add(Booking('BK1', '', 'Movie', 0, 'wrong', 'wrong'))

    def test_data_survives_reopening(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bookings.db'
            first = BookingStore(path)
            first.add(self.booking)
            first.close()
            second = BookingStore(path)
            self.assertEqual(second.get('BK001'), self.booking)
            second.close()


if __name__ == '__main__':
    unittest.main()
