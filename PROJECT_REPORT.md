# Movie Ticket Booking Management System

**Project name:** CineDesk  
**Batch:** 9  
**Technology:** Python, Tkinter, SQLite

| Registration number | Student name |
|---|---|
| RA2511003010216 | SHYAM S |
| RA2511003010217 | K SAISHIVAA |
| RA2511003010218 | SAAI KIRUTTHK S V |

## 1. Abstract

CineDesk is a desktop application for managing movie ticket booking records. Users enter customer and movie details, choose a show timing and ticket category, and create a booking. The application supports searching, updating, cancelling, and displaying bookings. Validation prevents missing information, duplicate identifiers, and invalid ticket quantities. SQLite stores records between application sessions. A graphical interface provides calculated prices, booking statistics, and CSV export.

## 2. Problem statement and objectives

Manual booking registers can contain duplicate identifiers, incomplete customer details, and incorrect ticket quantities. Searching and maintaining such records can become inconvenient. The project provides a consistent form and persistent local database to support these operations.

The objectives are to implement all specified booking operations, use the required selection widgets, validate data before storage, and provide an interface that can be demonstrated without external services.

## 3. Assignment coverage

| Assignment requirement | Implementation |
|---|---|
| Booking ID | Entry field; normalized to uppercase; unique primary key |
| Customer Name | Required Entry field |
| Movie Name | Required Entry field |
| Number of Tickets | Entry field validated as a positive integer |
| OptionMenu for show timing | `tk.OptionMenu` with four show timings |
| RadioButtons for ticket category | `ttk.Radiobutton` for Standard, Premium, and VIP |
| Add a booking | Add booking button and parameterized SQL INSERT |
| Search using Booking ID | Search field and exact, case-normalized ID lookup |
| Update booking details | Search/select, edit, then Update booking |
| Cancel a booking | Confirmation followed by SQL DELETE |
| Display all bookings in a Listbox | `tk.Listbox` with horizontal and vertical scrolling |
| Mandatory ID and customer name | Shared validation before insert/update |
| Positive ticket count | Rejects blank, zero, negative, decimal, and nonnumeric input |

Extra features include database persistence, total calculation, statistics, CSV export, and keyboard shortcuts. The assignment's named widgets remain present.

## 4. Requirements

**Software:** Python 3.10+, Tkinter/Tcl-Tk, and Python's built-in SQLite module. No third-party runtime libraries are needed.  
**Hardware:** A desktop computer capable of running Python and a graphical display with approximately 1000 × 860 usable pixels or more.  
**Storage:** Write access to the project folder or a custom database location.

## 5. Architecture

```text
User
  |
  v
Tkinter interface (main.py)
  | form values / button callbacks
  v
Shared validation + Booking model (booking_store.py)
  |
  v
BookingStore -> SQLite database (data/bookings.db)
  |
  v
Saved records -> Listbox / booking detail / totals
```

`Booking` is an immutable dataclass representing one booking. `validate_booking` normalizes and validates input. `BookingStore` owns database operations. `BookingApp` manages widgets and connects user actions to storage. Keeping validation and database logic separate allows testing without interacting with the GUI.

## 6. Database design

The database has one table, `bookings`.

| Column | SQLite type | Meaning |
|---|---|---|
| booking_id | TEXT PRIMARY KEY | Unique identifier |
| customer_name | TEXT NOT NULL | Customer's name |
| movie_name | TEXT NOT NULL | Movie title |
| tickets | INTEGER NOT NULL CHECK(tickets > 0) | Ticket quantity |
| show_time | TEXT NOT NULL | Selected timing |
| category | TEXT NOT NULL | Selected ticket category |
| created_at | TEXT NOT NULL | Local creation timestamp in ISO format |

Prices are defined centrally in the program: Standard = Rs. 150, Premium = Rs. 250, VIP = Rs. 400. Total price is derived as `tickets × category price` and is not stored in the database. Changing category prices therefore affects totals displayed for existing records.

Parameterized SQL keeps entered names separate from SQL commands. Database transactions commit completed writes and roll back failures. Booking IDs are trimmed and converted to uppercase, so `bk001` and `BK001` refer to the same booking.

## 7. Algorithms

### Add booking

1. Read form fields.
2. Trim text and normalize the Booking ID.
3. Validate required fields, ID format, ticket count, show timing, and category.
4. Insert the booking using parameterized SQL.
5. If the ID exists, show a validation message without overwriting the record.
6. Refresh the Listbox and totals, then select the saved booking.

