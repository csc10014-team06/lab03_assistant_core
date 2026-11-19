"""Lab 5, Part D warm-up: talk to a database from Python with the sqlite3 module.

Complete the four functions. Run the tests with:  pytest -q test_school_repo.py
Rule: ALWAYS use ? placeholders for values — never build SQL with + or f-strings.
"""

import sqlite3


def connect(path: str = "school.db") -> sqlite3.Connection:
    """Open a connection to the SQLite database at ``path``."""
    return sqlite3.connect(path)


def students_in_program(con: sqlite3.Connection, program: str) -> list[str]:
    """Return names of students in ``program``, sorted A to Z."""
    rows = con.execute("SELECT name FROM students WHERE program = ? ORDER BY name", (program,)).fetchall()
    return [r[0] for r in rows]


def add_student(con: sqlite3.Connection, name: str, year: int, program: str) -> int:
    """Insert a student and return the new row id."""
    cur = con.execute(
        "INSERT INTO students (name, year, program) VALUES (?, ?, ?)",
        (name, year, program),
    )
    con.commit()
    assert cur.lastrowid is not None
    return cur.lastrowid


def average_grade(con: sqlite3.Connection, code: str) -> float | None:
    """Return the rounded average grade for ``code``, or None if ungraded/absent."""
    row = con.execute("SELECT AVG(grade) FROM enrollments WHERE course_code = ?", (code,)).fetchone()
    if row is None or row[0] is None:
        return None
    return round(float(row[0]), 2)


def transcript(con: sqlite3.Connection, student_id: int) -> list[tuple[str, int, float | None]]:
    """Return ``(title, credits, grade)`` tuples for ``student_id``, ordered by course title."""
    return con.execute(
        """
        SELECT c.title, c.credits, e.grade
        FROM enrollments e
        JOIN courses c ON c.code = e.course_code
        WHERE e.student_id = ?
        ORDER BY c.title
        """,
        (student_id,),
    ).fetchall()
