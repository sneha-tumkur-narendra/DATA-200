import csv
import os
import base64
import time
import statistics
import unittest

# 1. SECURITY (Encryption/Decryption)

SECRET_KEY = "SJSU_DATA200_KEY"

def encrypt_password(password):
    """
    Encrypts a password using a simple XOR cipher and encodes in base64.
    """
    encrypted = []
    for i, char in enumerate(password):
        key_char = SECRET_KEY[i % len(SECRET_KEY)]
        encrypted_char = chr(ord(char) ^ ord(key_char))
        encrypted.append(encrypted_char)
    
    # Base64 encode to ensure it's a storable string
    return base64.b64encode("".join(encrypted).encode()).decode()

def decrypt_password(encrypted_password):
    """
    Decrypts a base64-encoded, XOR-encrypted password.
    """
    # Base64 decode
    try:
        encrypted_str = base64.b64decode(encrypted_password.encode()).decode()
    except Exception:
        return None # Handle invalid base64 string

    decrypted = []
    for i, char in enumerate(encrypted_str):
        key_char = SECRET_KEY[i % len(SECRET_KEY)]
        decrypted_char = chr(ord(char) ^ ord(key_char))
        decrypted.append(decrypted_char)
        
    return "".join(decrypted)


# 2. DATA CLASSES

class Student:
    """Represents a student record"""
    def __init__(self, email, first_name, last_name, course_id, grade, marks):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.course_id = course_id
        self.grade = grade
        self.marks = int(marks)

class Course:
    """Represents a course record"""
    def __init__(self, course_id, course_name, description):
        self.course_id = course_id
        self.course_name = course_name
        self.description = description

class Professor:
    """Represents a professor record"""
    def __init__(self, email, name, rank, course_id):
        self.email = email
        self.name = name
        self.rank = rank
        self.course_id = course_id

class LoginUser:
    """Represents a login user record"""
    def __init__(self, user_id, password, role):
        self.user_id = user_id
        self.password = password
        self.role = role

# 3. DATA MANAGER (CSV Read/Write)

# Define CSV filenames
STUDENT_FILE = 'students.csv'
COURSE_FILE = 'course.csv'
PROF_FILE = 'professors.csv'
LOGIN_FILE = 'login.csv'

# Define headers based on PDF
STUDENT_HEADERS = ['Email address', 'First name', 'Last name', 'Course.id', 'grades', 'Marks']
COURSE_HEADERS = ['Course id', 'Course_name', 'Description']
PROF_HEADERS = ['Professor id', 'Professor Name', 'Rank', 'Course.id']
LOGIN_HEADERS = ['User id', 'Password', 'Role']

def load_data(filename, headers, class_constructor):
    """Generic function to load data from a CSV file."""
    if not os.path.exists(filename):
        # Create file with headers if it doesn't exist
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        return []

    data = []
    try:
        with open(filename, 'r', newline='') as f:
            reader = csv.DictReader(f)
            # Verify headers
            if reader.fieldnames != headers:
                # Handle incorrect file format
                if not reader.fieldnames: # File is empty, just has headers
                     return []
                # Reset and use file's headers as keys
                f.seek(0)
                # Re-read headers
                new_headers = next(csv.reader(f))
                reader = csv.DictReader(f, fieldnames=new_headers)

            for row in reader:
                # Handle potential empty rows
                if not any(row.values()):
                    continue
                try:
                    data.append(class_constructor(row))
                except TypeError as e:
                    print(f"Error loading row: {row}. Mismatch: {e}")
                except ValueError as e:
                    print(f"Error loading row (bad data): {row}. Error: {e}")

    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    return data

def save_data(filename, data, headers):
    """Generic function to save data to a CSV file."""
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
    except IOError as e:
        print(f"Error writing to {filename}: {e}")


# These functions now get a list of dictionaries from load_data and manually construct the class objects.

