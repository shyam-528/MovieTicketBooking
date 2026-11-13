"""CineDesk — run with: python main.py (Python 3.10+ with Tkinter)."""
import argparse
import csv
from pathlib import Path
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from booking_store import BookingStore, PRICES, SHOW_TIMES, validate_booking

ROOT = Path(__file__).resolve().parent
BG = '#f3f5fa'
INK = '#18233b'
MUTED = '#65728a'
ACCENT = '#5c43d6'


def configure_display():
    """Keep Windows coordinates and drawing consistent on scaled displays."""
    import sys
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()


class BookingApp:
    def __init__(self, root, database):
        self.root = root
        root.tk.call('tk', 'scaling', 1.2)
        self.store = BookingStore(database)
        self.rows = []
        self.loaded_id = None
        self.vars = {key: tk.StringVar() for key in
                     ('booking_id', 'customer_name', 'movie_name', 'tickets', 'show_time', 'category')}
        self.query = tk.StringVar()
        self.status = tk.StringVar(value='Ready. Create a booking or search by Booking ID.')
        self.total = tk.StringVar()
        root.title('CineDesk | Movie Ticket Booking Management System')
        root.geometry('1180x860+40+40')
        root.minsize(1000, 820)
        root.configure(bg=BG)
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TFrame', background=BG)
        style.configure('Card.TFrame', background='white')
        style.configure('TLabel', background='white', foreground=INK, font=('Segoe UI', 10))
        style.configure('Muted.TLabel', foreground=MUTED)
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('TEntry', padding=8, font=('Segoe UI', 11))
        style.configure('TButton', padding=(12, 9), font=('Segoe UI', 10))
        style.configure('Primary.TButton', background=ACCENT, foreground='white')
        style.map('Primary.TButton', background=[('active', '#4930b8')])
        style.configure('Danger.TButton', foreground='#b32949')
        style.configure('TRadiobutton', background='white', font=('Segoe UI', 10))
        self._build()
        self.vars['tickets'].trace_add('write', self._total)
        self.vars['category'].trace_add('write', self._total)
        self.clear()
        self.refresh()
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.bind('<Control-f>', lambda event: self.search_entry.focus_set())
        root.bind('<Control-n>', lambda event: self.clear())

    def _build(self):
        header = tk.Frame(self.root, bg=INK, padx=28, pady=20)
        header.pack(fill='x')
        tk.Label(header, text='CINEDESK', bg=INK, fg='white', font=('Segoe UI', 24, 'bold')).pack(anchor='w')
        tk.Label(header, text='Movie Ticket Booking Management System  /  Batch 9',
                 bg=INK, fg='#c7cee0', font=('Segoe UI', 10)).pack(anchor='w', pady=(3, 0))
        self.stats = tk.StringVar()
        tk.Label(self.root, textvariable=self.stats, bg=BG, fg=MUTED,
                 font=('Segoe UI', 11), anchor='w', padx=28, pady=16).pack(fill='x')
        body = ttk.Frame(self.root, padding=(24, 0, 24, 12))
        body.pack(fill='both', expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        form = ttk.Frame(body, style='Card.TFrame', padding=22)
        form.grid(row=0, column=0, sticky='ns', padx=(0, 18))
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text='Booking details', style='Title.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(form, text='* Required fields', style='Muted.TLabel').grid(row=1, column=0, sticky='w', pady=(3, 12))
        labels = [('booking_id', 'Booking ID *'), ('customer_name', 'Customer name *'),
                  ('movie_name', 'Movie name *'), ('tickets', 'Number of tickets *')]
        for index, (key, label) in enumerate(labels):
            row = 2 + index * 2
            ttk.Label(form, text=label).grid(row=row, column=0, sticky='w', pady=(5, 4))
            entry = ttk.Entry(form, textvariable=self.vars[key], width=33)
            entry.grid(row=row + 1, column=0, sticky='ew')
            if key == 'booking_id':
                self.id_entry = entry
        ttk.Label(form, text='Show timing').grid(row=10, column=0, sticky='w', pady=(12, 4))
        # The assignment specifically requires an OptionMenu.
        self.show_menu = tk.OptionMenu(form, self.vars['show_time'], *SHOW_TIMES)
        self.show_menu.configure(bg='#eef0f8', fg=INK, relief='flat', highlightthickness=0,
                                 anchor='w', font=('Segoe UI', 10), padx=10, pady=7)
        self.show_menu.grid(row=11, column=0, sticky='ew')
        ttk.Label(form, text='Ticket category').grid(row=12, column=0, sticky='w', pady=(12, 4))
        categories = ttk.Frame(form, style='Card.TFrame')
        categories.grid(row=13, column=0, sticky='w')
        for index, (category, price) in enumerate(PRICES.items()):
            ttk.Radiobutton(categories, text=f'{category}\nRs. {price}', value=category,
                            variable=self.vars['category']).grid(row=0, column=index, padx=(0, 9), sticky='w')
        ttk.Label(form, textvariable=self.total, font=('Segoe UI', 14, 'bold'),
                  foreground=ACCENT).grid(row=14, column=0, sticky='w', pady=14)
        actions = ttk.Frame(form, style='Card.TFrame')
        actions.grid(row=15, column=0, sticky='ew')
        actions.columnconfigure((0, 1), weight=1)
        ttk.Button(actions, text='Add booking', style='Primary.TButton', command=self.add).grid(row=0, column=0, sticky='ew', padx=(0, 6))
        ttk.Button(actions, text='Update booking', command=self.update).grid(row=0, column=1, sticky='ew')
        ttk.Button(actions, text='New / Clear', command=self.clear).grid(row=1, column=0, sticky='ew', padx=(0, 6), pady=(8, 0))
        ttk.Button(actions, text='Cancel booking', style='Danger.TButton', command=self.cancel).grid(row=1, column=1, sticky='ew', pady=(8, 0))
        panel = ttk.Frame(body, style='Card.TFrame', padding=22)
        panel.grid(row=0, column=1, sticky='nsew')
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(4, weight=1)
        ttk.Label(panel, text='Booking register', style='Title.TLabel').grid(row=0, column=0, sticky='w')
        ttk.Label(panel, text='Search an ID or select a booking to view and edit.',
                  style='Muted.TLabel').grid(row=1, column=0, sticky='w', pady=(4, 14))
        search = ttk.Frame(panel, style='Card.TFrame')
        search.grid(row=2, column=0, sticky='ew')
        search.columnconfigure(0, weight=1)
        self.search_entry = ttk.Entry(search, textvariable=self.query, width=20)
        self.search_entry.grid(row=0, column=0, sticky='ew', padx=(0, 8))
        self.search_entry.bind('<Return>', lambda event: self.search())
        ttk.Button(search, text='Search ID', command=self.search).grid(row=0, column=1)
        ttk.Button(search, text='Show all', command=self.show_all).grid(row=0, column=2, padx=(8, 0))
        ttk.Label(panel, text='ID  /  CUSTOMER  /  MOVIE  /  TICKETS  /  SHOW  /  CATEGORY  /  TOTAL',
                  font=('Segoe UI', 8, 'bold'), foreground=MUTED).grid(row=3, column=0, sticky='w', pady=(18, 8))
        listing = ttk.Frame(panel, style='Card.TFrame')
        listing.grid(row=4, column=0, sticky='nsew')
        listing.columnconfigure(0, weight=1)
        listing.rowconfigure(0, weight=1)
        # A real Listbox is used, as required by the assignment.
        self.listbox = tk.Listbox(listing, font=('Consolas', 11), bg='#f8f9fd', fg=INK,
                                  selectbackground=ACCENT, selectforeground='white',
                                  relief='flat', highlightthickness=0, activestyle='none',
                                  exportselection=False, width=45, height=12)
        self.listbox.grid(row=0, column=0, sticky='nsew')
        vertical = ttk.Scrollbar(listing, orient='vertical', command=self.listbox.yview)
        vertical.grid(row=0, column=1, sticky='ns')
        horizontal = ttk.Scrollbar(listing, orient='horizontal', command=self.listbox.xview)
        horizontal.grid(row=1, column=0, sticky='ew')
        self.listbox.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.listbox.bind('<<ListboxSelect>>', self.select)
        self.detail = tk.StringVar(value='No booking selected.')
        ttk.Label(panel, textvariable=self.detail, wraplength=460,
                  style='Muted.TLabel').grid(row=5, column=0, sticky='w', pady=14)
        footer = ttk.Frame(panel, style='Card.TFrame')
        footer.grid(row=6, column=0, sticky='ew')
        ttk.Button(footer, text='Export all to CSV', command=self.export).pack(side='left')
        ttk.Button(footer, text='Project info', command=self.about).pack(side='right')
        tk.Label(self.root, textvariable=self.status, anchor='w', bg='#e7eaf3', fg=INK,
                 padx=24, pady=10, font=('Segoe UI', 10)).pack(side='bottom', fill='x', before=body)

    def _total(self, *_):
        raw = self.vars['tickets'].get().strip()
        valid = raw.isascii() and raw.isdecimal() and len(raw) <= 9 and int(raw) > 0
        amount = int(raw) * PRICES.get(self.vars['category'].get(), 0) if valid else None
        self.total.set(f'Total  Rs. {amount:,}' if amount is not None else 'Total  —')

    def read_form(self):
        return validate_booking(*(self.vars[key].get() for key in self.vars))

    def run_action(self, action):
        try:
            action()
        except ValueError as exc:
            messagebox.showwarning('Check booking details', str(exc), parent=self.root)
            self.status.set(str(exc))
        except (sqlite3.Error, OSError) as exc:
            messagebox.showerror('Operation failed', f'Unable to complete the operation.\n{exc}', parent=self.root)

    def add(self):
        def action():
            booking = self.read_form()
            self.store.add(booking)
            self.refresh()
            self.load(booking)
            self.status.set(f'Booking {booking.booking_id} added and saved successfully.')
        self.run_action(action)

    def update(self):
        def action():
            booking = self.read_form()
            if self.loaded_id != booking.booking_id:
                raise ValueError('Search or select the booking you want to update first. Booking IDs cannot be renamed.')
            self.store.update(booking)
            self.refresh()
            self.load(booking)
            self.status.set(f'Booking {booking.booking_id} updated successfully.')
        self.run_action(action)

    def cancel(self):
        def action():
            booking_id = self.vars['booking_id'].get().strip().upper()
            if not booking_id:
                raise ValueError('Enter or select a Booking ID to cancel.')
            booking = self.store.get(booking_id)
            if not booking:
                raise ValueError('Booking not found.')
            if messagebox.askyesno('Cancel booking?',
                                  f'Delete {booking.booking_id} for {booking.customer_name}?\n'
                                  f'{booking.movie_name} • {booking.tickets} ticket(s)\nThis cannot be undone.', parent=self.root):
                self.store.cancel(booking_id)
                self.clear()
                self.refresh()
                self.status.set(f'Booking {booking_id} cancelled.')
        self.run_action(action)

    def search(self):
        def action():
            booking_id = self.query.get().strip()
            if not booking_id:
                raise ValueError('Enter a Booking ID in the search field.')
            booking = self.store.get(booking_id)
            if not booking:
                raise ValueError(f'No booking found for {booking_id}.')
            self.load(booking)
            self.status.set(f'Found {booking.booking_id}. Details are ready to edit.')
        self.run_action(action)

    def load(self, booking):
        self.loaded_id = booking.booking_id
        for key, variable in self.vars.items():
            variable.set(str(getattr(booking, key)))
        self.id_entry.configure(state='readonly')
        self.detail.set(f'{booking.booking_id} · {booking.customer_name}\n{booking.movie_name}\n'
                        f'{booking.show_time} · {booking.category} · {booking.tickets} ticket(s) · Rs. {booking.total:,}')
        for index, row in enumerate(self.rows):
            if row.booking_id == booking.booking_id:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(index)
                self.listbox.see(index)
                break

    def select(self, _event=None):
        selected = self.listbox.curselection()
        if selected and selected[0] < len(self.rows):
            self.load(self.rows[selected[0]])

    def clear(self):
        self.loaded_id = None
        self.id_entry.configure(state='normal')
        for variable in self.vars.values():
            variable.set('')
        self.vars['tickets'].set('1')
        self.vars['show_time'].set(SHOW_TIMES[0])
        self.vars['category'].set('Standard')
        self.listbox.selection_clear(0, tk.END)
        self.detail.set('No booking selected. Enter details to add a new booking.')
        self.status.set('New booking. Enter a unique Booking ID, such as BK001.')
        self.id_entry.focus_set()
        self._total()

    def refresh(self):
        self.rows = self.store.all()
        self.listbox.delete(0, tk.END)
        for booking in self.rows:
            self.listbox.insert(tk.END, f'{booking.booking_id}  |  {booking.customer_name}  |  {booking.movie_name}'
                                f'  |  {booking.tickets}  |  {booking.show_time}  |  {booking.category}  |  Rs. {booking.total:,}')
        self.stats.set(f'{len(self.rows)} BOOKINGS     •     {sum(b.tickets for b in self.rows)} TICKETS'
                       f'     •     Rs. {sum(b.total for b in self.rows):,} BOOKING VALUE')
        if not self.rows:
            self.detail.set('Your register is empty. Add your first booking using the form.')

    def show_all(self):
        def action():
            self.query.set('')
            self.refresh()
            self.status.set(f'Showing all {len(self.rows)} saved bookings.')
        self.run_action(action)

    def export(self):
        def action():
            rows = self.store.all()
            if not rows:
                raise ValueError('There are no bookings to export.')
            path = filedialog.asksaveasfilename(parent=self.root, title='Export bookings',
                                               defaultextension='.csv', initialfile='bookings.csv',
                                               filetypes=[('CSV files', '*.csv')])
            if not path:
                return
            # Neutralize spreadsheet formula prefixes in user-entered text.
            def safe(value):
                return "'" + value if isinstance(value, str) and value.startswith(('=', '+', '-', '@')) else value
            with open(path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(['Booking ID', 'Customer Name', 'Movie Name', 'Tickets', 'Show Timing', 'Category', 'Total INR'])
                for b in rows:
                    writer.writerow([safe(v) for v in (b.booking_id, b.customer_name, b.movie_name,
                                                       b.tickets, b.show_time, b.category, b.total)])
            self.status.set(f'Exported {len(rows)} bookings to {Path(path).name}.')
        self.run_action(action)

    def about(self):
        messagebox.showinfo('Batch 9 • Project information',
                            'Movie Ticket Booking Management System\n\n'
                            'RA2511003010216 — SHYAM S\n'
                            'RA2511003010217 — K SAISHIVAA\n'
                            'RA2511003010218 — SAAI KIRUTTHK S V\n\n'
                            'Python • Tkinter • SQLite\n'
                            'Demo ticket prices in INR. No payment processing.\n'
                            'Ctrl+N: New booking   |   Ctrl+F: Search', parent=self.root)

    def close(self):
        self.store.close()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description='CineDesk movie booking manager')
    parser.add_argument('--database', type=Path, default=ROOT / 'data' / 'bookings.db')
    args = parser.parse_args()
    configure_display()
    root = tk.Tk()
    try:
        BookingApp(root, args.database)
    except (sqlite3.Error, OSError) as exc:
        messagebox.showerror('Startup failed', f'Cannot open booking database:\n{exc}', parent=root)
        root.destroy()
        return
    root.mainloop()


if __name__ == '__main__':
    main()
