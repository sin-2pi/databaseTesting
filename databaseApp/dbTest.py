import sqlite3

def listAvailable(cursor, tableName, idColumn, nameColumn):
    query = f'''
        SELECT {idColumn}, {nameColumn}
        FROM {tableName};
    '''
    try:
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print(f"No entries found in {tableName}.")
        else:
            print(f"--- Available {tableName} ---")
            for row in rows:
                print(f"{row[0]} - {row[1]}")
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")

def promptChoices(tableDictionary, queryDictionary):
    while True:

        tableSelection = input("--- Select a table ---\n"
                            "('exit' to exit.)\n"
                            "1 - Students\n"
                            "2 - Teachers\n"
                            "3 - Courses\n"
                            "4 - Enrollment\n"
                            "5 - Available Queries\n"
                            "Selection: ")
        
        if tableSelection.lower() == 'exit':
            return False

        if tableSelection == "5":

            querySelection = input("--- Available Queries ---\n"
                                "1 - All students in a class\n"
                                "2 - All students for a teacher\n" \
                                "3 - All students in a class with the teacher\n"
                                "Selection: ")
            
            if querySelection in queryDictionary:
                return ("query mode", querySelection)
            else: 
                print("Invalid query.")
                continue
        

        tableChoice = tableDictionary.get(tableSelection)

        if tableChoice:
            return ("table mode", tableChoice)
        else: 
            print("Invalid query.")
            continue
def queryOutput(cursor, queryChoice, choiceDictionary):
    
    if queryChoice == '1':
        listAvailable(cursor, 'Courses', 'course_id', 'course_name')

        courseID = input("Enter the course ID: ")

        try:
            cursor.execute('''
                SELECT Students.student_name
                FROM Students
                JOIN Enrollment ON Students.student_id = Enrollment.student_id
                WHERE Enrollment.course_id = ?;
            ''', (courseID,))
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")

        students = cursor.fetchall()

        query = '''
        SELECT course_name
        FROM Courses
        WHERE course_id = ?;
        '''
        try:
            cursor.execute(query, (courseID,))
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")

        result = cursor.fetchone()

        print(f"--- {choiceDictionary[queryChoice]}: '{result[0]}' ---")
        for student in students:
            print(student[0])  
        print("\n")

    if queryChoice == '2':
        listAvailable(cursor, 'Teachers', 'teacher_id', 'teacher_name')

        teacherID = input("Enter teacher ID: ")
        try:
            cursor.execute('''
            SELECT DISTINCT Students.student_id, Students.student_name
            FROM Students
            JOIN Enrollment ON Students.student_id = Enrollment.student_id
            JOIN Courses ON Enrollment.course_id = Courses.course_id
            WHERE Courses.teacher_id = ?;
                        ''', (teacherID))
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")

        students = cursor.fetchall()
        query = '''
        SELECT teacher_name
        FROM Teachers
        WHERE teacher_id = ?;
        '''
        try:
            cursor.execute(query, (teacherID,))
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")

        result = cursor.fetchone()

        print(f"--- {choiceDictionary[queryChoice]}: '{result[0]}' ---")
        for student in students:
            print(student[1])  
        print("\n")

    if queryChoice == '3':
        listAvailable(cursor, 'Courses', 'course_id', 'course_name')

        courseID = input("Enter course ID: ")
        try:
            cursor.execute('''
            SELECT Students.student_id, Students.student_name, Teachers.teacher_name
            FROM Students
            JOIN Enrollment ON Students.student_id = Enrollment.student_id
            JOIN Courses ON Enrollment.course_id = Courses.course_id
            JOIN Teachers ON Courses.teacher_id = Teachers.teacher_id
            WHERE Enrollment.course_id = ?;
                        ''', (courseID))
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
        
        students = cursor.fetchall()

        try:
            cursor.execute('''
                SELECT Courses.course_name, Teachers.teacher_name
                FROM Courses
                JOIN Teachers ON Courses.teacher_id = Teachers.teacher_id
                WHERE Courses.course_id = ?;
            ''', (courseID,))
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
        
        result = cursor.fetchone()
        courseName, teacherName = result

        print(f"--- {choiceDictionary[queryChoice]}: '{courseName}' with '{teacherName}' ---")
        for student in students:
            print(student[1])  
        print("\n")

def insertToTable(cursor, connection, workingTable):
            attributeList = []

            try:
                cursor.execute(f"PRAGMA table_info('{workingTable}')")
            except sqlite3.Error as e:
                print(f"Database error occurred: {e}")

            attributeData = cursor.fetchall()

            if workingTable == "Enrollment":
                 attributeData = attributeData
            else:
                 attributeData = attributeData[1:]
           
            attributeList = [attribute[1] for attribute in attributeData]

            insertVals = input(f"Enter '{', '.join(attributeList)}': ")

            if insertVals.lower() == 'exit':
                return False 
            
            insertVals = [val.strip() for val in insertVals.split(",")]
            
            if any(val == '' for val in insertVals):
                print("Error: All fields must be non-empty.")
                return True
            
            placeholders = ', '.join('?' for _ in attributeList)

            insert_query = f'''
            INSERT INTO {workingTable} ({', '.join(attributeList)}) 
            VALUES ({placeholders});
            '''
            data = [val for val in insertVals]
            
            try:
                cursor.execute(insert_query, data)
            except sqlite3.Error as e:
                print(f"Database error occurred: {e}")

            connection.commit()
            return True



def main():
    options = {
    '1': "Students",
    '2': "Teachers",
    '3': "Courses",
    '4': "Enrollment",
    '5': "Query"
    }

    queryChoices = {
    '1': "All students in a class",
    '2': "All students for a teacher",
    '3': "All students in a class with a teacher"
    }

    # Tables are created initally here, then the input loop is ran.
    with sqlite3.connect('enrollment.db') as connection:

        cursor = connection.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS Teachers (
                teacher_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_name TEXT,
                teacher_age  TEXT
            );

            CREATE TABLE IF NOT EXISTS Students (
                student_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name  TEXT,
                student_age   TEXT
            );

            CREATE TABLE IF NOT EXISTS Courses (
                course_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name    TEXT,
                course_credits INTEGER,
                teacher_id     INTEGER,
                FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id)
            );

            CREATE TABLE IF NOT EXISTS Enrollment (
                student_id INTEGER,
                course_id  INTEGER,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES Students(student_id),
                FOREIGN KEY (course_id)  REFERENCES Courses(course_id)
            );
        """)

        connection.commit()

        while True:
            selection = promptChoices(options, queryChoices)
            
            if selection is False:
                break

            currentMode, userSelection = selection

            if currentMode == "query mode":
                queryOutput(cursor, userSelection, queryChoices)

            elif currentMode == "table mode":
                insertResult = insertToTable(cursor, connection, userSelection)
                if insertResult is False:
                    break

if __name__ == "__main__":
     main()