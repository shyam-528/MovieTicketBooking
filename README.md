# CineDesk — Movie Ticket Booking Management System

A complete Python desktop project for Batch 9. It uses the exact widget types requested in the assignment: an **OptionMenu**, **Radiobuttons**, and a **Listbox**.

## Run on Windows

1. Extract the ZIP to a writable folder.
2. Install Python 3.10 or newer with **Tkinter/Tcl-Tk** and **Add Python to PATH** enabled if Python is not already installed.
3. Double-click `Start_CineDesk.bat`, or open a terminal in this folder and run:

```console
python main.py
```

No pip packages, internet connection, database server, or account are required. If `python` is unavailable but the Windows launcher is installed, use `py main.py`. A desktop display with at least 1000 × 860 usable pixels is recommended.

## Features

- Add, search by Booking ID, update, cancel, and display all bookings.
- Required Booking ID, customer name, movie name, and positive integer ticket count.
- Four show timings and Standard, Premium, and VIP ticket categories.
- SQLite persistence, duplicate-ID protection, and confirmation before cancellation.
- Automatic total calculation, booking statistics, and CSV export.
- Keyboard shortcuts: Ctrl+N for a new form, Ctrl+F for search.

## Quick demonstration

1. Enter `BK001`, `Shyam S`, `Interstellar`, and `2` tickets.
2. Choose `05:00 PM` and `Premium`. The total is **Rs. 500**.
3. Click **Add booking**. The record appears in the Listbox.
4. Click **New / Clear**, type `bk001` in the search field, and click **Search ID**.
5. Change the ticket count to `3`; click **Update booking**. The total becomes **Rs. 750**.
6. Close and reopen the application to show that the record persists.
7. Export all records to CSV.
8. Select the record and click **Cancel booking**, then confirm. The record disappears.
9. Demonstrate validation with a blank customer name, duplicate ID, and ticket counts `0`, `-1`, and `2.5`.

Selecting a saved booking locks its ID to prevent accidental updates to another record. Use **New / Clear** to enter a different ID. Cancellation permanently deletes the record after confirmation. Editing the form does not save changes until Add or Update is clicked.

## Files

| File | Purpose |
|---|---|
| `main.py` | Tkinter interface and event handlers |
| `booking_store.py` | Validation, booking model, and SQLite operations |
| `Start_CineDesk.bat` | Windows launcher |
| `PROJECT_REPORT.md` | Project explanation, design, algorithms, and viva questions |
| `tests/test_bookings.py` | Storage and validation tests |
| `tests/test_ui.py` | GUI workflow integration test |
| `preview.png` | Actual interface with temporary demonstration records |

## Data and customization

The first launch creates `data/bookings.db`. Data stays on your computer. Back up this file while the app is closed; CSV is an export, not a restorable database backup. The delivered project starts with an empty database. Screenshot records are illustrative.

Show timings and demo prices are defined in `SHOW_TIMES` and `PRICES` in `booking_store.py`. Existing totals are calculated using the current category prices, so changing those constants also changes displayed historical totals. For isolated testing, choose another database:

```console
python main.py --database data/demo.db
```

## Tests

```console
python -m unittest discover -s tests -v
```

The GUI test requires a desktop display. To run only storage tests on a machine without a display:

```console
python -m unittest discover -s tests -p test_bookings.py -v
```

## Scope

This is an academic local booking manager. Prices are illustrative INR values. It does not process payments, assign seats, check theatre capacity, schedule dates, authenticate users, or synchronize between computers. It is intended to demonstrate Tkinter widgets, CRUD operations, validation, and persistent storage.
