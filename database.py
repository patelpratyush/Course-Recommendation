import sqlite3
from tkinter.tix import TEXT

conn = sqlite3.connect('course.db')
c = conn.cursor()
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
        FOREIGN KEY (user_id) REFERENCES user (id)
    )""")

# conn = sqlite3.connect('course.db')
# c = conn.cursor()

# # Drop the prerequisites table if it exists
# c.execute("DROP TABLE IF EXISTS courses")
# c.execute("DROP TABLE IF EXISTS prerequisites")
# c.execute("DROP TABLE IF EXISTS user_courses")
# c.execute("DROP TABLE IF EXISTS schedule")
# c.execute("DROP TABLE IF EXISTS users")


conn.commit()
conn.close()

def add_course(course_code, course_title):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()
    c.execute("INSERT INTO courses (course_code, course_title) VALUES (?, ?)", (course_code, course_title))
    conn.commit() 
    conn.close()

def course_exists(course_code):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()
    c.execute("SELECT * FROM courses WHERE course_code = ?", (course_code,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

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

def add_schedule(course_codes):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    for course_code in course_codes:    
        course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()[0]
        c.execute("INSERT INTO schedule (course_id) VALUES (?)", (course_id,))
    conn.commit()
    conn.close()

def recommendation(user):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    # Get the user ID
    user_id = c.execute("SELECT id FROM users WHERE name = ?", (user,)).fetchone()
    print("User ID:", user_id)

    if not user_id:
        print("User not found.")
        return []

    # Select courses from the schedule table that the user has not taken
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
    print("Recommended courses before filtering:", recommended_courses)

    # Find the prerequisites for each recommended course
    courses_with_prerequisites = []
    for course_id, course_code, course_title in recommended_courses:
        # Check if the user has taken all the prerequisites for the course
        c.execute("""
            SELECT prereq_course_id
            FROM prerequisites 
            WHERE prereq_course = ?
            EXCEPT
            SELECT course_id 
            FROM user_courses 
            WHERE user_id = ?
        """, (course_id, user_id[0]))  #FIX THE TABLE COURSE ID SHOULD BE ON LEFT AND COURSE ID OF PREREQ SHOULD BE ON RIGHT

        missing_prerequisites = c.fetchall()
        # print(missing_prerequisites[-1])

        # If there are no missing prerequisites or the last one is -1, add the course
        if not missing_prerequisites or missing_prerequisites[-1][0] == -1:
            courses_with_prerequisites.append((course_id, course_code, course_title))

    conn.close()

    print("Recommended courses after filtering prerequisites:", courses_with_prerequisites)
    return courses_with_prerequisites



def insert_user_and_courses(username, course_codes):

    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    c.execute("INSERT INTO users (name) VALUES (?)", (username,))
    user_id = c.lastrowid  # Get the id of the newly inserted user

    # Insert course codes into user_courses table
    for course_code in course_codes:
        # Get the course_id for the given course_code
        course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()
        if course_id:
            # Insert the user_id and course_id into user_courses table
            c.execute("INSERT INTO user_courses (user_id, course_id) VALUES (?, ?)", (user_id, course_id[0]))

    conn.commit()
    conn.close()

def add_course_for_user(user, course_code):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    # Check if the user exists
    user_id = c.execute("SELECT id FROM users WHERE name = ?", (user,)).fetchone()
    if not user_id:
        print("User not found.")
        conn.close()
        return

    # Check if the course exists
    course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()
    if not course_id:
        print("Course not found.")
        conn.close()
        return

    # Insert the user_id and course_id into user_courses table
    c.execute("INSERT INTO user_courses (user_id, course_id) VALUES (?, ?)", (user_id[0], course_id[0]))

    conn.commit()
    conn.close()

def update_schedule(new_course_codes):
    conn = sqlite3.connect('course.db')
    c = conn.cursor()

    # Clear the existing schedule
    c.execute("DELETE FROM schedule")

    # Insert the new courses into the schedule table
    for course_code in new_course_codes:
        course_id = c.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()
        if course_id:
            c.execute("INSERT INTO schedule (course_id) VALUES (?)", (course_id[0],))

    conn.commit()
    conn.close()

# courses
#     id : INTEGER
#     code : CSE 015, MATH 131
#     title : Discrete Math

# 111|CSE 111|Database Systems

# prerequisites
#     course_id : INTEGER
#     course_code : CSE 015, MATH 131 #not needed
#     prereq_course_id : INTEGER
#     prereq_course_code : CSE 015, MATH 131

# CSE 111|CSE 031
# CSE 111|MATH 024
# CSE 111|CSE 100

# semesters
#     id : INTEGER
#     name : 2024 Spring
    
# 11|2024 Spring

# schedule
#       term : TEXT
#     course_id : INTEGER

# historical_schedule
#     term : TEXT
#     course_id : INTEGER


# schedule_historical
#     course_id : INTEGER
#     course_code : CSE 015, MATH 131
#     semester_id : INTEGER

# 111|CSE 111|10
# 111|CSE 111|8

#users
    # id : INTEGER
    # name : TEXT

#user_courses
    # user_id : INTEGER
    # course_id : INTEGER
    # semester_id : INTEGER

#POPULATE THE DATABASES, THEN WORK ON RECOMMENDATION SQL SQUERY THAT CONNECTS USER TAKEN COURSES TO SEMESTER AND PREREQ