### Search booking

1. Read and normalize the ID from the search field.
2. Query the database for the matching primary key.
3. If found, populate the form and select the Listbox item.
4. Otherwise, show a clear not-found message.

### Update booking

1. Search for or select the intended record.
2. Keep the ID read-only while allowing other fields to change.
3. Validate the edited values.
4. Update the database row with the selected ID.
5. Refresh the list, selection, and totals.

### Cancel booking

1. Find the booking using the form's Booking ID.
2. Display the saved customer, movie, and quantity for confirmation.
3. If confirmed, delete the row. If declined, retain it.
4. Clear the form and refresh the register after deletion.

### Display and export

Read all records ordered by creation time descending and ID ascending, then populate the Listbox. Export writes all saved bookings to UTF-8 CSV with a header and derived total. Spreadsheet formula prefixes in entered text are neutralized during export.

## 8. Validation and error handling

- Booking ID and customer name are mandatory; movie name is also required.
- IDs contain at most 30 ASCII letters, digits, underscores, or hyphens.
- Customer and movie names contain at most 100 characters, without control characters.
- Ticket counts must be positive ASCII whole numbers up to 999,999,999. This is an input bound, not theatre capacity.
- Show timing and category must match the configured options.
- Duplicate IDs, missing records, database errors, and file export errors produce dialogs.
- Cancellation requires confirmation because it permanently removes a record.

## 9. Testing

The supplied suite contains nine automated tests. It checks the complete booking lifecycle; duplicate protection; invalid ticket inputs; required and selection fields; missing-record operations; apostrophes and SQL-like text; validation of direct storage input; persistence after reopening; and the GUI add/search/update/export/cancel workflow, including declining cancellation.

Run `python -m unittest discover -s tests -v` from the project folder. UI dialogs are mocked in the integration test to exercise callbacks without requiring user responses. Visual inspection of the rendered interface is separate from these automated assertions.

| Manual demonstration | Expected result |
|---|---|
| Add BK001 with 2 Premium tickets | Record saved; total Rs. 500 |
| Search using bk001 | Same booking loaded |
| Change quantity to 3 and update | Total Rs. 750; one record remains |
| Restart application | Saved booking remains |
| Add duplicate BK001 | Message shown; existing record preserved |
| Enter 0, -1, or 2.5 tickets | Validation message; no invalid record saved |
| Decline cancellation | Booking retained |
| Confirm cancellation | Booking removed |

## 10. Limitations and future improvements

The current scope is a local academic booking register. It has no payment gateway, refund workflow, authentication, seat allocation, capacity validation, date selection, or multi-computer synchronization. Cancellation deletes records instead of preserving an audit history. Prices are illustrative and are not stored as historical snapshots.

Future work could add show dates and seat maps, separate movie/show/customer tables, capacity checks inside transactions, stored purchase prices, cancellation history, role-based access, and a server-backed interface.

## 11. Viva preparation

**Why use Tkinter?** It provides Python's standard desktop GUI widgets, including the widgets explicitly required in the assignment.

**Why SQLite?** It provides persistent relational storage without installing a separate database server.

**What are CRUD operations?** Create, Read, Update, and Delete. Add creates a record, search/list reads records, update changes a record, and cancel deletes a record.

**What is a primary key?** A column that uniquely identifies a row. Here it prevents duplicate Booking IDs.

**What is a callback?** A function executed in response to an event, such as pressing the Add booking button.

**What is StringVar?** A Tkinter variable that connects a widget's displayed value with Python code. Variable tracing also updates the calculated total when inputs change.

**Why use parameterized SQL?** Parameters safely pass data such as names containing apostrophes without treating that text as SQL syntax.

**Why validate in the storage module as well as the form?** Shared validation protects writes even when the storage class is called without the GUI.

**Why is Booking ID locked during editing?** It prevents accidentally changing the identity of the selected record. New / Clear begins a separate booking.

**What happens after closing the program?** Committed bookings remain in the SQLite file and are loaded when the program starts again.

## 12. Conclusion

CineDesk implements the assignment's form fields, selection widgets, booking operations, and validation requirements. It demonstrates event-driven programming, structured validation, parameterized database operations, and persistence through a locally runnable desktop application.
