from pathlib import Path
from datetime import date, timedelta
import sqlite3
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "library_db.sqlite3"

st.set_page_config(page_title="Libra | Library Management", page_icon="📚", layout="wide")

# ---------- Database ----------
def connect():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
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
        # Add sample data only if the respective table is empty.
        if conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO books(title,author,category,isbn,copies,available) VALUES(?,?,?,?,?,?)",
                [
                    ("Database System Concepts", "Abraham Silberschatz", "Computer Science", "9780078022159", 3, 3),
                    ("Wings of Fire", "A. P. J. Abdul Kalam", "Biography", "9788173711466", 2, 2),
                    ("The Alchemist", "Paulo Coelho", "Fiction", "9780061122415", 4, 4),
                    ("Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", "9780262046305", 2, 2),
                ],
            )
        if conn.execute("SELECT COUNT(*) FROM members").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO members(name,email,phone) VALUES(?,?,?)",
                [("Arun Kumar", "arun@example.com", "9876543210"),
                 ("Priya Sharma", "priya@example.com", "9876501234")],
            )

def df(sql, params=()):
    with connect() as conn:
        return pd.read_sql_query(sql, conn, params=params)

def scalar(sql, params=()):
    with connect() as conn:
        return conn.execute(sql, params).fetchone()[0]

def safe_error(prefix, exc):
    st.error(f"{prefix}: {exc}")

init_db()

