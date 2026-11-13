-- Lab 5, Part C: SQL practice on school.db (Q1-Q15)
-- Check answers with:  python check.py

-- Q1 (all columns of all students)
SELECT * FROM students;

-- Q2 (only name and year of every student)
SELECT name, year FROM students;

-- Q3 (names of CS students)
SELECT name FROM students WHERE program = 'CS';

-- Q4 (name and year of students in year 3 or higher)
SELECT name, year FROM students WHERE year >= 3;

-- Q5 (student names from Z to A)
SELECT name FROM students ORDER BY name DESC;

-- Q6 (title and credits of 4-credit courses, sorted by title)
SELECT title, credits FROM courses WHERE credits = 4 ORDER BY title;

-- Q7 (how many students?)
SELECT COUNT(*) FROM students;

-- Q8 (number of students per program, sorted by program)
SELECT program, COUNT(*) FROM students GROUP BY program ORDER BY program;

-- Q9 (average grade in CSC10004, rounded to 2 decimals)
SELECT ROUND(AVG(grade), 2) FROM enrollments WHERE course_code = 'CSC10004';

-- Q10 (student_id and course_code of enrollments without a grade, sorted by student_id)
SELECT student_id, course_code FROM enrollments WHERE grade IS NULL ORDER BY student_id;

-- Q11 (name and grade of graded students in CSC10014, by name)
SELECT s.name, e.grade
FROM enrollments e
JOIN students s ON s.id = e.student_id
WHERE e.course_code = 'CSC10014' AND e.grade IS NOT NULL
ORDER BY s.name;

-- Q12 (each course title with the number of enrolled students, most first, then by title)
SELECT c.title, COUNT(*) AS enrolled
FROM enrollments e
JOIN courses c ON c.code = e.course_code
GROUP BY c.code, c.title
ORDER BY enrolled DESC, c.title;

-- Q13 (names of students with a grade below 5)
SELECT DISTINCT s.name
FROM enrollments e
JOIN students s ON s.id = e.student_id
WHERE e.grade < 5
ORDER BY s.name;

-- Q14 (each student's name and total credits enrolled, most first, then by name)
SELECT s.name, COALESCE(SUM(c.credits), 0) AS credits
FROM students s
LEFT JOIN enrollments e ON e.student_id = s.id
LEFT JOIN courses c ON c.code = e.course_code
GROUP BY s.id, s.name
ORDER BY credits DESC, s.name;

-- Q15 (names of students not enrolled in CSC10014)
SELECT s.name
FROM students s
LEFT JOIN enrollments e ON e.student_id = s.id AND e.course_code = 'CSC10014'
WHERE e.student_id IS NULL
ORDER BY s.name;