def load_students():
    # class_constructor (lambda r: r) returns the row dictionary
    raw_data = load_data(STUDENT_FILE, STUDENT_HEADERS, lambda r: r)
    students = []
    for r in raw_data:
        try:
            # Manually map dictionary keys to class __init__ arguments
            students.append(Student(
                email=r['Email address'],
                first_name=r['First name'],
                last_name=r['Last name'],
                course_id=r['Course.id'],
                grade=r['grades'],
                marks=r['Marks']
            ))
        except KeyError:
            pass
    return students

def save_students(students):
    # Convert Student objects back to dicts matching CSV headers
    data_to_save = [
        {'Email address': s.email, 'First name': s.first_name, 'Last name': s.last_name,
         'Course.id': s.course_id, 'grades': s.grade, 'Marks': s.marks}
        for s in students
    ]
    save_data(STUDENT_FILE, data_to_save, STUDENT_HEADERS)

def load_courses():
    raw_data = load_data(COURSE_FILE, COURSE_HEADERS, lambda r: r)
    courses = []
    for r in raw_data:
        try:
            courses.append(Course(
                course_id=r['Course id'],
                course_name=r['Course_name'],
                description=r['Description']
            ))
        except KeyError:
             pass
    return courses

def save_courses(courses):
    data_to_save = [
        {'Course id': c.course_id, 'Course_name': c.course_name, 'Description': c.description}
        for c in courses
    ]
    save_data(COURSE_FILE, data_to_save, COURSE_HEADERS)

def load_professors():
    raw_data = load_data(PROF_FILE, PROF_HEADERS, lambda r: r)
    professors = []
    for r in raw_data:
        try:
            professors.append(Professor(
                email=r['Professor id'],
                name=r['Professor Name'],
                rank=r['Rank'],
                course_id=r['Course.id']
            ))
        except KeyError:
            pass
    return professors

def save_professors(professors):
    data_to_save = [
        {'Professor id': p.email, 'Professor Name': p.name, 'Rank': p.rank, 'Course.id': p.course_id}
        for p in professors
    ]
    save_data(PROF_FILE, data_to_save, PROF_HEADERS)

def load_users():
    raw_data = load_data(LOGIN_FILE, LOGIN_HEADERS, lambda r: r)
    users = []
    for r in raw_data:
        try:
            users.append(LoginUser(
                user_id=r['User id'],
                password=r['Password'],
                role=r['Role']
            ))
        except KeyError:
            pass
    return users

def save_users(users):
    data_to_save = [
        {'User id': u.user_id, 'Password': u.password, 'Role': u.role}
        for u in users
    ]
    save_data(LOGIN_FILE, data_to_save, LOGIN_HEADERS)


# 4. APPLICATION LOGIC (CheckMyGradeApp Class)