# ---------- Visual style ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
.stApp {background:#F5F7FB;}
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
[data-testid="stSidebar"] {background:#10233F;}
[data-testid="stSidebar"] * {color:#E8EEF8;}
.block-container {max-width:1500px;padding-top:1.8rem;padding-bottom:3rem;}
h1,h2,h3 {font-family:'Manrope',sans-serif;color:#132744;}
div[data-testid="stForm"] {background:#fff;border:1px solid #E7ECF4;border-radius:14px;padding:16px;}
.stButton button,.stDownloadButton button {border-radius:9px;font-weight:650;min-height:2.5rem;}
[data-testid="stDataFrame"] {border:1px solid #E7ECF4;border-radius:12px;overflow:hidden;}
.metric {background:#fff;border:1px solid #E7ECF4;border-radius:16px;padding:18px;}
.metric .label {font-size:.76rem;color:#718096;font-weight:700;text-transform:uppercase;letter-spacing:.04em;}
.metric .value {font-size:1.9rem;font-weight:800;color:#142B4C;margin-top:6px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='font-size:2rem;font-weight:800;margin:8px 0'>📚 libra</div><div style='font-size:.78rem;margin-bottom:22px;color:#AEBFD8'>LIBRARY OPERATIONS PLATFORM</div>", unsafe_allow_html=True)
    page = st.radio("WORKSPACE", ["Overview", "Books", "Members", "Issue & Return", "Transaction History"])
    st.divider()
    st.caption("SQLite database · Local project")

st.title("Libra Library Management")
st.caption(f"Local database: `{DB_PATH.name}` · Changes are saved automatically.")

# Dashboard counts are queried on every Streamlit rerun.
book_titles = scalar("SELECT COUNT(*) FROM books")
member_total = scalar("SELECT COUNT(*) FROM members")
available_total = scalar("SELECT COALESCE(SUM(available),0) FROM books")
active_loans = scalar("SELECT COUNT(*) FROM issues WHERE return_date IS NULL")
overdue_total = scalar("SELECT COUNT(*) FROM issues WHERE return_date IS NULL AND due_date < DATE('now')")

def metric(label, value):
    st.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div></div>', unsafe_allow_html=True)

def loans_frame():
    return df("""
        SELECT i.issue_id AS 'Loan ID', b.title AS Book, m.name AS Member,
               i.issue_date AS 'Issue date', i.due_date AS 'Due date',
               COALESCE(i.return_date,'—') AS 'Return date',
               CASE WHEN i.return_date IS NOT NULL THEN 'Returned'
                    WHEN i.due_date < DATE('now') THEN 'Overdue' ELSE 'Issued' END AS Status
        FROM issues i JOIN books b ON b.book_id=i.book_id
        JOIN members m ON m.member_id=i.member_id
        ORDER BY i.issue_id DESC
    """)

# ---------- Overview ----------
if page == "Overview":
    st.markdown(f"""<div style="background:linear-gradient(120deg,#10233F,#315CB5);border-radius:20px;padding:26px 30px;color:white;margin-bottom:20px">
    <div style="font-size:.75rem;font-weight:800;letter-spacing:.14em;color:#BFD2FF">LIBRARY CONTROL CENTRE</div>
    <div style="font-size:1.8rem;font-weight:800;margin-top:8px">Your library at a glance</div>
    <div style="color:#D7E4FA;margin-top:5px">{date.today().strftime('%A, %d %B %Y')} · Books, members and circulation in one place.</div></div>""", unsafe_allow_html=True)
    cols = st.columns(5)
    for col, label, value in zip(cols, ["Book titles", "Members", "Available copies", "Active loans", "Overdue"], [book_titles, member_total, available_total, active_loans, overdue_total]):
        with col: metric(label, value)
    left, right = st.columns([1.15, .85], gap="large")
    with left:
        st.subheader("Catalogue by category")
        cats = df("SELECT category AS Category, COUNT(*) AS Titles FROM books GROUP BY category ORDER BY Titles DESC")
        if cats.empty: st.info("Add a book to begin.")
        else: st.bar_chart(cats.set_index("Category"))
    with right:
        st.subheader("Needs attention")
        if overdue_total:
            st.warning(f"{overdue_total} loan(s) are overdue.")
        else:
            st.success("No overdue loans right now.")

    low = df("""
        SELECT title AS Title, available AS "Available copies"
        FROM books
        WHERE available <= 1
        ORDER BY available, title
        LIMIT 8
    """)
    st.markdown("**Low availability**")
    if low.empty:
        st.success("All books have more than one available copy.")
    else:
        st.dataframe(low, hide_index=True, use_container_width=True)

    st.subheader("Recent circulation")
    recent = loans_frame().head(8)
    if recent.empty:
        st.info("No issue/return records yet.")
    else:
        st.dataframe(recent, hide_index=True, use_container_width=True)

# ---------- Books ----------
elif page == "Books":
    st.header("Books catalogue")
    st.caption("Add, search, edit and remove book records. Stock cannot be reduced below copies already on loan.")
    with st.expander("＋ Add a new book", expanded=True):
        with st.form("add_book_form", clear_on_submit=True):
            a,b = st.columns(2)
            title = a.text_input("Book title *")
            author = b.text_input("Author *")
            c,d,e = st.columns(3)
            category = c.text_input("Category", value="General")
            isbn = d.text_input("ISBN (optional)")
            copies = e.number_input("Total copies", min_value=1, max_value=10000, value=1, step=1)
            submitted = st.form_submit_button("Add book", type="primary", use_container_width=True)
        if submitted:
            if not title.strip() or not author.strip():
                st.error("Book title and author are required.")
            else:
                try:
                    with connect() as conn:
                        conn.execute("INSERT INTO books(title,author,category,isbn,copies,available) VALUES(?,?,?,?,?,?)",
                                     (title.strip(), author.strip(), category.strip() or "General", isbn.strip() or None, int(copies), int(copies)))
                    st.success("Book added.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That ISBN already exists. Use a unique ISBN or leave it blank.")
                except sqlite3.Error as exc: safe_error("Could not add book", exc)

    search = st.text_input("Search books", placeholder="Title, author, category or ISBN")
    books = df("""SELECT book_id AS ID,title AS Title,author AS Author,category AS Category,
                  COALESCE(isbn,'') AS ISBN,copies AS Copies,available AS Available
                  FROM books WHERE title LIKE ? OR author LIKE ? OR category LIKE ? OR COALESCE(isbn,'') LIKE ?
                  ORDER BY title""", tuple([f"%{search}%"]*4))
    st.caption(f"{len(books)} book title(s)")
    st.dataframe(books, hide_index=True, use_container_width=True, height=330)
    st.download_button("Export books CSV", books.to_csv(index=False).encode("utf-8"), "library_books.csv", "text/csv")
    st.subheader("Edit a book")
    if books.empty:
        st.info("No books match this search.")
    else:
        book_options = {f"#{int(r.ID)} · {r.Title}": int(r.ID) for r in books.itertuples()}
        chosen_label = st.selectbox("Choose a book to edit", list(book_options), key="edit_book_select")
        chosen_id = book_options[chosen_label]
        row = df("SELECT * FROM books WHERE book_id=?", (chosen_id,)).iloc[0]
        with st.form("edit_book_form"):
            a,b = st.columns(2)
            etitle = a.text_input("Title", value=str(row["title"]))
            eauthor = b.text_input("Author", value=str(row["author"]))
            c,d,e = st.columns(3)
            ecategory = c.text_input("Category", value=str(row["category"] or "General"))
            eisbn = d.text_input("ISBN", value=str(row["isbn"] or ""))
            ecopies = e.number_input("Total copies", min_value=1, max_value=10000, value=max(1,int(row["copies"])), step=1)
            save_edit = st.form_submit_button("Save book changes", type="primary")
        if save_edit:
            if not etitle.strip() or not eauthor.strip():
                st.error("Title and author are required.")
            else:
                try:
                    with connect() as conn:
                        current = conn.execute("SELECT copies,available FROM books WHERE book_id=?", (chosen_id,)).fetchone()
                        on_loan = current["copies"] - current["available"]
                        if int(ecopies) < on_loan:
                            st.error(f"Cannot set total copies below {on_loan}; that many copies are currently on loan.")
                        else:
                            new_available = int(ecopies) - on_loan
                            conn.execute("UPDATE books SET title=?,author=?,category=?,isbn=?,copies=?,available=? WHERE book_id=?",
                                         (etitle.strip(), eauthor.strip(), ecategory.strip() or "General", eisbn.strip() or None, int(ecopies), new_available, chosen_id))
                            st.success("Book updated."); st.rerun()
                except sqlite3.IntegrityError: st.error("That ISBN is already assigned to another book.")
                except sqlite3.Error as exc: safe_error("Could not update book", exc)
    with st.expander("Delete a book", expanded=True):
        all_books = df("SELECT book_id,title FROM books ORDER BY title")
        if all_books.empty: st.info("No books to delete.")
        else:
            delete_map = {f"#{int(r.book_id)} · {r.title}": int(r.book_id) for r in all_books.itertuples()}
            del_label = st.selectbox("Select book", list(delete_map), key="delete_book_select")
            del_book_id = delete_map[del_label]
            linked_loans = scalar("SELECT COUNT(*) FROM issues WHERE book_id=?", (del_book_id,))
            st.warning(f"This will permanently delete the book and its {linked_loans} related loan record(s). This cannot be undone.")
            confirm_book_delete = st.checkbox("I understand and want to permanently delete this book", key="confirm_book_delete")
            if st.button("Delete selected book", key="delete_book_btn", type="primary", disabled=not confirm_book_delete):
                try:
                    with connect() as conn:
                        conn.execute("DELETE FROM issues WHERE book_id=?", (del_book_id,))
                        conn.execute("DELETE FROM books WHERE book_id=?", (del_book_id,))
                    st.success("Book and related loan records deleted."); st.rerun()
                except sqlite3.Error as exc: safe_error("Could not delete book", exc)

# ---------- Members ----------
elif page == "Members":
    st.header("Member directory")
    st.caption("Register readers, search records and edit contact details.")
    with st.expander("＋ Register a member", expanded=True):
        with st.form("add_member_form", clear_on_submit=True):
            a,b,c = st.columns([1,1.2,1])
            name = a.text_input("Full name *")
            email = b.text_input("Email address *")
            phone = c.text_input("Phone number")
            submitted = st.form_submit_button("Register member", type="primary", use_container_width=True)
        if submitted:
            normalized_email = email.strip().lower()
            if not name.strip() or "@" not in normalized_email or "." not in normalized_email.split("@")[-1]:
                st.error("Enter a name and a valid email address.")
            else:
                try:
                    with connect() as conn:
                        conn.execute("INSERT INTO members(name,email,phone) VALUES(?,?,?)", (name.strip(), normalized_email, phone.strip()))
                    st.success("Member registered."); st.rerun()
                except sqlite3.IntegrityError: st.error("That email address is already registered.")
                except sqlite3.Error as exc: safe_error("Could not register member", exc)
    search = st.text_input("Search members", placeholder="Name, email or phone")
    members_df = df("""SELECT member_id AS ID,name AS Name,email AS Email,COALESCE(phone,'') AS Phone,joined_on AS 'Joined on'
                       FROM members WHERE name LIKE ? OR email LIKE ? OR COALESCE(phone,'') LIKE ? ORDER BY name""",
                    tuple([f"%{search}%"]*3))
    st.caption(f"{len(members_df)} member(s)")
    st.dataframe(members_df, hide_index=True, use_container_width=True, height=330)
    st.download_button("Export members CSV", members_df.to_csv(index=False).encode("utf-8"), "library_members.csv", "text/csv")
    st.subheader("Edit a member")
    all_members = df("SELECT * FROM members ORDER BY name")
    if not all_members.empty:
        member_map = {f"#{int(r.member_id)} · {r.name} ({r.email})": int(r.member_id) for r in all_members.itertuples()}
        mlabel = st.selectbox("Choose a member to edit", list(member_map), key="edit_member_select")
        mid = member_map[mlabel]
        mrow = df("SELECT * FROM members WHERE member_id=?", (mid,)).iloc[0]
        with st.form("edit_member_form"):
            a,b,c = st.columns([1,1.2,1])
            mname = a.text_input("Name", value=str(mrow["name"]))
            memail = b.text_input("Email", value=str(mrow["email"]))
            mphone = c.text_input("Phone", value=str(mrow["phone"] or ""))
            save_member = st.form_submit_button("Save member changes", type="primary")
        if save_member:
            norm = memail.strip().lower()
            if not mname.strip() or "@" not in norm or "." not in norm.split("@")[-1]:
                st.error("Enter a name and a valid email.")
            else:
                try:
                    with connect() as conn:
                        conn.execute("UPDATE members SET name=?,email=?,phone=? WHERE member_id=?", (mname.strip(),norm,mphone.strip(),mid))
                    st.success("Member updated."); st.rerun()
                except sqlite3.IntegrityError: st.error("That email belongs to another member.")
                except sqlite3.Error as exc: safe_error("Could not update member", exc)
    with st.expander("Delete a member", expanded=True):
        if all_members.empty: st.info("No members to delete.")
        else:
            del_member_label = st.selectbox("Select member", list(member_map), key="delete_member_select")
            del_member_id = member_map[del_member_label]
            linked_loans = scalar("SELECT COUNT(*) FROM issues WHERE member_id=?", (del_member_id,))
            open_member_loans = scalar("SELECT COUNT(*) FROM issues WHERE member_id=? AND return_date IS NULL", (del_member_id,))
            st.warning(f"This will permanently delete the member and {linked_loans} related loan record(s). {open_member_loans} open loan(s) will be closed and their copies returned to stock. This cannot be undone.")
            confirm_member_delete = st.checkbox("I understand and want to permanently delete this member", key="confirm_member_delete")
            if st.button("Delete selected member", key="delete_member_btn", type="primary", disabled=not confirm_member_delete):
                try:
                    with connect() as conn:
                        open_loans = conn.execute("SELECT book_id, COUNT(*) AS qty FROM issues WHERE member_id=? AND return_date IS NULL GROUP BY book_id", (del_member_id,)).fetchall()
                        for loan in open_loans:
                            conn.execute("UPDATE books SET available=MIN(copies,available+?) WHERE book_id=?", (loan["qty"], loan["book_id"]))
                        conn.execute("DELETE FROM issues WHERE member_id=?", (del_member_id,))
                        conn.execute("DELETE FROM members WHERE member_id=?", (del_member_id,))
                    st.success("Member and related loan records deleted."); st.rerun()
                except sqlite3.Error as exc: safe_error("Could not delete member", exc)

# ---------- Issue and Return ----------
elif page == "Issue & Return":
    st.header("Issue & return desk")
    c1,c2,c3 = st.columns(3)
    with c1: metric("Active loans", active_loans)
    with c2: metric("Overdue", overdue_total)
    with c3: metric("Returned today", scalar("SELECT COUNT(*) FROM issues WHERE return_date=DATE('now')"))
    books_available = df("SELECT book_id,title,author,available FROM books WHERE available > 0 ORDER BY title")
    members_all = df("SELECT member_id,name,email FROM members ORDER BY name")
    st.subheader("Issue a book")
    if books_available.empty: st.warning("No copies are available. Add stock or return a book first.")
    elif members_all.empty: st.warning("Register a member before issuing a book.")
    else:
        with st.form("issue_form", clear_on_submit=True):
            book_map = {f"{r.title} — {r.author} (available: {r.available})": int(r.book_id) for r in books_available.itertuples()}
            member_map = {f"{r.name} — {r.email}": int(r.member_id) for r in members_all.itertuples()}
            a,b = st.columns(2)
            book_label = a.selectbox("Book", list(book_map))
            member_label = b.selectbox("Member", list(member_map))
            issue_date = st.date_input("Issue date", value=date.today())
            due_date = st.date_input("Due date", value=date.today()+timedelta(days=14), min_value=issue_date)
            submit_issue = st.form_submit_button("Confirm issue", type="primary", use_container_width=True)
        if submit_issue:
            bid, mid = book_map[book_label], member_map[member_label]
            if due_date < issue_date:
                st.error("Due date cannot be before issue date.")
            else:
                try:
                    with connect() as conn:
                        current = conn.execute("SELECT available FROM books WHERE book_id=?", (bid,)).fetchone()
                        if current is None or current["available"] < 1:
                            st.error("No copies available now. Refresh and select another book.")
                        else:
                            conn.execute("INSERT INTO issues(book_id,member_id,issue_date,due_date) VALUES(?,?,?,?)",
                                         (bid,mid,issue_date.isoformat(),due_date.isoformat()))
                            conn.execute("UPDATE books SET available=available-1 WHERE book_id=? AND available>0", (bid,))
                            st.success(f"Issue recorded. Due date: {due_date.isoformat()}")
                            st.rerun()
                except sqlite3.Error as exc: safe_error("Could not issue book", exc)
    st.subheader("Open loans to return")
    open_loans = loans_frame()
    if not open_loans.empty:
        open_loans = open_loans[open_loans["Status"].isin(["Issued","Overdue"])]
    if open_loans.empty:
        st.info("There are no open loans to return.")
    else:
        with st.form("return_form"):
            return_map = {f"Loan #{int(r['Loan ID'])} · {r['Book']} — {r['Member']} (due {r['Due date']})": int(r["Loan ID"]) for _,r in open_loans.iterrows()}
            selected_loan = st.selectbox("Select an open loan", list(return_map))
            submit_return = st.form_submit_button("Mark as returned", type="primary", use_container_width=True)
        if submit_return:
            issue_id = return_map[selected_loan]
            try:
                with connect() as conn:
                    loan = conn.execute("SELECT book_id,return_date FROM issues WHERE issue_id=?", (issue_id,)).fetchone()
                    if loan is None or loan["return_date"] is not None:
                        st.error("This loan has already been returned or no longer exists.")
                    else:
                        conn.execute("UPDATE issues SET return_date=? WHERE issue_id=? AND return_date IS NULL", (date.today().isoformat(),issue_id))
                        conn.execute("UPDATE books SET available=MIN(copies,available+1) WHERE book_id=?", (loan["book_id"],))
                        st.success("Return recorded and availability updated."); st.rerun()
            except sqlite3.Error as exc: safe_error("Could not return book", exc)
    st.subheader("Loan register")
    status = st.selectbox("Filter loans", ["All loans","Issued","Overdue","Returned"])
    loan_df = loans_frame()
    if status != "All loans": loan_df = loan_df[loan_df["Status"] == status]
    st.dataframe(loan_df, hide_index=True, use_container_width=True)

# ---------- Transaction History ----------
elif page == "Transaction History":
    st.header("Transaction history")
    st.caption("All issue and return records, newest first.")
    history = loans_frame()
    q = st.text_input("Search history", placeholder="Search book, member, status or date")
    if q.strip():
        mask = history.astype(str).apply(lambda col: col.str.contains(q.strip(), case=False, na=False)).any(axis=1)
        history = history[mask]
    st.dataframe(history, hide_index=True, use_container_width=True)
    st.download_button("Export transaction history CSV", history.to_csv(index=False).encode("utf-8"), "library_transactions.csv", "text/csv")
