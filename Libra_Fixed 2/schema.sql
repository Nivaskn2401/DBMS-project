-- Library Management System (MySQL 8+)
CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(100) NOT NULL,
    category VARCHAR(80) NOT NULL DEFAULT 'General',
    isbn VARCHAR(20) UNIQUE,
    copies INT NOT NULL DEFAULT 1,
    available INT NOT NULL DEFAULT 1,
    CONSTRAINT chk_book_copies CHECK (copies >= 0),
    CONSTRAINT chk_book_available CHECK (available >= 0 AND available <= copies)
);

CREATE TABLE IF NOT EXISTS members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(15),
    joined_on DATE NOT NULL DEFAULT (CURRENT_DATE)
);

CREATE TABLE IF NOT EXISTS issues (
    issue_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE NULL,
    CONSTRAINT fk_issue_book FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE RESTRICT,
    CONSTRAINT fk_issue_member FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE RESTRICT
);

CREATE INDEX idx_issues_member ON issues(member_id);
CREATE INDEX idx_issues_book ON issues(book_id);

-- Sample records (run once; remove or skip if already inserted)
INSERT INTO books (title, author, category, isbn, copies, available) VALUES
('Database System Concepts', 'Abraham Silberschatz', 'Computer Science', '9780078022159', 3, 3),
('Wings of Fire', 'A. P. J. Abdul Kalam', 'Biography', '9788173711466', 2, 2),
('The Alchemist', 'Paulo Coelho', 'Fiction', '9780061122415', 4, 4),
('Introduction to Algorithms', 'Thomas H. Cormen', 'Computer Science', '9780262046305', 2, 2);

INSERT INTO members (name, email, phone) VALUES
('Arun Kumar', 'arun@example.com', '9876543210'),
('Priya Sharma', 'priya@example.com', '9876501234');

-- Viva/demo queries
SELECT * FROM books;
SELECT * FROM members;
SELECT i.issue_id, b.title, m.name, i.issue_date, i.due_date, i.return_date
FROM issues AS i
JOIN books AS b ON b.book_id = i.book_id
JOIN members AS m ON m.member_id = i.member_id;
SELECT * FROM issues WHERE return_date IS NULL;
SELECT * FROM issues WHERE return_date IS NULL AND due_date < CURRENT_DATE;
SELECT category, COUNT(*) AS title_count FROM books GROUP BY category;
