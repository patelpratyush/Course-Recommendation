import sqlite3

conn = sqlite3.connect('course.db')
c = conn.cursor()

# Check if 'courses' table exists; if not, create necessary tables
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courses'")
table_exists = c.fetchone()

if not table_exists:
    c.execute("""CREATE TABLE courses(
        course_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        course_title TEXT
    )""")

    c.execute("""CREATE TABLE prerequisites(
        prereq_course INTEGER NOT NULL,
        prereq_course_code TEXT,
        prereq_course_id INTEGER,
        FOREIGN KEY (prereq_course) REFERENCES courses (course_id)
    )""")

    c.execute("""CREATE TABLE schedule(
        course_id INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES courses (course_id)
    )""")

    c.execute("""CREATE TABLE users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )""")

    c.execute("""CREATE TABLE user_courses(
        course_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES courses (course_id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )""")

conn.commit()
conn.close()

# Function to add a course to the 'courses' table
def add_course(course_code, course_title):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()
    c.execute("INSERT INTO courses (course_code, course_title) VALUES (?, ?)", (course_code, course_title))
    conn.commit()
    conn.close()

# Function to check if a course exists in the 'courses' table
def course_exists(course_code):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()
    c.execute("SELECT * FROM courses WHERE course_code = ?", (course_code,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Function to add prerequisites for a course
def add_prerequisites(prereq_course_codes, course_code):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()[0]

    for prereq_course_code in prereq_course_codes:
        if prereq_course_code == 'None':
            prereq_course_id = -1
        else:
            prereq_course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (prereq_course_code,)).fetchone()[0]
        c.execute("""
            INSERT INTO prerequisites (prereq_course, prereq_course_code, prereq_course_id)
            VALUES (?, ?, ?)
            """, (course_id, prereq_course_code, prereq_course_id))

    conn.commit()
    conn.close()

# Function to check if a course has prerequisites
def has_prerequisite(course_code):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()[0]
    
    if course_id:
        c.execute("SELECT * FROM prerequisites WHERE prereq_course = ? ", (course_id,))
        exists = c.fetchone() is not None
    else:
        exists = False

    conn.close()
    return exists

# Function to add courses to the schedule
def add_schedule(course_codes):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    for course_code in course_codes:    
        course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()[0]
        c.execute("INSERT INTO schedule (course_id) VALUES (?)", (course_id,))

    conn.commit()
    conn.close()

# Function to recommend courses for a user based on their taken courses and prerequisites
def recommendation(user):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    user_id = c.execute("SELECT id FROM users WHERE name = ?", (user,)).fetchone()

    if not user_id:
        return []

    c.execute("""
        SELECT schedule.course_id, courses.course_code, courses.course_title 
        FROM schedule 
        LEFT JOIN courses ON schedule.course_id = courses.course_id
        EXCEPT
        SELECT user_courses.course_id, courses.course_code, courses.course_title 
        FROM user_courses
        JOIN courses ON user_courses.course_id = courses.course_id
        WHERE user_courses.user_id = ?
    """, (user_id[0],))

    recommended_courses = c.fetchall()

    courses_with_prerequisites = []
    for course_id, course_code, course_title in recommended_courses:
        c.execute("""
            SELECT prereq_course_id
            FROM prerequisites 
            WHERE prereq_course = ?
            EXCEPT
            SELECT course_id 
            FROM user_courses 
            WHERE user_id = ?
        """, (course_id, user_id[0]))

        missing_prerequisites = c.fetchall()

        if not missing_prerequisites or missing_prerequisites[-1][0] == -1:
            courses_with_prerequisites.append((course_id, course_code, course_title))

    conn.close()

    return courses_with_prerequisites

# Function to insert a user and their enrolled courses
def insert_user_and_courses(username, course_codes):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    c.execute("INSERT INTO users (name) VALUES (?)", (username,))
    user_id = c.lastrowid

    for course_code in course_codes:
        course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()
        if course_id:
            c.execute("INSERT INTO user_courses (user_id, course_id) VALUES (?, ?)", (user_id, course_id[0]))

    conn.commit()
    conn.close()

# Function to add a course for a user
def add_course_for_user(user, course_code):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    user_id = c.execute("SELECT id FROM users WHERE name = ?", (user,)).fetchone()
    if not user_id:
        conn.close()
        return

    course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()
    if not course_id:
        conn.close()
        return

    c.execute("INSERT INTO user_courses (user_id, course_id) VALUES (?, ?)", (user_id[0], course_id[0]))

    conn.commit()
    conn.close()

# Function to update the schedule with new courses
def update_schedule(new_course_codes):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    c.execute("DELETE FROM schedule")

    for course_code in new_course_codes:
        course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()
        if course_id:
            c.execute("INSERT INTO schedule (course_id) VALUES (?)", (course_id[0],))

    conn.commit()
    conn.close()
