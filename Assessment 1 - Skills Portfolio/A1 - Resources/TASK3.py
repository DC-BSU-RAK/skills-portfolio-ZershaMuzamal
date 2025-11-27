"""
Assessment 2 - Student Management System
-------------------------------------------------------------------------
📚 REFERENCES & LEARNING RESOURCES USED
-------------------------------------------------------------------------
1. Python Object Oriented Programming (Classes):
   - Source: W3Schools
   - Link: https://www.w3schools.com/python/python_classes.asp
   - Concept: Creating the 'Student' class to hold data and calculate grades.

2. Tkinter Treeview (The Table):
   - Source: GeeksForGeeks
   - Link: https://www.geeksforgeeks.org/tkinter-treeview-widget/
   - Concept: Displaying data in columns and rows.

3. Reading and Writing Files:
   - Source: W3Schools
   - Link: https://www.w3schools.com/python/python_file_write.asp
   - Concept: Saving student data to 'studentMarks.txt' so it isn't lost.

4. Python Lambda Functions (Sorting):
   - Source: YouTube / RealPython
   - Concept: Using 'key=lambda s: s.name' to sort the list of objects.
-------------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys

# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================
# I added the emoji here so it appears on the top bar of the main window
WINDOW_TITLE = "🎓 Student Manager Professional"
WINDOW_SIZE = "1100x700"

# Color Palette (Modern Dark/Blue Theme)
# I chose these colors to look like a modern dashboard (Facebook/Twitter style colors)
COLOR_BG_MAIN = "#f0f2f5"
COLOR_SIDEBAR = "#2c3e50"
COLOR_SIDEBAR_HOVER = "#34495e"
COLOR_TEXT_WHITE = "#ecf0f1"
COLOR_ACCENT = "#3498db"
COLOR_SUCCESS = "#2ecc71"
COLOR_WARNING = "#e67e22"
COLOR_DANGER = "#e74c3c"

# Setting up fonts in one place so I don't have to change them everywhere later
FONT_HEADER = ("Segoe UI", 20, "bold")
FONT_SUBHEADER = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")

# =============================================================================
# DATA MODEL CLASS
# =============================================================================
class Student:
    """
    I created this class to represent a single student.
    It holds their info and does the maths for their grades.
    """
    def __init__(self, code, name, cw1, cw2, cw3, exam):
        # Cleaning up the input (removing spaces) just in case
        self.code = str(code).strip()
        self.name = str(name).strip()
        # Storing coursework in a list makes it easier to sum up later
        self.coursework = [int(cw1), int(cw2), int(cw3)]
        self.exam = int(exam)

    # I used @property decorators here so I can access .total_overall like a variable
    # instead of calling a function .total_overall() every time.
    @property
    def total_coursework(self):
        return sum(self.coursework)

    @property
    def total_overall(self):
        return self.total_coursework + self.exam

    @property
    def percentage(self):
        # The total marks possible are 20+20+20 (Coursework) + 100 (Exam) = 160
        return (self.total_overall / 160) * 100

    @property
    def grade(self):
        # This logic converts the percentage into a letter grade
        p = self.percentage
        if p >= 70: return 'A'
        elif p >= 60: return 'B'
        elif p >= 50: return 'C'
        elif p >= 40: return 'D'
        else: return 'F'

    def to_csv_string(self):
        # This formats the student data into a comma-separated string for the text file
        return f"{self.code},{self.name},{self.coursework[0]},{self.coursework[1]},{self.coursework[2]},{self.exam}\n"

    def __str__(self):
        return f"{self.name} ({self.code})"

# =============================================================================
# CONTROLLER CLASS (LOGIC HANDLER)
# =============================================================================
class StudentController:
    """
    This class handles the 'backend' logic: saving files, loading files, and sorting.
    I separated this from the GUI code to keep things organized (MVC pattern).
    """
    def __init__(self):
        # I found this code online to make sure the text file is always found
        # regardless of where I run the script from.
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        self.filepath = os.path.join(application_path, "studentMarks.txt")
        self.students = [] # This list will hold all my Student objects
        self.load_data()

    def load_data(self):
        """Loads students from the text file."""
        self.students = []
        
        # Validation: Checking if the file actually exists before trying to read it
        if not os.path.exists(self.filepath):
            # If not, I create a dummy file so the app doesn't crash next time
            try:
                with open(self.filepath, "w") as f:
                    f.write("0\n")
                messagebox.showwarning("File Missing", 
                    f"Could not find 'studentMarks.txt'.\n\nI have created a new empty file for you.")
            except IOError:
                messagebox.showerror("IO Error", "Could not create data file.")
            return

        try:
            # Using 'with open' is safer because it automatically closes the file
            with open(self.filepath, "r") as file:
                lines = file.readlines()
                
                # Check if file is empty
                if len(lines) < 2 and lines[0].strip() == "0":
                    return 

                # I start from index 1 (lines[1:]) because line 0 is just the count
                for line in lines[1:]:
                    parts = line.strip().split(",")
                    if len(parts) == 6:
                        # Creating a new Student object for each line in the file
                        s = Student(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])
                        self.students.append(s)
                        
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load data: {e}")

    def save_data(self):
        """Saves current student list back to the text file."""
        try:
            with open(self.filepath, "w") as file:
                # First line is the total number of students
                file.write(f"{len(self.students)}\n")
                # Then I loop through every student and write their CSV string
                for s in self.students:
                    file.write(s.to_csv_string())
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data: {e}")

    def add_student(self, student_obj):
        # Validation: Check if the ID already exists
        for s in self.students:
            if s.code == student_obj.code:
                return False, "Student Code already exists."
        
        self.students.append(student_obj)
        self.save_data() # Auto-save after adding
        return True, "Student added successfully."

    def delete_student(self, code):
        # I use enumerate so I can delete by index
        for i, s in enumerate(self.students):
            if s.code == code:
                del self.students[i]
                self.save_data()
                return True
        return False

    def update_student(self, original_code, new_student_obj):
        # If the code changed, make sure the NEW code isn't taken by someone else
        if original_code != new_student_obj.code:
            for s in self.students:
                if s.code == new_student_obj.code:
                    return False, "New Student Code is already taken."

        for i, s in enumerate(self.students):
            if s.code == original_code:
                self.students[i] = new_student_obj
                self.save_data()
                return True, "Student updated successfully."
        
        return False, "Original record not found."

    def get_student_by_code(self, code):
        for s in self.students:
            if s.code == str(code):
                return s
        return None

    def get_highest_scorer(self):
        if not self.students: return None
        # Using the max() function with a key is much faster than writing a loop myself
        return max(self.students, key=lambda s: s.total_overall)

    def get_lowest_scorer(self):
        if not self.students: return None
        return min(self.students, key=lambda s: s.total_overall)

    def sort_students(self, key, reverse=False):
        # Sorting logic based on what the user selected in the dropdown
        if key == 'code':
            self.students.sort(key=lambda s: s.code, reverse=reverse)
        elif key == 'name':
            self.students.sort(key=lambda s: s.name.lower(), reverse=reverse)
        elif key == 'percentage':
            self.students.sort(key=lambda s: s.percentage, reverse=reverse)

    def get_average_percentage(self):
        if not self.students: return 0.0
        total = sum(s.percentage for s in self.students)
        return total / len(self.students)

# =============================================================================
# GUI CLASSES
# =============================================================================

class StudentForm(tk.Toplevel):
    """
    This is the pop-up window for Adding/Updating students.
    I made it a Toplevel so it sits on top of the main window.
    """
    def __init__(self, parent, title, current_student=None):
        super().__init__(parent)
        # Adding the emoji to the pop-up title as requested
        self.title("🎓 " + title) 
        self.geometry("400x500")
        self.resizable(False, False)
        self.result = None 
        self.configure(bg=COLOR_BG_MAIN)
        self.create_widgets(current_student)
        
        # Making the window modal (user must finish here before clicking main window)
        self.transient(parent)
        self.grab_set()
        self.parent = parent

    def create_widgets(self, student):
        pad_x = 20
        lbl_head = tk.Label(self, text="Student Details", font=FONT_SUBHEADER, bg=COLOR_BG_MAIN)
        lbl_head.pack(pady=20)

        form_frame = tk.Frame(self, bg=COLOR_BG_MAIN)
        form_frame.pack(fill="both", expand=True, padx=pad_x)

        # Creating entries for all the marks
        self.entry_code = self.create_input(form_frame, "Student Code (1000-9999):", 0)
        self.entry_name = self.create_input(form_frame, "Full Name:", 1)
        self.entry_cw1 = self.create_input(form_frame, "Coursework 1 (0-20):", 2)
        self.entry_cw2 = self.create_input(form_frame, "Coursework 2 (0-20):", 3)
        self.entry_cw3 = self.create_input(form_frame, "Coursework 3 (0-20):", 4)
        self.entry_exam = self.create_input(form_frame, "Exam Mark (0-100):", 5)

        # If we are Updating, pre-fill the boxes with existing data
        if student:
            self.entry_code.insert(0, student.code)
            self.entry_name.insert(0, student.name)
            self.entry_cw1.insert(0, str(student.coursework[0]))
            self.entry_cw2.insert(0, str(student.coursework[1]))
            self.entry_cw3.insert(0, str(student.coursework[2]))
            self.entry_exam.insert(0, str(student.exam))

        btn_frame = tk.Frame(self, bg=COLOR_BG_MAIN)
        btn_frame.pack(pady=20)

        btn_save = tk.Button(btn_frame, text="Save", bg=COLOR_ACCENT, fg="white", 
                             font=FONT_BOLD, width=12, command=self.on_save)
        btn_save.pack(side="left", padx=10)

        btn_cancel = tk.Button(btn_frame, text="Cancel", bg=COLOR_DANGER, fg="white", 
                               font=FONT_BOLD, width=12, command=self.destroy)
        btn_cancel.pack(side="right", padx=10)

    def create_input(self, parent, label_text, row):
        # Helper function to make creating labels and entries faster
        lbl = tk.Label(parent, text=label_text, bg=COLOR_BG_MAIN, font=FONT_BODY)
        lbl.grid(row=row, column=0, sticky="w", pady=5)
        entry = tk.Entry(parent, font=FONT_BODY, width=25)
        entry.grid(row=row, column=1, sticky="e", pady=5)
        return entry

    def on_save(self):
        # Getting all the text from the inputs
        code = self.entry_code.get().strip()
        name = self.entry_name.get().strip()
        cw1 = self.entry_cw1.get().strip()
        cw2 = self.entry_cw2.get().strip()
        cw3 = self.entry_cw3.get().strip()
        exam = self.entry_exam.get().strip()

        # Validation 1: Required fields
        if not code or not name:
            messagebox.showwarning("Validation", "Code and Name are required.")
            return

        # Validation 2: Code format
        if not (code.isdigit() and 1000 <= int(code) <= 9999):
            messagebox.showwarning("Validation", "Code must be a number between 1000 and 9999.")
            return
        
        try:
            c1 = int(cw1)
            c2 = int(cw2)
            c3 = int(cw3)
            ex = int(exam)

            # Validation 3: Mark ranges
            if not (0 <= c1 <= 20 and 0 <= c2 <= 20 and 0 <= c3 <= 20):
                messagebox.showwarning("Validation", "Coursework marks must be between 0 and 20.")
                return
            if not (0 <= ex <= 100):
                messagebox.showwarning("Validation", "Exam mark must be between 0 and 100.")
                return
            
            # If everything is good, create the object and close window
            self.result = Student(code, name, c1, c2, c3, ex)
            self.destroy()

        except ValueError:
            messagebox.showwarning("Validation", "Marks must be numeric integers.")


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.controller = StudentController()
        
        # Removing the default feather icon by generating a transparent/colored block
        # This makes the app look more custom and less like a default Tk script.
        try:
            # Creating a 1x1 pixel image to use as a blank icon
            blank_icon = tk.PhotoImage(width=1, height=1)
            self.iconphoto(True, blank_icon)
        except Exception:
            pass

        self.title(WINDOW_TITLE) # Title includes the emoji
        self.geometry(WINDOW_SIZE)
        self.configure(bg=COLOR_BG_MAIN)
        self.setup_styles()

        # Layout: Sidebar on the Left, Main Content on the Right
        self.container_sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=250)
        self.container_sidebar.pack(side="left", fill="y")
        self.container_sidebar.pack_propagate(False) # Stops sidebar from shrinking

        self.container_main = tk.Frame(self, bg=COLOR_BG_MAIN)
        self.container_main.pack(side="right", fill="both", expand=True)

        self.build_sidebar()
        self.build_pages()
        
        # Start by showing the table view
        self.show_page("view_all")

    def setup_styles(self):
        # Configuring the Treeview (Table) to look modern
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview.Heading", font=FONT_BOLD, background=COLOR_SIDEBAR, 
                        foreground="white", padding=10)
        style.configure("Treeview", font=FONT_BODY, rowheight=30, 
                        background="white", fieldbackground="white")
        style.map("Treeview", background=[("selected", COLOR_ACCENT)])

    def build_sidebar(self):
        # Adding the Emoji Logo here in the sidebar title too
        lbl_title = tk.Label(self.container_sidebar, text="🎓 Student\nManager", 
                             font=("Segoe UI", 24, "bold"), 
                             bg=COLOR_SIDEBAR, fg="white", pady=30)
        lbl_title.pack()

        # Adding navigation buttons
        self.create_nav_button("View All Records", lambda: self.show_page("view_all"))
        self.create_nav_button("Find Student", lambda: self.show_page("individual"))
        self.create_nav_button("Class Statistics", lambda: self.show_page("stats"))
        self.create_nav_button("Highest Scorer", lambda: self.show_page("highest"))
        self.create_nav_button("Lowest Scorer", lambda: self.show_page("lowest"))
        
        # Separator line
        tk.Frame(self.container_sidebar, height=2, bg=COLOR_SIDEBAR_HOVER).pack(fill="x", pady=20)
        
        # Action buttons with different colors
        self.create_nav_button("Add New Student", self.action_add_student, bg_color=COLOR_SUCCESS)
        self.create_nav_button("Update Record", self.action_update_student, bg_color=COLOR_ACCENT)
        self.create_nav_button("Delete Record", self.action_delete_student, bg_color=COLOR_DANGER)
        
        lbl_ver = tk.Label(self.container_sidebar, text="v2.0 Pro", 
                           bg=COLOR_SIDEBAR, fg="#7f8c8d", font=("Segoe UI", 8))
        lbl_ver.pack(side="bottom", pady=10)

    def create_nav_button(self, text, command, bg_color=COLOR_SIDEBAR):
        # Helper to make sidebar buttons
        btn = tk.Button(self.container_sidebar, text=text, font=FONT_BODY,
                        bg=bg_color, fg="white", activebackground=COLOR_SIDEBAR_HOVER,
                        activeforeground="white", bd=0, padx=20, pady=12,
                        anchor="w", command=command, cursor="hand2")
        btn.pack(fill="x", pady=2)

    def build_pages(self):
        # I store all frames in a dictionary so I can easily switch between them
        self.frames = {}
        self.frames["view_all"] = self.create_view_all_frame()
        self.frames["individual"] = self.create_individual_frame()
        self.frames["stats"] = self.create_stats_frame()

    def create_view_all_frame(self):
        frame = tk.Frame(self.container_main, bg=COLOR_BG_MAIN)
        self.add_header(frame, "All Student Records")

        # Sorting controls
        sort_frame = tk.Frame(frame, bg=COLOR_BG_MAIN)
        sort_frame.pack(fill="x", padx=40, pady=10)
        tk.Label(sort_frame, text="Sort By:", bg=COLOR_BG_MAIN, font=FONT_BOLD).pack(side="left")
        
        sort_opts = ["Student Code", "Name", "Percentage (High-Low)", "Percentage (Low-High)"]
        self.combo_sort = ttk.Combobox(sort_frame, values=sort_opts, state="readonly", width=25)
        self.combo_sort.current(0)
        self.combo_sort.pack(side="left", padx=10)
        
        btn_sort = tk.Button(sort_frame, text="Apply Sort", bg=COLOR_SIDEBAR, fg="white",
                             command=self.refresh_table_sorted)
        btn_sort.pack(side="left")

        # Defining columns for the Treeview
        cols = ("Code", "Name", "CW1", "CW2", "CW3", "Exam", "Total", "%", "Grade")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")
        
        col_widths = [80, 200, 60, 60, 60, 60, 80, 80, 60]
        for col, width in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        
        # Adding a scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y", pady=(0, 40), padx=(0, 40))
        self.tree.pack(fill="both", expand=True, padx=(40, 0), pady=(0, 40))
        
        return frame

    def create_individual_frame(self):
        frame = tk.Frame(self.container_main, bg=COLOR_BG_MAIN)
        self.add_header(frame, "Individual Student Search")

        search_frame = tk.Frame(frame, bg="white", padx=20, pady=20, relief="raised")
        search_frame.pack(pady=20)
        
        tk.Label(search_frame, text="Enter Student Code:", font=FONT_BODY, bg="white").pack(side="left", padx=10)
        self.entry_search = tk.Entry(search_frame, font=FONT_BODY, width=20)
        self.entry_search.pack(side="left", padx=10)
        
        btn_find = tk.Button(search_frame, text="Search", bg=COLOR_ACCENT, fg="white",
                             command=self.action_find_student)
        btn_find.pack(side="left", padx=10)

        # Label to show results
        self.lbl_result_details = tk.Label(frame, text="", font=("Courier New", 12), 
                                           bg="#fffbe6", justify="left", relief="solid", bd=1, padx=20, pady=20)
        self.lbl_result_details.pack(pady=30, padx=50, fill="x")

        return frame

    def create_stats_frame(self):
        frame = tk.Frame(self.container_main, bg=COLOR_BG_MAIN)
        self.add_header(frame, "Class Statistics")
        self.stats_container = tk.Frame(frame, bg=COLOR_BG_MAIN)
        self.stats_container.pack(fill="both", expand=True, padx=40, pady=20)
        return frame

    def add_header(self, parent, text):
        # Adding the Emoji to page headers too for consistency
        lbl = tk.Label(parent, text="🎓 " + text, font=FONT_HEADER, 
                       bg=COLOR_BG_MAIN, fg=COLOR_SIDEBAR)
        lbl.pack(anchor="w", padx=40, pady=(40, 20))
        tk.Frame(parent, height=4, bg=COLOR_ACCENT, width=100).pack(anchor="w", padx=40)

    def show_page(self, page_name):
        # Hides all pages then shows the one requested
        for f in self.frames.values():
            f.pack_forget()
        
        if page_name == "view_all":
            self.refresh_table()
        elif page_name == "stats":
            self.update_stats_display()
        elif page_name == "highest":
            self.show_extreme_student("high")
            return 
        elif page_name == "lowest":
            self.show_extreme_student("low")
            return 

        self.frames[page_name].pack(fill="both", expand=True)

    def refresh_table(self, students_list=None):
        # If no list provided, get all from controller
        if students_list is None:
            students_list = self.controller.students
        
        # Clear current table items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Re-populate table
        for s in students_list:
            self.tree.insert("", "end", values=(
                s.code, s.name, 
                s.coursework[0], s.coursework[1], s.coursework[2], 
                s.exam, s.total_overall, 
                f"{s.percentage:.2f}%", s.grade
            ))

    def refresh_table_sorted(self):
        choice = self.combo_sort.get()
        # Sort based on dropdown selection
        if "Code" in choice:
            self.controller.sort_students('code')
        elif "Name" in choice:
            self.controller.sort_students('name')
        elif "Percentage (High-Low)" in choice:
            self.controller.sort_students('percentage', reverse=True)
        elif "Percentage (Low-High)" in choice:
            self.controller.sort_students('percentage', reverse=False)
        self.refresh_table()

    def action_find_student(self):
        code = self.entry_search.get().strip()
        student = self.controller.get_student_by_code(code)
        
        if student:
            # Creating a formatted string to display results nicely
            text = (
                f"Student Found:\n\n"
                f"Name:          {student.name}\n"
                f"Student Code:  {student.code}\n"
                f"----------------------------\n"
                f"Coursework 1:  {student.coursework[0]}\n"
                f"Coursework 2:  {student.coursework[1]}\n"
                f"Coursework 3:  {student.coursework[2]}\n"
                f"Coursework Tot:{student.total_coursework}\n"
                f"Exam Mark:     {student.exam}\n"
                f"----------------------------\n"
                f"Overall Total: {student.total_overall}/160\n"
                f"Percentage:    {student.percentage:.2f}%\n"
                f"Final Grade:   {student.grade}"
            )
            self.lbl_result_details.config(text=text, fg="black")
        else:
            self.lbl_result_details.config(text="Student not found.", fg="red")

    def show_extreme_student(self, type_):
        if not self.controller.students:
            messagebox.showinfo("Info", "No students loaded.")
            return

        if type_ == "high":
            s = self.controller.get_highest_scorer()
            title = "Highest Performing Student"
        else:
            s = self.controller.get_lowest_scorer()
            title = "Lowest Performing Student"
            
        # Automatically go to the find page and show this student
        self.entry_search.delete(0, tk.END)
        self.entry_search.insert(0, s.code)
        self.show_page("individual")
        self.action_find_student()
        messagebox.showinfo("🎓 " + title, f"{title} is {s.name} ({s.percentage:.2f}%)")

    def update_stats_display(self):
        # Cleaning up old stats widgets before redrawing
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        if not self.controller.students:
            tk.Label(self.stats_container, text="No Data Available", font=FONT_SUBHEADER).pack()
            return

        count = len(self.controller.students)
        avg = self.controller.get_average_percentage()
        
        # Helper to draw statistic cards
        def draw_card(parent, title, value, color, row, col):
            card = tk.Frame(parent, bg="white", relief="raised", bd=1)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", ipadx=20, ipady=20)
            tk.Label(card, text=title, font=FONT_BODY, fg="#7f8c8d", bg="white").pack()
            tk.Label(card, text=value, font=("Segoe UI", 24, "bold"), fg=color, bg="white").pack()

        self.stats_container.columnconfigure(0, weight=1)
        self.stats_container.columnconfigure(1, weight=1)

        draw_card(self.stats_container, "Total Students", str(count), COLOR_ACCENT, 0, 0)
        draw_card(self.stats_container, "Class Average", f"{avg:.2f}%", COLOR_SUCCESS, 0, 1)

        tk.Label(self.stats_container, text="Grade Distribution", font=FONT_SUBHEADER, 
                 bg=COLOR_BG_MAIN).grid(row=1, column=0, columnspan=2, pady=(30, 10))

        dist_frame = tk.Frame(self.stats_container, bg="white")
        dist_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Calculating grade counts
        grades = {'A':0, 'B':0, 'C':0, 'D':0, 'F':0}
        for s in self.controller.students:
            grades[s.grade] += 1
        
        # Drawing grade bars
        for i, (g, c) in enumerate(grades.items()):
            f = tk.Frame(dist_frame, bg="#ecf0f1", padx=10, pady=5)
            f.pack(side="left", expand=True, fill="x", padx=2)
            tk.Label(f, text=f"Grade {g}", font=FONT_BOLD, bg="#ecf0f1").pack()
            tk.Label(f, text=str(c), font=FONT_SUBHEADER, fg=COLOR_SIDEBAR, bg="#ecf0f1").pack()

    # --- Actions triggered by Sidebar Buttons ---

    def action_add_student(self):
        # Open the pop-up form
        dialog = StudentForm(self, "Add New Student")
        self.wait_window(dialog) # Wait until it closes
        if dialog.result:
            success, msg = self.controller.add_student(dialog.result)
            if success:
                messagebox.showinfo("Success", msg)
                self.show_page("view_all")
            else:
                messagebox.showerror("Error", msg)

    def action_delete_student(self):
        code = simpledialog.askstring("Delete Student", "Enter Student Code to DELETE:")
        if code:
            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete student {code}?")
            if confirm:
                if self.controller.delete_student(code):
                    messagebox.showinfo("Success", "Student deleted.")
                    self.show_page("view_all")
                else:
                    messagebox.showerror("Error", "Student Code not found.")

    def action_update_student(self):
        code = simpledialog.askstring("Update Student", "Enter Student Code to UPDATE:")
        if not code: return
        student = self.controller.get_student_by_code(code)
        if not student:
            messagebox.showerror("Error", "Student not found.")
            return
        
        # Pass existing student to the form so it pre-fills the data
        dialog = StudentForm(self, f"Update Student: {student.name}", current_student=student)
        self.wait_window(dialog)
        if dialog.result:
            success, msg = self.controller.update_student(code, dialog.result)
            if success:
                messagebox.showinfo("Success", msg)
                self.show_page("view_all")
            else:
                messagebox.showerror("Error", msg)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()