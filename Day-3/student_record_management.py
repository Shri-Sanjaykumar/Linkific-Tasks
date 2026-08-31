import os

# Tuple containing fixed subjects
SUBJECTS = ("Python", "Math", "Data Science")
FILE_NAME = "students.txt"


def load_records():
    students = []
    registered_rolls = set()

    if not os.path.exists(FILE_NAME):
        return students, registered_rolls

    with open(FILE_NAME, "r") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) >= 2 + len(SUBJECTS):
                roll_no = parts[0]
                name = parts[1]
                marks = [float(m) for m in parts[2:]]
                
                record = {
                    "roll_no": roll_no,
                    "name": name,
                    "marks": marks
                }
                students.append(record)
                registered_rolls.add(roll_no)

    return students, registered_rolls


def save_record_to_file(record):
    with open(FILE_NAME, "a") as file:
        marks_str = ",".join(str(m) for m in record["marks"])
        file.write(f"{record['roll_no']},{record['name']},{marks_str}\n")


def add_student(students, registered_rolls):
    print("\n--- Add New Student ---")
    roll_no = input("Enter Roll Number: ").strip()

    if roll_no in registered_rolls:
        print("Error: Roll number already exists.")
        return

    name = input("Enter Student Name: ").strip()
    marks = []

    print(f"Enter marks for subjects {SUBJECTS}:")
    for subject in SUBJECTS:
        while True:
            try:
                score = float(input(f"  {subject}: "))
                if 0 <= score <= 100:
                    marks.append(score)
                    break
                else:
                    print("  Please enter a valid score between 0 and 100.")
            except ValueError:
                print("  Invalid number. Please try again.")

    # Dictionary to store individual student record
    student_record = {
        "roll_no": roll_no,
        "name": name,
        "marks": marks
    }

    students.append(student_record)
    registered_rolls.add(roll_no)
    save_record_to_file(student_record)
    print(f"Record for {name} saved successfully!")


def view_students(students):
    print("\n--- Student Records ---")
    if not students:
        print("No student records found.")
        return

    print(f"{'Roll No':<10} {'Name':<20} {'Marks (' + ', '.join(SUBJECTS) + ')':<30} {'Average':<8}")
    print("-" * 72)

    for s in students:
        marks_display = ", ".join(f"{m:.1f}" for m in s["marks"])
        avg = sum(s["marks"]) / len(s["marks"])
        print(f"{s['roll_no']:<10} {s['name']:<20} {marks_display:<30} {avg:<8.2f}")


def main():
    students, registered_rolls = load_records()

    while True:
        print("\n=== Student Record Management System ===")
        print("1. Add Student")
        print("2. View Students")
        print("3. Exit")

        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            add_student(students, registered_rolls)
        elif choice == "2":
            view_students(students)
        elif choice == "3":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
