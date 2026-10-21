"""
Library Management System
Frontend: Python Tkinter / ttk
Database: SQLite (built-in; no separate installation required)
A MySQL schema is included separately for DBMS lab demonstration.
Run: python library_app.py
"""
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import date

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "library_db.sqlite3"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'General',
            isbn TEXT UNIQUE,
            copies INTEGER NOT NULL DEFAULT 1 CHECK(copies >= 0),
            available INTEGER NOT NULL DEFAULT 1 CHECK(available >= 0 AND available <= copies)
        );
        CREATE TABLE IF NOT EXISTS members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            joined_on TEXT NOT NULL DEFAULT (DATE('now'))
        );
        CREATE TABLE IF NOT EXISTS issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE RESTRICT,
            member_id INTEGER NOT NULL REFERENCES members(member_id) ON DELETE RESTRICT,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_issues_member ON issues(member_id);
        CREATE INDEX IF NOT EXISTS idx_issues_book ON issues(book_id);
        """)
        book_count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        member_count = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]
        if book_count == 0:
            conn.executemany(
                "INSERT INTO books(title, author, category, isbn, copies, available) VALUES(?,?,?,?,?,?)",
                [
                    ("Database System Concepts", "Abraham Silberschatz", "Computer Science", "9780078022159", 3, 3),
                    ("Wings of Fire", "A. P. J. Abdul Kalam", "Biography", "9788173711466", 2, 2),
                    ("The Alchemist", "Paulo Coelho", "Fiction", "9780061122415", 4, 4),
                    ("Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", "9780262046305", 2, 2),
                ])
        if member_count == 0:
            conn.executemany(
                "INSERT INTO members(name,email,phone) VALUES(?,?,?)",
                [
                    ("Arun Kumar", "arun@example.com", "9876543210"),
                    ("Priya Sharma", "priya@example.com", "9876501234"),
                ])

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1180x760")
        self.minsize(1000, 650)
        self.configure(bg="#F3F6FB")
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.configure_styles()
        self.build_shell()
        self.refresh_all()

    def configure_styles(self):
        self.style.configure("TFrame", background="#F3F6FB")
        self.style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        self.style.configure("TLabel", background="#F3F6FB", foreground="#172B4D", font=("Arial", 10))
        self.style.configure("Title.TLabel", font=("Arial", 22, "bold"), foreground="#14294D")
        self.style.configure("Sub.TLabel", font=("Arial", 10), foreground="#64748B")
        self.style.configure("CardValue.TLabel", background="#FFFFFF", font=("Arial", 22, "bold"), foreground="#14294D")
        self.style.configure("CardTitle.TLabel", background="#FFFFFF", font=("Arial", 9, "bold"), foreground="#64748B")
        self.style.configure("TButton", font=("Arial", 10), padding=(12, 8))
        self.style.configure("Accent.TButton", background="#2457C5", foreground="#FFFFFF", font=("Arial", 10, "bold"))
        self.style.map("Accent.TButton", background=[("active", "#1D469D")])
        self.style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#172B4D", rowheight=30, font=("Arial", 10))
        self.style.configure("Treeview.Heading", background="#E8EEF8", foreground="#20385F", font=("Arial", 9, "bold"), padding=8)
        self.style.map("Treeview", background=[("selected", "#D7E5FF")], foreground=[("selected", "#14294D")])
        self.style.configure("TNotebook", background="#F3F6FB", borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=(18, 10), font=("Arial", 10, "bold"))

    def build_shell(self):
        header = tk.Frame(self, bg="#14294D", height=92)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📚  LIBRARY MANAGEMENT SYSTEM", bg="#14294D", fg="white",
                 font=("Arial", 20, "bold")).pack(anchor="w", padx=26, pady=(18, 2))
        tk.Label(header, text="A database-driven application for books, members and circulation",
                 bg="#14294D", fg="#C7D6F2", font=("Arial", 10)).pack(anchor="w", padx=28)
        self.body = ttk.Frame(self, padding=(22, 18))
        self.body.pack(fill="both", expand=True)
        title_row = ttk.Frame(self.body)
        title_row.pack(fill="x", pady=(0, 14))
        ttk.Label(title_row, text="Overview", style="Title.TLabel").pack(side="left")
        ttk.Label(title_row, text="Manage library records from one place", style="Sub.TLabel").pack(side="left", padx=16, pady=(9,0))
        cards = ttk.Frame(self.body)
        cards.pack(fill="x", pady=(0, 16))
        self.card_books = self.make_stat_card(cards, "TOTAL BOOK TITLES", "0")
        self.card_members = self.make_stat_card(cards, "REGISTERED MEMBERS", "0")
        self.card_available = self.make_stat_card(cards, "COPIES AVAILABLE", "0")
        self.card_issued = self.make_stat_card(cards, "CURRENTLY ISSUED", "0")
        self.tabs = ttk.Notebook(self.body)
        self.tabs.pack(fill="both", expand=True)
        self.build_books_tab()
        self.build_members_tab()
        self.build_circulation_tab()
        footer = tk.Frame(self, bg="#E7EDF6", height=28)
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, text=f"Local database: {DB_PATH.name}  •  Project demo build",
                 bg="#E7EDF6", fg="#52647F", font=("Arial", 9)).pack(side="left", padx=22, pady=6)

    def make_stat_card(self, parent, label, value):
        card = ttk.Frame(parent, style="Card.TFrame", padding=(16, 14))
        card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        ttk.Label(card, text=label, style="CardTitle.TLabel").pack(anchor="w")
        val = ttk.Label(card, text=value, style="CardValue.TLabel")
        val.pack(anchor="w", pady=(8, 0))
        return val

    def make_table(self, parent, columns, headings, widths=None):
        wrapper = ttk.Frame(parent)
        wrapper.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        tree = ttk.Treeview(wrapper, columns=columns, show="headings", selectmode="browse")
        for idx, (col, heading) in enumerate(zip(columns, headings)):
            tree.heading(col, text=heading)
            tree.column(col, width=(widths[idx] if widths else 130), anchor="w")
        ybar = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        xbar = ttk.Scrollbar(wrapper, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        wrapper.rowconfigure(0, weight=1)
        wrapper.columnconfigure(0, weight=1)
        return tree

    def build_books_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Books")
        form = ttk.LabelFrame(tab, text="Add a book", padding=12)
        form.pack(fill="x", padx=14, pady=(14, 4))
        self.book_fields = {}
        fields = [("Title", 24), ("Author", 20), ("Category", 16), ("ISBN (optional)", 17), ("Copies", 7)]
        for i, (label, width) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky="w", padx=5, pady=(0,4))
            entry = ttk.Entry(form, width=width)
            entry.grid(row=1, column=i, padx=5, pady=(0,4), sticky="ew")
            self.book_fields[label] = entry
        self.book_fields["Category"].insert(0, "General")
        self.book_fields["Copies"].insert(0, "1")
        ttk.Button(form, text="＋ Add Book", style="Accent.TButton", command=self.add_book).grid(row=1, column=5, padx=8)
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", padx=14, pady=(8,0))
        ttk.Label(toolbar, text="Search books").pack(side="left")
        self.book_search = tk.StringVar()
        search = ttk.Entry(toolbar, textvariable=self.book_search, width=32)
        search.pack(side="left", padx=8)
        self.book_search.trace_add("write", lambda *_: self.load_books())
        ttk.Button(toolbar, text="Delete Selected", command=self.delete_book).pack(side="right")
        self.books_tree = self.make_table(tab, ("id","title","author","category","isbn","copies","available"),
            ("ID","Title","Author","Category","ISBN","Copies","Available"), (55,260,190,135,150,75,85))

    def build_members_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Members")
        form = ttk.LabelFrame(tab, text="Register a member", padding=12)
        form.pack(fill="x", padx=14, pady=(14, 4))
        self.member_fields = {}
        for i, (label, width) in enumerate([("Name",24),("Email",30),("Phone",18)]):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky="w", padx=5, pady=(0,4))
            entry = ttk.Entry(form, width=width)
            entry.grid(row=1, column=i, padx=5, pady=(0,4), sticky="ew")
            self.member_fields[label] = entry
        ttk.Button(form, text="＋ Register Member", style="Accent.TButton", command=self.add_member).grid(row=1, column=3, padx=8)
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", padx=14, pady=(8,0))
        ttk.Label(toolbar, text="Search members").pack(side="left")
        self.member_search = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.member_search, width=32).pack(side="left", padx=8)
        self.member_search.trace_add("write", lambda *_: self.load_members())
        ttk.Button(toolbar, text="Delete Selected", command=self.delete_member).pack(side="right")
        self.members_tree = self.make_table(tab, ("id","name","email","phone","joined"),
            ("ID","Name","Email","Phone","Joined On"), (65,220,300,180,130))

    def build_circulation_tab(self):
        tab = ttk.Frame(self.tabs)
        self.tabs.add(tab, text="Issue / Return")
        intro = ttk.Label(tab, text="Select a book and member by ID. New loans receive a 14-day due date.", style="Sub.TLabel")
        intro.pack(anchor="w", padx=16, pady=(14,4))
        form = ttk.LabelFrame(tab, text="Issue a book", padding=12)
        form.pack(fill="x", padx=14, pady=4)
        ttk.Label(form, text="Book ID").grid(row=0, column=0, padx=5, sticky="w")
        self.issue_book_id = ttk.Entry(form, width=12)
        self.issue_book_id.grid(row=1, column=0, padx=5)
        ttk.Label(form, text="Member ID").grid(row=0, column=1, padx=5, sticky="w")
        self.issue_member_id = ttk.Entry(form, width=12)
        self.issue_member_id.grid(row=1, column=1, padx=5)
        ttk.Button(form, text="Issue Book", style="Accent.TButton", command=self.issue_book).grid(row=1, column=2, padx=10)
        ttk.Button(form, text="Return Selected", command=self.return_book).grid(row=1, column=3, padx=4)
        ttk.Button(form, text="Refresh", command=self.refresh_all).grid(row=1, column=4, padx=4)
        ttk.Label(tab, text="Loan history", font=("Arial", 11, "bold")).pack(anchor="w", padx=16, pady=(10,0))
        self.issues_tree = self.make_table(tab, ("id","book","member","issued","due","returned","status"),
            ("Issue ID","Book","Member","Issue Date","Due Date","Return Date","Status"), (70,245,180,115,115,115,110))

    def add_book(self):
        f = self.book_fields
        title, author = f["Title"].get().strip(), f["Author"].get().strip()
        category = f["Category"].get().strip() or "General"
        isbn = f["ISBN (optional)"].get().strip() or None
        try:
            copies = int(f["Copies"].get())
            if not title or not author:
                raise ValueError("Title and author are required.")
            if copies < 1:
                raise ValueError("Copies must be at least 1.")
            with connect() as conn:
                conn.execute("INSERT INTO books(title,author,category,isbn,copies,available) VALUES(?,?,?,?,?,?)",
                             (title,author,category,isbn,copies,copies))
            for key in f:
                f[key].delete(0, "end")
            f["Category"].insert(0,"General"); f["Copies"].insert(0,"1")
            self.refresh_all()
            messagebox.showinfo("Book added", "The book has been saved.")
        except ValueError as exc:
            messagebox.showerror("Check input", str(exc) if str(exc) else "Copies must be a whole number.")
        except sqlite3.IntegrityError as exc:
            messagebox.showerror("Could not add book", "That ISBN is already registered, or a value violates a database rule.")
        except sqlite3.Error as exc:
            messagebox.showerror("Database error", str(exc))

    def delete_book(self):
        sel = self.books_tree.selection()
        if not sel:
            messagebox.showwarning("Select a book", "Select a book row first.")
            return
        book_id = self.books_tree.item(sel[0], "values")[0]
        if not messagebox.askyesno("Confirm deletion", "Delete this book record? Books with loan history cannot be deleted."):
            return
        try:
            with connect() as conn:
                conn.execute("DELETE FROM books WHERE book_id=?", (book_id,))
            self.refresh_all()
        except sqlite3.IntegrityError:
            messagebox.showerror("Cannot delete", "This book has loan history. Keep the record to preserve referential integrity.")

    def add_member(self):
        f = self.member_fields
        name, email, phone = f["Name"].get().strip(), f["Email"].get().strip(), f["Phone"].get().strip()
        if not name or not email or "@" not in email:
            messagebox.showerror("Check input", "Enter a name and a valid email address.")
            return
        try:
            with connect() as conn:
                conn.execute("INSERT INTO members(name,email,phone) VALUES(?,?,?)", (name,email,phone))
            for e in f.values(): e.delete(0,"end")
            self.refresh_all()
            messagebox.showinfo("Member registered", "The member has been saved.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate email", "A member with this email already exists.")
        except sqlite3.Error as exc:
            messagebox.showerror("Database error", str(exc))

    def delete_member(self):
        sel = self.members_tree.selection()
        if not sel:
            messagebox.showwarning("Select a member", "Select a member row first.")
            return
        member_id = self.members_tree.item(sel[0], "values")[0]
        if not messagebox.askyesno("Confirm deletion", "Delete this member? Members with loan history cannot be deleted."):
            return
        try:
            with connect() as conn:
                conn.execute("DELETE FROM members WHERE member_id=?", (member_id,))
            self.refresh_all()
        except sqlite3.IntegrityError:
            messagebox.showerror("Cannot delete", "This member has loan history. Keep the record to preserve referential integrity.")

    def issue_book(self):
        try:
            bid, mid = int(self.issue_book_id.get()), int(self.issue_member_id.get())
            today = date.today()
            due = date.fromordinal(today.toordinal() + 14).isoformat()
            with connect() as conn:
                book = conn.execute("SELECT available FROM books WHERE book_id=?", (bid,)).fetchone()
                member = conn.execute("SELECT member_id FROM members WHERE member_id=?", (mid,)).fetchone()
                if not book:
                    raise ValueError("Book ID was not found.")
                if not member:
                    raise ValueError("Member ID was not found.")
                if book["available"] < 1:
                    raise ValueError("No copies of this book are currently available.")
                conn.execute("INSERT INTO issues(book_id,member_id,issue_date,due_date) VALUES(?,?,?,?)",
                             (bid,mid,today.isoformat(),due))
                conn.execute("UPDATE books SET available=available-1 WHERE book_id=?", (bid,))
            self.issue_book_id.delete(0,"end"); self.issue_member_id.delete(0,"end")
            self.refresh_all()
            messagebox.showinfo("Book issued", f"Loan recorded. Due date: {due}")
        except ValueError as exc:
            messagebox.showerror("Cannot issue book", str(exc) or "Enter numeric Book ID and Member ID.")
        except sqlite3.Error as exc:
            messagebox.showerror("Database error", str(exc))

    def return_book(self):
        sel = self.issues_tree.selection()
        if not sel:
            messagebox.showwarning("Select a loan", "Select a loan record first.")
            return
        issue_id = self.issues_tree.item(sel[0], "values")[0]
        try:
            with connect() as conn:
                loan = conn.execute("SELECT book_id,return_date FROM issues WHERE issue_id=?", (issue_id,)).fetchone()
                if not loan:
                    raise ValueError("Loan record not found.")
                if loan["return_date"] is not None:
                    raise ValueError("This book has already been returned.")
                conn.execute("UPDATE issues SET return_date=? WHERE issue_id=?", (date.today().isoformat(),issue_id))
                conn.execute("UPDATE books SET available=available+1 WHERE book_id=?", (loan["book_id"],))
            self.refresh_all()
            messagebox.showinfo("Book returned", "The return has been recorded.")
        except ValueError as exc:
            messagebox.showinfo("Return status", str(exc))
        except sqlite3.Error as exc:
            messagebox.showerror("Database error", str(exc))

    def load_books(self):
        query = self.book_search.get().strip() if hasattr(self, "book_search") else ""
        with connect() as conn:
            rows = conn.execute("""SELECT book_id,title,author,category,COALESCE(isbn,''),copies,available
                                   FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
                                   ORDER BY title""", (f"%{query}%",)*3).fetchall()
        self.populate(self.books_tree, rows)

    def load_members(self):
        query = self.member_search.get().strip() if hasattr(self, "member_search") else ""
        with connect() as conn:
            rows = conn.execute("""SELECT member_id,name,email,COALESCE(phone,''),joined_on
                                   FROM members WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
                                   ORDER BY name""", (f"%{query}%",)*3).fetchall()
        self.populate(self.members_tree, rows)

    def load_issues(self):
        with connect() as conn:
            rows = conn.execute("""
                SELECT i.issue_id,b.title,m.name,i.issue_date,i.due_date,
                       COALESCE(i.return_date,'—'),
                       CASE WHEN i.return_date IS NOT NULL THEN 'Returned'
                            WHEN i.due_date < DATE('now') THEN 'Overdue'
                            ELSE 'Issued' END AS status
                FROM issues i JOIN books b ON b.book_id=i.book_id
                JOIN members m ON m.member_id=i.member_id
                ORDER BY i.issue_id DESC
            """).fetchall()
        self.populate(self.issues_tree, rows)

    @staticmethod
    def populate(tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", "end", values=tuple(row))

    def refresh_all(self):
        self.load_books()
        self.load_members()
        self.load_issues()
        with connect() as conn:
            books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            members = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]
            available = conn.execute("SELECT COALESCE(SUM(available),0) FROM books").fetchone()[0]
            issued = conn.execute("SELECT COUNT(*) FROM issues WHERE return_date IS NULL").fetchone()[0]
        self.card_books.configure(text=str(books))
        self.card_members.configure(text=str(members))
        self.card_available.configure(text=str(available))
        self.card_issued.configure(text=str(issued))

if __name__ == "__main__":
    initialize_database()
    app = LibraryApp()
    app.mainloop()
