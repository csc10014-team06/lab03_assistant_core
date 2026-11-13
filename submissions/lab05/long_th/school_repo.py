"""Lab 5, Part D warm-up: talk to a database from Python with the sqlite3 module.

Complete the four functions. Run the tests with:  pytest -q test_school_repo.py
Rule: ALWAYS use ? placeholders for values — never build SQL with + or f-strings.
"""
import sqlite3


def connect(path: str = "school.db") -> sqlite3.Connection:
    return sqlite3.connect(path)


def students_in_program(con: sqlite3.Connection, program: str) -> list[str]:
    """Names of students in `program`, sorted A→Z."""
    rows = con.execute("SELECT name FROM students WHERE program = ? ORDER BY name", (program,)).fetchall()
    return [r[0] for r in rows]                     # example — already done


def add_student(con: sqlite3.Connection, name: str, year: int, program: str) -> int:
    """Insert a student and return the new id."""
    cur = con.execute("INSERT INTO students (name, year, program) VALUES (?, ?, ?)", (name, year, program))
    con.commit()
    return cur.lastrowid


def average_grade(con: sqlite3.Connection, course_code: str) -> float | None:
    """Average grade in a course (ignoring NULL), rounded to 2 decimals; None if no grades."""
    val = con.execute(
        "SELECT AVG(grade) FROM enrollments WHERE course_code = ?",
        (course_code,),
    ).fetchone()[0]

    return round(val, 2) if val is not None else None


def transcript(con: sqlite3.Connection, student_id: int) -> list[tuple[str, int, float | None]]:
    """(course title, credits, grade) for one student, sorted by title. Needs a JOIN."""
    query = """
        SELECT courses.title, courses.credits, enrollments.grade
        FROM enrollments
        JOIN courses ON enrollments.course_code = courses.code
        WHERE enrollments.student_id = ?
        ORDER BY courses.title
    """
    return con.execute(query, (student_id,)).fetchall()
