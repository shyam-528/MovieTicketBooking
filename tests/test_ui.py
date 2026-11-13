"""Integration test: requires a desktop display; dialogs are mocked."""
import sys
from pathlib import Path
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import BookingApp


class InterfaceTests(unittest.TestCase):
    def test_form_search_update_export_cancel(self):
        with tempfile.TemporaryDirectory() as directory:
            root = tk.Tk()
            root.withdraw()
            app = BookingApp(root, Path(directory) / 'test.db')
            try:
                with patch('main.messagebox.showwarning') as warning, patch('main.messagebox.showerror') as error:
                    app.vars['booking_id'].set('BK001')
                    app.vars['customer_name'].set('Shyam S')
                    app.vars['movie_name'].set('Interstellar')
                    app.vars['tickets'].set('2')
                    app.add()
                    self.assertEqual(app.listbox.size(), 1)
                    self.assertEqual(app.store.get('BK001').total, 300)
                    app.clear()
                    app.query.set('bk001')
                    app.search()
                    self.assertEqual(app.vars['movie_name'].get(), 'Interstellar')
                    app.vars['tickets'].set('3')
                    app.update()
                    self.assertEqual(app.store.get('BK001').tickets, 3)
                    export = Path(directory) / 'export.csv'
                    with patch('main.filedialog.asksaveasfilename', return_value=str(export)):
                        app.export()
                    self.assertIn('BK001', export.read_text(encoding='utf-8-sig'))
                    with patch('main.messagebox.askyesno', return_value=False):
                        app.cancel()
                    self.assertEqual(len(app.store.all()), 1)
                    with patch('main.messagebox.askyesno', return_value=True):
                        app.cancel()
                    self.assertEqual(app.listbox.size(), 0)
                    warning.assert_not_called()
                    error.assert_not_called()
                    app.vars['tickets'].set('-1')
                    app.add()
                    warning.assert_called_once()
            finally:
                app.close()


if __name__ == '__main__':
    unittest.main()
