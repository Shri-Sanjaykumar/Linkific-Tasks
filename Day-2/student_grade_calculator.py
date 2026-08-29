# Day 2 - Student Grade Calculator
# A simple program to calculate total marks, average percentage, and assign letter grades.

def main():
    print("========================================")
    print("      STUDENT GRADE CALCULATOR          ")
    print("========================================")

    # Taking student details as input
    student_name = input("Enter Student Name: ")
    num_subjects = int(input("Enter number of subjects: "))

    total_marks = 0

    # Taking marks input for each subject
    print("\n--- Enter Marks (out of 100 for each subject) ---")
    for i in range(1, num_subjects + 1):
        subject_mark = float(input(f"Enter marks for Subject {i}: "))
        total_marks += subject_mark

    # Calculating Average Percentage
    # Formula: Average = Total Marks / Number of Subjects
    max_possible_marks = num_subjects * 100
    average_marks = total_marks / num_subjects

    # Grading Logic:
    # 90% and above -> Grade A (Outstanding)
    # 80% to 89%    -> Grade B (Very Good)
    # 70% to 79%    -> Grade C (Good)
    # 60% to 69%    -> Grade D (Satisfactory)
    # 40% to 59%    -> Grade E (Pass)
    # Below 40%     -> Grade F (Fail)

    if average_marks >= 90:
        grade = "A"
        remarks = "Outstanding"
    elif average_marks >= 80:
        grade = "B"
        remarks = "Very Good"
    elif average_marks >= 70:
        grade = "C"
        remarks = "Good"
    elif average_marks >= 60:
        grade = "D"
        remarks = "Satisfactory"
    elif average_marks >= 40:
        grade = "E"
        remarks = "Pass"
    else:
        grade = "F"
        remarks = "Fail / Needs Improvement"

    # Displaying Results
    print("\n========================================")
    print("           REPORT SUMMARY               ")
    print("========================================")
    print(f"Student Name    : {student_name}")
    print(f"Total Subjects  : {num_subjects}")
    print(f"Total Marks     : {total_marks:.2f} / {max_possible_marks}")
    print(f"Average / %     : {average_marks:.2f}%")
    print(f"Grade Assigned  : {grade}")
    print(f"Status / Remarks: {remarks}")
    print("========================================")

if __name__ == "__main__":
    main()
