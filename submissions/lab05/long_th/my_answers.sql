-- Write ONE query under each marker. Do not delete the markers.
-- Check with:  python check.py
-- Q1  (all columns of all students)
SELECT * FROM students;

-- Q2  (name and year of every student)
SELECT name, year FROM students;

-- Q3  (names of CS students)
SELECT name FROM students where program = 'CS';

-- Q4  (name and year of students in year 3 or higher)
SELECT name, year from students where year >= 3;

-- Q5  (student names, Z to A)
SELECT name from students ORDER by name DESC;
-- Q6  (title and credits of 4-credit courses, by title)
SELECT title, credits FROM courses where credits = 4 ORDER BY title;

-- Q7  (how many students?)
SELECT COUNT(*) FROM students;
-- Q8  (number of students per program, by program)
SELECT program, COUNT(*) FROM students GROUP BY program ORDER BY program;
-- Q9  (average grade in CSC10004, rounded to 2 decimals)
SELECT ROUND(AVG(grade), 2) FROM enrollments where course_code = 'CSC10004';
-- Q10 (student_id and course_code of enrollments without a grade, by student_id)
SELECT student_id, course_code from enrollments where grade is null ORDER BY student_id;
-- Q11 (name and grade of graded students in CSC10014, by name)
SELECT s.name, e.grade FROM enrollments e JOIN students s ON s.id = e.student_id where course_code = 'CSC10014' and grade is not null order by name;
-- Q12 (course title and number of enrolled students, most first, then by title)
SELECT title, COUNT(*) as num_students
FROM courses c
JOIN enrollments e
    ON c.code = e.course_code
GROUP BY c.code, c.title
ORDER BY num_students DESC, title ASC;

-- Q13 (names of students with a grade below 5, by name)
SELECT name from enrollments e
JOIN students s ON s.id = e.student_id where grade < 5 order by name;
-- Q14 (each student's name and total credits enrolled, most first, then by name)
SELECT name, SUM(c.credits) AS credits
FROM enrollments e
JOIN students s on s.id = e.student_id
JOIN courses c on c.code = e.course_code
GROUP BY s.id
ORDER BY credits DESC, name ASC;
-- Q15 (names of students NOT enrolled in CSC10014, by name)
SELECT s.name
FROM students s
LEFT JOIN enrollments e on e.student_id = s.id AND e.course_code = 'CSC10014'
WHERE e.student_id IS NULL
ORDER BY s.name;