class CheckMyGradeApp:
    def __init__(self):
        self.students = load_students()
        self.courses = load_courses()
        self.professors = load_professors()
        self.users = load_users()
        self.current_user = None

    # Authentication
    
    def register_user(self, email, password, role):
        """Registers a new user."""
        if self.find_user(email):
            return False, "User ID (email) already exists."
        
        encrypted_pass = encrypt_password(password) #
        new_user = LoginUser(user_id=email, password=encrypted_pass, role=role)
        self.users.append(new_user)
        save_users(self.users)
        return True, "User registered successfully."

    def login(self, email, password):
        """Logs in a user."""
        user = self.find_user(email)
        if user:
            decrypted_pass = decrypt_password(user.password) #
            if decrypted_pass == password:
                self.current_user = user
                return True
        return False

    def logout(self):
        """Logs out the current user."""
        self.current_user = None

    def find_user(self, email):
        """Helper to find a user by email."""
        for user in self.users:
            if user.user_id == email:
                return user
        return None

    # Student Management

    def find_student(self, email):
        """Helper to find a student by email."""
        for student in self.students:
            if student.email == email:
                return student
        return None

    def add_student(self, email, first_name, last_name, course_id, grade, marks):
        """Adds a new student.""" #
        if not email or self.find_student(email): #
            print("Error: Student email must be unique and not null.")
            return False
        
        # Check if course exists
        if not self.find_course(course_id):
            print(f"Error: Course ID {course_id} does not exist.")
            return False
            
        student = Student(email, first_name, last_name, course_id, grade, int(marks))
        self.students.append(student)
        save_students(self.students) 
        return True

    def modify_student(self, email, new_first_name, new_last_name, new_course_id, new_grade, new_marks):
        """Modifies an existing student's record.""" 
        student = self.find_student(email)
        if student:
            # Only update fields that are not empty
            if new_first_name: student.first_name = new_first_name
            if new_last_name: student.last_name = new_last_name
            if new_course_id: student.course_id = new_course_id
            if new_grade: student.grade = new_grade
            if new_marks is not None: student.marks = int(new_marks)
            
            save_students(self.students) 
            return True
        return False

    def delete_student(self, email):
        """Deletes a student record.""" 
        student = self.find_student(email)
        if student:
            self.students.remove(student)
            save_students(self.students) 
            return True
        return False

    # Course Management

    def find_course(self, course_id):
        """Helper to find a course by ID."""
        for course in self.courses:
            if course.course_id == course_id:
                return course
        return None

    def add_course(self, course_id, course_name, description):
        """Adds a new course.""" 
        if not course_id or self.find_course(course_id): 
            print("Error: Course ID must be unique and not null.")
            return False
        
        course = Course(course_id, course_name, description)
        self.courses.append(course)
        save_courses(self.courses) 
        return True

    def modify_course(self, course_id, new_name, new_description):
        """Modifies an existing course.""" 
        course = self.find_course(course_id)
        if course:
            if new_name: course.course_name = new_name
            if new_description: course.description = new_description
            save_courses(self.courses)
            return True
        return False

    def delete_course(self, course_id):
        """Deletes a course."""
        course = self.find_course(course_id)
        if course:
            self.courses.remove(course)
            save_courses(self.courses)
            return True
        return False

    # Professor Management

    def find_professor(self, email):
        """Helper to find a professor by email."""
        for prof in self.professors:
            if prof.email == email:
                return prof
        return None

    def add_professor(self, email, name, rank, course_id):
        """Adds a new professor."""
        if not email or self.find_professor(email):
            print("Error: Professor email must be unique and not null.")
            return False
        
        prof = Professor(email, name, rank, course_id)
        self.professors.append(prof)
        save_professors(self.professors)
        return True

    def modify_professor(self, email, new_name, new_rank, new_course_id):
        """Modifies an existing professor."""
        prof = self.find_professor(email)
        if prof:
            if new_name: prof.name = new_name
            if new_rank: prof.rank = new_rank
            if new_course_id: prof.course_id = new_course_id
            save_professors(self.professors)
            return True
        return False

    def delete_professor(self, email):
        """Deletes a professor."""
        prof = self.find_professor(email)
        if prof:
            self.professors.remove(prof)
            save_professors(self.professors)
            return True
        return False

    # Search & Sort

    def search_student(self, email):
        """Searches for a student and prints search time.""" 
        start_time = time.perf_counter()
        
        student = self.find_student(email)
        
        end_time = time.perf_counter()
        search_time = (end_time - start_time) * 1000 # in milliseconds
        
        print(f"\n--- Search Time: {search_time:.4f} ms ---") 
        return student

    def sort_students(self, by='name', descending=False):
        """Sorts student records and prints sort time.""" 
        start_time = time.perf_counter()
        
        if by == 'name':
            key_func = lambda s: s.last_name.lower()
        elif by == 'marks':
            key_func = lambda s: s.marks
        else:
            print("Invalid sort key. Defaulting to name.")
            key_func = lambda s: s.last_name.lower()
            
        sorted_list = sorted(self.students, key=key_func, reverse=descending)
        
        end_time = time.perf_counter()
        sort_time = (end_time - start_time) * 1000 # in milliseconds
        
        print(f"\n--- Sort Time: {sort_time:.4f} ms ---") 
        return sorted_list

    # Statistics & Reporting

    def get_course_statistics(self, course_id):
        """Calculates average and median score for a course.""" #
        scores = [s.marks for s in self.students if s.course_id == course_id]
        
        if not scores:
            return None, None
            
        average = statistics.mean(scores)
        median = statistics.median(scores)
        
        return average, median

    def get_student_report(self, email):
        """Generates a report for a single student.""" #
        student = self.find_student(email)
        if not student:
            return "Student not found."
        
        course = self.find_course(student.course_id)
        course_name = course.course_name if course else "Unknown Course"
        
        report = f"\n--- Student Grade Report ---\n"
        report += f"Name: {student.first_name} {student.last_name}\n"
        report += f"Email: {student.email}\n"
        report += f"Course: {course_name} ({student.course_id})\n"
        report += f"Grade: {student.grade}\n"
        report += f"Marks: {student.marks}\n"
        report += "-----------------------------"
        return report

    def get_course_report(selfself, course_id):
        """Generates a report for all students in a course.""" 
        course = selfself.find_course(course_id)
        if not course:
            return "Course not found."
            
        students_in_course = [s for s in selfself.students if s.course_id == course_id]
        
        report = f"\n--- Course Grade Report: {course.course_name} ({course_id}) ---\n"
        if not students_in_course:
            report += "No students enrolled in this course."
            return report
            
        for s in students_in_course:
            report += f"  - {s.last_name}, {s.first_name} ({s.email}): {s.marks} ({s.grade})\n"
        
        stats = selfself.get_course_statistics(course_id)
        report += "--------------------------------------\n"
        if stats[0] is not None:
            report += f"Statistics: Average={stats[0]:.2f}, Median={stats[1]}\n"
        else:
            report += "Statistics: No data available.\n"
        return report

    def get_professor_report(self, prof_email):
        """Generates a report for a professor and their courses.""" #
        prof = self.find_professor(prof_email)
        if not prof:
            return "Professor not found."
            
        report = f"\n--- Professor Report ---\n"
        report += f"Name: {prof.name}\n"
        report += f"Email: {prof.email}\n"
        report += f"Rank: {prof.rank}\n"
        
        course = self.find_course(prof.course_id)
        if course:
            report += f"\nAssigned Course:\n"
            report += f"  ID: {course.course_id}\n"
            report += f"  Name: {course.course_name}\n"
            report += f"  Description: {course.description}\n"
            report += f"\n{self.get_course_report(course.course_id)}"
        else:
            report += f"No assigned course found (ID: {prof.course_id})."
        
        return report


