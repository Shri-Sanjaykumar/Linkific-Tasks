# Day 3 – Python Data Structures & File Handling

- **Date:** 31 August 2026
- **Training Day:** Day 3
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Focus Area:** Python Data Structures (`list`, `tuple`, `dict`, `set`) and Flat-File Persistence (`with open`)

---

## 🎯 Overview & Objectives

The primary goal of Day 3 was to master Python's core data structures, understand their distinct properties (mutability, indexing, uniqueness, key-value mapping), and apply them alongside persistent file handling to build a console-based **Student Record Management System**.

---

## 🛠️ Concepts Breakdown: Where, Why & How Each is Used

The project was structured so that every fundamental data structure serves a specific, practical purpose:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                      STUDENT RECORD MANAGEMENT SYSTEM                   │
├─────────────────┬───────────────────┬───────────────────────────────────┤
│ Concept         │ Implementation    │ Why & How It Is Used              │
├─────────────────┼───────────────────┼───────────────────────────────────┤
│ 1. Tuple        │ SUBJECTS          │ Immutable fixed subjects tuple    │
│ 2. Set          │ registered_rolls  │ Fast O(1) duplicate prevention    │
│ 3. Dictionary   │ student_record    │ Structured key-value student data │
│ 4. List         │ students, marks   │ Ordered collection of all records │
│ 5. File I/O     │ with open(...)    │ Persistent read/append storage    │
└─────────────────┴───────────────────┴───────────────────────────────────┘
```

### 1. 🔹 Tuple (`tuple`) — Immutable Fixed Schema
- **Code Reference:**
  ```python
  SUBJECTS = ("Python", "Math", "Data Science")
  ```
- **Why Used:** Tuples are ordered and **immutable** (cannot be modified after creation). Since the curriculum subjects are constant and should not be accidentally altered during runtime, a tuple is the ideal structure.
- **How Used:** Iterated dynamically during user prompt (`for subject in SUBJECTS:`) and table header generation.

---

### 2. 🔹 Set (`set`) — Fast Unique Membership Checking
- **Code Reference:**
  ```python
  registered_rolls = set()
  registered_rolls.add(roll_no)
  ```
- **Why Used:** Sets store **unique elements only** and provide $O(1)$ constant-time lookup. 
- **How Used:** Before creating a student record, the program checks `if roll_no in registered_rolls:`. If present, it prevents duplicate roll numbers immediately without needing to scan the entire list of records.

---

### 3. 🔹 Dictionary (`dict`) — Key-Value Entity Modeling
- **Code Reference:**
  ```python
  student_record = {
      "roll_no": roll_no,
      "name": name,
      "marks": marks
  }
  ```
- **Why Used:** Dictionaries represent real-world entities through structured **key-value pairs**, allowing intuitive access to attributes (`record["name"]`, `record["marks"]`) rather than relying on arbitrary index positions.
- **How Used:** Each student's details are encapsulated in a dictionary before being added to the main list and saved to disk.

---

### 4. 🔹 List (`list`) — Dynamic Ordered Collections
- **Code Reference:**
  ```python
  students = []
  marks = []
  students.append(student_record)
  ```
- **Why Used:** Lists are **mutable and ordered**, making them the standard choice for growing collections of items.
- **How Used:** `marks` stores the numerical scores entered for each subject, and `students` holds the master list of all student dictionary objects.

---

### 5. 🔹 File Handling (`with open(...)`) — Persistent Storage
- **Code Reference:**
  ```python
  # Loading on startup:
  with open(FILE_NAME, "r") as file:
      for line in file:
          # parse comma-separated values

  # Appending new record:
  with open(FILE_NAME, "a") as file:
      file.write(f"{record['roll_no']},{record['name']},{marks_str}\n")
  ```
- **Why Used:** Data in memory is lost when the program terminates. Flat-file storage ensures records persist across sessions.
- **How Used:** Using Python's context manager (`with open(...)`) ensures automatic closing of file streams, preventing file corruption or memory leaks.

---

## 📂 Project Structure & Files

```text
Day-3/
├── README.md                     # Comprehensive documentation and concept mapping
├── student_record_management.py  # Main interactive Python script
└── students.txt                  # Flat-file database storing student records
```

---

## 🚀 How to Run and Use the Program

### Step 1: Run the Script
Open your terminal inside the `Day-3` directory and execute:
```bash
python student_record_management.py
```

### Step 2: Main Menu Options
Upon launch, the program automatically loads existing data from `students.txt` and displays the menu:
```text
=== Student Record Management System ===
1. Add Student
2. View Students
3. Exit
Enter your choice (1-3): 
```

- **Option `1` (Add Student):**
  - Prompts for Roll Number (validated against the unique set).
  - Prompts for Student Name.
  - Prompts for marks (0 to 100) for each subject defined in the `SUBJECTS` tuple.
  - Automatically appends the new record to `students.txt`.

- **Option `2` (View Students):**
  - Formats all saved records into a clean tabular view.
  - Computes and displays the average percentage for each student.

- **Option `3` (Exit):**
  - Safely terminates the console application.

---

## 💾 Data Storage Format (`students.txt`)

Data is stored in a clean, human-readable comma-separated format:
```text
101,Shri Sanjaykumar,85.0,90.0,88.0
102,Priya,92.0,95.0,91.0
```
- **Field 1:** Roll Number (`str`)
- **Field 2:** Student Name (`str`)
- **Fields 3+:** Subject Marks (`float`)

---

## 🖥️ Sample Execution Walkthrough

```text
=== Student Record Management System ===
1. Add Student
2. View Students
3. Exit
Enter your choice (1-3): 1

--- Add New Student ---
Enter Roll Number: 101
Enter Student Name: Shri Sanjaykumar
Enter marks for subjects ('Python', 'Math', 'Data Science'):
  Python: 85
  Math: 90
  Data Science: 88
Record for Shri Sanjaykumar saved successfully!

=== Student Record Management System ===
1. Add Student
2. View Students
3. Exit
Enter your choice (1-3): 2

--- Student Records ---
Roll No    Name                 Marks (Python, Math, Data Science) Average 
------------------------------------------------------------------------
101        Shri Sanjaykumar     85.0, 90.0, 88.0               87.67   
102        Priya                92.0, 95.0, 91.0               92.67   

=== Student Record Management System ===
1. Add Student
2. View Students
3. Exit
Enter your choice (1-3): 3
Exiting program. Goodbye!
```

---

## 📦 Deliverables Summary

- [`student_record_management.py`](student_record_management.py) — Complete source code implementing data structures and file I/O.
- [`students.txt`](students.txt) — Persistent data storage file.
- [`README.md`](README.md) — Detailed technical breakdown, usage instructions, and implementation rationale.
