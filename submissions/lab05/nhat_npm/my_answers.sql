-- Q1 (all columns of all students)
SELECT * FROM students;

-- Q2 (name and year of every student)
SELECT name, year FROM students;

-- Q3 (names of CS students)
SELECT name FROM students WHERE program = 'CS';

-- Q4 (name and year of students in year 3 or higher)
SELECT name, year FROM students WHERE year >= 3;

-- Q5 (student names, Z to A)
SELECT name FROM students ORDER BY name DESC;

-- Q6 (title and credits of 4-credit courses, by title)
SELECT title, credits FROM courses WHERE credits = 4 ORDER BY title;

-- Q7 (how many students?)
SELECT COUNT(*) FROM students;

-- Q8 (number of students per program, by program)
SELECT program, COUNT(*) FROM students GROUP BY program ORDER BY program;

-- Q9 (average grade in CSC10004, rounded to 2 decimals)
SELECT ROUND(AVG(grade), 2) FROM enrollments WHERE course_code = 'CSC10004';

-- Q10 (student_id and course_code of enrollments without a grade, by student_id)
SELECT student_id, course_code FROM enrollments WHERE grade IS NULL ORDER BY student_id;

-- Q11 (name and grade of graded students in CSC10014, by name)
SELECT students.name, enrollments.grade
FROM enrollments
JOIN students ON students.id = enrollments.student_id
WHERE enrollments.course_code = 'CSC10014' AND enrollments.grade IS NOT NULL
ORDER BY students.name;

-- Q12 (course title and number of enrolled students, most first, then by title)
SELECT courses.title, COUNT(enrollments.student_id) AS student_count
FROM courses
JOIN enrollments ON enrollments.course_code = courses.code
GROUP BY courses.code, courses.title
ORDER BY student_count DESC, courses.title;

-- Q13 (names of students with a grade below 5, by name)
SELECT DISTINCT students.name
FROM students
JOIN enrollments ON enrollments.student_id = students.id
WHERE enrollments.grade < 5
ORDER BY students.name;

-- Q14 (each student's name and total credits enrolled, most first, then by name)
SELECT students.name, COALESCE(SUM(courses.credits), 0) AS total_credits
FROM students
LEFT JOIN enrollments ON enrollments.student_id = students.id
LEFT JOIN courses ON courses.code = enrollments.course_code
GROUP BY students.id, students.name
ORDER BY total_credits DESC, students.name;

-- Q15 (names of students NOT enrolled in CSC10014, by name)
SELECT students.name
FROM students
WHERE NOT EXISTS (
    SELECT 1 FROM enrollments
    WHERE enrollments.student_id = students.id
      AND enrollments.course_code = 'CSC10014'
)
ORDER BY students.name;