# 5. MAIN APPLICATION (Menu-driven)

def get_input(prompt, required=True):
    """Helper to get non-empty input."""
    while True:
        val = input(f"{prompt}: ").strip()
        if not val and required:
            print("Input cannot be empty.")
        else:
            return val

def get_int_input(prompt, required=True):
    """Helper to get integer input."""
    while True:
        val = get_input(prompt, required)
        if not val and not required:
            return None
        try:
            if val:
                return int(val)
            return None
        except ValueError:
            print("Invalid input. Please enter a number.")

def student_menu(app):
    """Menu for a logged-in student."""
    print(f"\nWelcome, {app.current_user.user_id} (Student)")
    print(app.get_student_report(app.current_user.user_id))

def professor_menu(app):
    """Menu for a logged-in professor (admin)."""
    prof = app.find_professor(app.current_user.user_id)
    name = prof.name if prof else app.current_user.user_id
    
    print(f"\nWelcome, {name} (Professor)")
    
    while True:
        print("\n--- Professor Menu ---")
        print("1. Manage Students")
        print("2. Manage Courses")
        print("3. Manage Professors")
        print("4. View Reports")
        print("5. View My Course Statistics")
        print("0. Logout")
        choice = get_input("Select an option")

        if choice == '1':
            manage_students(app)
        elif choice == '2':
            manage_courses(app)
        elif choice == '3':
            manage_professors(app)
        elif choice == '4':
            view_reports(app)
        elif choice == '5':
            if prof:
                avg, med = app.get_course_statistics(prof.course_id)
                print(f"\n--- Statistics for {prof.course_id} ---")
                if avg is not None:
                    print(f"Average Score: {avg:.2f}")
                    print(f"Median Score:  {med}")
                else:
                    print("No student data for this course.")
            else:
                print("You are not registered as a professor with an assigned course.")
        elif choice == '0':
            app.logout()
            print("Logged out successfully.")
            break
        else:
            print("Invalid option.")

