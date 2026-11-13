"""Lab 5, Part D warm-up: talk to a database from Python with sqlite3."""

import sqlite3


def connect(path: str = "school.db") -> sqlite3.Connection:
    return sqlite3.connect(path)


def students_in_program(con: sqlite3.Connection, program: str) -> list[str]:
    """Return names in a program, sorted alphabetically."""
    rows = con.execute(
        "SELECT name FROM students WHERE program = ? ORDER BY name",
        (program,),
    ).fetchall()
    return [row[0] for row in rows]


def add_student(con: sqlite3.Connection, name: str, year: int, program: str) -> int:
    """Insert a student and return the new id."""
    cur = con.execute(
        "INSERT INTO students (name, year, program) VALUES (?, ?, ?)",
        (name, year, program),
    )
    con.commit()
    return int(cur.lastrowid)


def average_grade(con: sqlite3.Connection, course_code: str) -> float | None:
    """Return the course average rounded to two decimals, or None without grades."""
    row = con.execute(
        "SELECT AVG(grade) FROM enrollments WHERE course_code = ?",
        (course_code,),
    ).fetchone()
    average = row[0]
    return None if average is None else round(float(average), 2)


def transcript(
    con: sqlite3.Connection, student_id: int
) -> list[tuple[str, int, float | None]]:
    """Return a student's (course title, credits, grade) rows ordered by title."""
    rows = con.execute(
        """SELECT courses.title, courses.credits, enrollments.grade
           FROM enrollments
           JOIN courses ON courses.code = enrollments.course_code
           WHERE enrollments.student_id = ?
           ORDER BY courses.title""",
        (student_id,),
    ).fetchall()
    return [(title, credits, grade) for title, credits, grade in rows]