def manage_students(app):
    """Sub-menu for student management."""
    while True:
        print("\n--- Manage Students ---")
        print("1. Add Student")
        print("2. Modify Student")
        print("3. Delete Student")
        print("4. Search Student")
        print("5. Sort Students (by Name)")
        print("6. Sort Students (by Marks)")
        print("0. Back to Main Menu")
        choice = get_input("Select an option")
        
        if choice == '1':
            print("Enter new student details:")
            email = get_input("Email")
            fname = get_input("First Name")
            lname = get_input("Last Name")
            cid = get_input("Course ID")
            grade = get_input("Grade (e.g., A)")
            marks = get_int_input("Marks (e.g., 95)")
            if app.add_student(email, fname, lname, cid, grade, marks):
                print("Student added successfully.")
            else:
                print("Failed to add student (see error above).")

        elif choice == '2':
            email = get_input("Enter student email to modify")
            if not app.find_student(email):
                print("Student not found.")
                continue
            print("Enter new details (leave blank to keep current):")
            fname = get_input("First Name", required=False)
            lname = get_input("Last Name", required=False)
            cid = get_input("Course ID", required=False)
            grade = get_input("Grade", required=False)
            marks = get_int_input("Marks", required=False)
            if app.modify_student(email, fname, lname, cid, grade, marks):
                print("Student modified successfully.")
            else:
                print("Failed to modify student.")

        elif choice == '3':
            email = get_input("Enter student email to delete")
            if app.delete_student(email):
                print("Student deleted successfully.")
            else:
                print("Student not found.")

        elif choice == '4':
            email = get_input("Enter student email to search")
            student = app.search_student(email)
            if student:
                print(app.get_student_report(email))
            else:
                print("Student not found.")
        
        elif choice == '5': # Sort by Name
            sorted_list = app.sort_students(by='name')
            print("\n--- Students Sorted by Name ---")
            for s in sorted_list:
                print(f"{s.last_name}, {s.first_name} ({s.email})")
        
        elif choice == '6': # Sort by Marks
            sorted_list = app.sort_students(by='marks', descending=True)
            print("\n--- Students Sorted by Marks (High to Low) ---")
            for s in sorted_list:
                print(f"{s.marks} - {s.last_name}, {s.first_name}")

        elif choice == '0':
            break

def manage_courses(app):
    """Sub-menu for course management."""
    while True:
        print("\n--- Manage Courses ---")
        print("1. Add Course")
        print("2. Modify Course")
        print("3. Delete Course")
        print("4. List All Courses")
        print("0. Back to Main Menu")
        choice = get_input("Select an option")

        if choice == '1':
            cid = get_input("Course ID")
            cname = get_input("Course Name")
            desc = get_input("Description")
            if app.add_course(cid, cname, desc):
                print("Course added successfully.")
            else:
                print("Failed to add course.")
        
        elif choice == '2':
            cid = get_input("Enter Course ID to modify")
            if not app.find_course(cid):
                print("Course not found.")
                continue
            cname = get_input("New Course Name", required=False)
            desc = get_input("New Description", required=False)
            if app.modify_course(cid, cname, desc):
                print("Course modified.")
            else:
                print("Failed to modify.")

        elif choice == '3':
            cid = get_input("Enter Course ID to delete")
            if app.delete_course(cid):
                print("Course deleted.")
            else:
                print("Course not found.")
        
        elif choice == '4':
            print("\n--- All Courses ---")
            if not app.courses:
                print("No courses found.")
            for c in app.courses:
                print(f"[{c.course_id}] {c.course_name}: {c.description}")

        elif choice == '0':
            break

def manage_professors(app):
    """Sub-menu for professor management."""
    while True:
        print("\n--- Manage Professors ---")
        print("1. Add Professor")
        print("2. Modify Professor")
        print("3. Delete Professor")
        print("4. List All Professors")
        print("0. Back to Main Menu")
        choice = get_input("Select an option")
        
        if choice == '1':
            print("Enter new professor details:")
            email = get_input("Email")
            name = get_input("Name")
            rank = get_input("Rank")
            cid = get_input("Course ID")
            if app.add_professor(email, name, rank, cid):
                print("Professor added successfully.")
            else:
                print("Failed to add professor.")
                
        elif choice == '2':
            email = get_input("Enter professor email to modify")
            if not app.find_professor(email):
                print("Professor not found.")
                continue
            print("Enter new details (leave blank to keep current):")
            name = get_input("Name", required=False)
            rank = get_input("Rank", required=False)
            cid = get_input("Course ID", required=False)
            if app.modify_professor(email, name, rank, cid):
                print("Professor modified successfully.")
            else:
                print("Failed to modify professor.")

        elif choice == '3':
            email = get_input("Enter professor email to delete")
            if app.delete_professor(email):
                print("Professor deleted successfully.")
            else:
                print("Professor not found.")

        elif choice == '4':
            print("\n--- All Professors ---")
            if not app.professors:
                print("No professors found.")
            for p in app.professors:
                print(f"[{p.email}] {p.name}, {p.rank} (Course: {p.course_id})")
        
        elif choice == '0':
            break


def view_reports(app):
    """Sub-menu for viewing all reports."""
    print("\n--- View Reports ---")
    print("1. Student Report")
    print("2. Course Report")
    print("3. Professor Report")
    print("0. Back")
    choice = get_input("Select an option")
    
    if choice == '1':
        email = get_input("Enter student email")
        print(app.get_student_report(email))
    elif choice == '2':
        cid = get_input("Enter Course ID")
        print(app.get_course_report(cid))
    elif choice == '3':
        email = get_input("Enter professor email")
        print(app.get_professor_report(email))
    elif choice == '0':
        return

def main_app():
    """Main application loop."""
    app = CheckMyGradeApp()
    
    while True:
        print("\n==== Welcome to CheckMyGrade App ====")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = get_input("Select an option")

        if choice == '1':
            # Login
            email = get_input("Email")
            password = get_input("Password") 
            if app.login(email, password):
                print("Login successful!")
                if app.current_user.role == 'student':
                    student_menu(app)
                    app.logout() # Auto-logout after student views grades
                elif app.current_user.role == 'professor':
                    professor_menu(app)
                else:
                    print("Unknown role. Logging out.")
                    app.logout()
            else:
                print("Invalid email or password.")
        
        elif choice == '2':
            # Register
            print("--- New User Registration ---")
            email = get_input("Email")
            password = get_input("Password")
            role = get_input("Role (student/professor)").lower()
            if role not in ['student', 'professor']:
                print("Invalid role. Must be 'student' or 'professor'.")
                continue
            
            success, message = app.register_user(email, password, role)
            print(message)
            
            # Auto-register professor in their table
            if success and role == 'professor':
                name = get_input("Full Name")
                rank = get_input("Rank (e.g., Senior Professor)")
                cid = get_input("Course ID")
                if not app.add_professor(email, name, rank, cid):
                     print(f"Failed to add professor details.")
            elif success and role == 'student':
                # Student records must be added by a professor
                print("Student user created. Grade data must be added by a professor.")

        elif choice == '3':
            print("Thank you for using CheckMyGrade.")
            break
        
        else:
            print("Invalid choice. Please try again.")


# 6. UNIT TESTS

# Test Configuration
TEST_STUDENT_FILE = 'test_students.csv'
TEST_COURSE_FILE = 'test_course.csv'
TEST_PROF_FILE = 'test_professors.csv'
TEST_LOGIN_FILE = 'test_login.csv'

# Store original filenames
ORIG_FILES = {
    'STUDENT_FILE': STUDENT_FILE,
    'COURSE_FILE': COURSE_FILE,
    'PROF_FILE': PROF_FILE,
    'LOGIN_FILE': LOGIN_FILE,
}

def mock_data_manager_files():
    """Point global file-path variables to test files."""
    global STUDENT_FILE, COURSE_FILE, PROF_FILE, LOGIN_FILE
    STUDENT_FILE = TEST_STUDENT_FILE
    COURSE_FILE = TEST_COURSE_FILE
    PROF_FILE = TEST_PROF_FILE
    LOGIN_FILE = TEST_LOGIN_FILE

def restore_data_manager_files():
    """Restore original filenames."""
    global STUDENT_FILE, COURSE_FILE, PROF_FILE, LOGIN_FILE
    STUDENT_FILE = ORIG_FILES['STUDENT_FILE']
    COURSE_FILE = ORIG_FILES['COURSE_FILE']
    PROF_FILE = ORIG_FILES['PROF_FILE']
    LOGIN_FILE = ORIG_FILES['LOGIN_FILE']

def cleanup_test_files():
    """Delete test CSV files."""
    for f in [TEST_STUDENT_FILE, TEST_COURSE_FILE, TEST_PROF_FILE, TEST_LOGIN_FILE]:
        if os.path.exists(f):
            os.remove(f)

class TestCheckMyGradeApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Mock filenames once for all tests."""
        mock_data_manager_files()

    @classmethod
    def tearDownClass(cls):
        """Restore filenames and clean up files after all tests."""
        restore_data_manager_files()
        cleanup_test_files()

    def setUp(self):
        """
        Run before each test. 
        Cleans files and creates a fresh app instance.
        """
        cleanup_test_files() # Ensure a clean state
        self.app = CheckMyGradeApp() # This will create new empty files
        
        # Pre-populate with one course for testing
        self.app.add_course("DATA200", "Applied Data Intelligence", "Test Course")

    def tearDown(self):
        """Run after each test."""
        pass 

    def test_01_student_add_delete_modify(self):
        """Testing of student records addition/deletion and modification.""" #
        # Add
        result = self.app.add_student("sneha@sjsu.edu", "Sneha", "Tumkur Narendra", "DATA200", "A", 96)
        self.assertTrue(result)
        self.assertEqual(len(self.app.students), 1)
        self.assertEqual(self.app.students[0].first_name, "Sneha")

        # Modify
        result = self.app.modify_student("sneha@sjsu.edu", "Sneha", "", "DATA200", "", 98)
        self.assertTrue(result)
        self.assertEqual(len(self.app.students), 1)
        self.assertEqual(self.app.students[0].first_name, "Sneha")
        self.assertEqual(self.app.students[0].marks, 98)

        # Delete
        result = self.app.delete_student("sneha@sjsu.edu")
        self.assertTrue(result)
        self.assertEqual(len(self.app.students), 0)

    def test_02_course_add_delete_modify(self):
        """Unit test to add/delete/modify the course.""" 
        # We added one course in setUp, so count is 1
        self.assertEqual(len(self.app.courses), 1)
        
        # Add
        result = self.app.add_course("DATA220", "ML", "Test ML")
        self.assertTrue(result)
        self.assertEqual(len(self.app.courses), 2)

        # Modify
        result = self.app.modify_course("DATA220", "Machine Learning", "Updated Desc")
        self.assertTrue(result)
        self.assertEqual(self.app.courses[1].course_name, "Machine Learning")

        # Delete
        result = self.app.delete_course("DATA220")
        self.assertTrue(result)
        self.assertEqual(len(self.app.courses), 1)

    def test_03_professor_add_delete_modify(self):
        """Unit test to add/delete/modify professors.""" #
        # Add
        result = self.app.add_professor("sam@sjsu.edu", "Sam C", "Professor", "DATA200")
        self.assertTrue(result)
        self.assertEqual(len(self.app.professors), 1)

        # Modify
        result = self.app.modify_professor("sam@sjsu.edu", "Sam Carpenter", "Senior Professor", "")
        self.assertTrue(result)
        self.assertEqual(self.app.professors[0].name, "Sam Carpenter")
        self.assertEqual(self.app.professors[0].rank, "Senior Professor")
        
        # Delete
        result = self.app.delete_professor("sam@sjsu.edu")
        self.assertTrue(result)
        self.assertEqual(len(self.app.professors), 0)

    def test_04_load_and_search(self):
        """Test loading data and searching records with timing.""" 
        self.app.add_student("sneha@sjsu.edu", "Sneha", "Tumkur Narendra", "DATA200", "A", 98)
        
        # Simulate app restart by creating new instance
        app_new = CheckMyGradeApp()
        self.assertEqual(len(app_new.students), 1)
        
        print("\n--- Testing Search (test_04_load_and_search) ---")
        student = app_new.search_student("sneha@sjsu.edu")
        self.assertIsNotNone(student)
        self.assertEqual(student.first_name, "Sneha")

    def test_05_sort(self):
        """Test sorting students by marks and name, with timing.""" #
        self.app.add_student("charlie@sjsu.edu", "Charlie", "Brown", "DATA200", "C", 75)
        self.app.add_student("alice@sjsu.edu", "Alice", "Smith", "DATA200", "A", 95)
        self.app.add_student("bob@sjsu.edu", "Bob", "Johnson", "DATA200", "B", 85)
        
        print("\n--- Testing Sort by Name (test_05_sort) ---")
        sorted_by_name = self.app.sort_students(by='name')
        self.assertEqual(sorted_by_name[0].first_name, "Charlie")
        self.assertEqual(sorted_by_name[1].first_name, "Bob")
        self.assertEqual(sorted_by_name[2].first_name, "Alice")
        
        print("\n--- Testing Sort by Marks (test_05_sort) ---")
        sorted_by_marks = self.app.sort_students(by='marks', descending=True)
        self.assertEqual(sorted_by_marks[0].marks, 95)
        self.assertEqual(sorted_by_marks[1].marks, 85)
        self.assertEqual(sorted_by_marks[2].marks, 75)

    def test_06_1000_records_performance(self):
        """Test with 1000 student records for search and sort timing.""" #
        print("\n--- Populating 1000 records... ---")
        students_to_add = []
        for i in range(1000):
            students_to_add.append(Student(
                email=f"student{i}@stest.edu",
                first_name="First",
                last_name=f"Last{999-i}", # Sort reverse of email
                course_id="DATA200",
                grade="B",
                marks=80
            ))
        
        # Add a specific target student
        students_to_add[500] = Student("target@test.edu", "Target", "Student", "DATA200", "A", 100)
        self.app.students = students_to_add
        save_students(self.app.students)
        
        # Load the 1000 records
        app_1000 = CheckMyGradeApp()
        self.assertEqual(len(app_1000.students), 1000)
        print("--- 1000 records loaded. ---")

        # Test Search Time
        print("\n--- Testing Search (1000 records) ---")
        student = app_1000.search_student("target@test.edu")
        self.assertIsNotNone(student)
        self.assertEqual(student.first_name, "Target")

        # Test Sort Time (by name)
        print("\n--- Testing Sort by Name (1000 records) ---")
        sorted_list = app_1000.sort_students(by='name')
        self.assertEqual(sorted_list[0].last_name, "Last0") # 'Last{999-i}'
        self.assertEqual(sorted_list[999].last_name, "Student")

    def test_07_encryption(self):
        """Test password encryption and decryption.""" 
        self.app.register_user("encrypt@test.edu", "Welcome12#_", "student")
        
        # Manually load users to check file content
        users = load_users()
        found = False
        for u in users:
            if u.user_id == "encrypt@test.edu":
                found = True
                # Password in file must not be "Welcome12#_"
                self.assertNotEqual(u.password, "Welcome12#_")
                # It should be the encrypted version
                self.assertEqual(u.password, encrypt_password("Welcome12#_"))
                # It should decrypt correctly
                self.assertEqual(decrypt_password(u.password), "Welcome12#_")
        
        self.assertTrue(found, "User was not saved to file")


# MAIN EXECUTION

if __name__ == "__main__":
    main_app()
