import numpy as np

# 1. NumPy Version Verification
print(f"NumPy Version: {np.__version__}")
print()

# 2. 1D Array Creation & Properties
arr_1d = np.array([10, 20, 30, 40, 50])
print("1D Array   :", arr_1d)
print("Shape      :", arr_1d.shape)
print("Dimensions :", arr_1d.ndim)
print("Data Type  :", arr_1d.dtype)
print()

# 3. 2D Array Creation & Properties
arr_2d = np.array([
    [10, 20, 30],
    [40, 50, 60]
])
print("2D Array:\n", arr_2d)
print("Shape      :", arr_2d.shape)
print("Dimensions :", arr_2d.ndim)
print("Total Size :", arr_2d.size)
print()

# 4. Array Indexing
print("1D Element [0]        :", arr_1d[0])
print("1D Element [-1]       :", arr_1d[-1])
print("2D Element [Row 0, Col 1]:", arr_2d[0, 1])
print("2D Element [Row 1, Col 2]:", arr_2d[1, 2])
print()

# 5. Array Slicing
print("1D Slice [1:4]         :", arr_1d[1:4])
print("1D Slice [:3]          :", arr_1d[:3])
print("2D First Row [0, :]    :", arr_2d[0, :])
print("2D Columns 1 to end:\n", arr_2d[:, 1:])
print()

# 6. Basic Mathematical Operations
numbers = np.array([10, 25, 40, 55, 70])
print("Numbers Array          :", numbers)
print("Sum                    :", np.sum(numbers))
print("Mean                   :", np.mean(numbers))
print("Max                    :", np.max(numbers))
print("Min                    :", np.min(numbers))
print("Add 5                  :", numbers + 5)
print("Multiply by 2          :", numbers * 2)
print()

# 7. Python List vs NumPy Array
py_list = [1, 2, 3]
np_arr = np.array([1, 2, 3])
print("List '+' (Concatenation):", py_list + py_list)
print("NumPy '+' (Vector Addition):", np_arr + np_arr)
print()

# 8. Student Marks Analysis
# 4 Students x 3 Subjects (Python, Math, AI Basics)
marks = np.array([
    [85, 78, 90],
    [92, 88, 95],
    [70, 65, 80],
    [88, 82, 84]
])

print("Student Marks Matrix:\n", marks)
print(f"Total Marks Across Class : {np.sum(marks)}")
print(f"Overall Class Average     : {np.mean(marks):.2f}")
print(f"Highest Score in Class    : {np.max(marks)}")
print(f"Lowest Score in Class     : {np.min(marks)}")
print()

# Per-Student Performance (sum and mean across columns)
student_totals = np.sum(marks, axis=1)
student_averages = np.mean(marks, axis=1)
for i in range(len(student_totals)):
    print(f"Student {i+1}: Total = {student_totals[i]}, Average = {student_averages[i]:.2f}%")
print()

# Per-Subject Averages (mean down rows)
subject_names = ["Python", "Math", "AI Basics"]
subject_averages = np.mean(marks, axis=0)
for j in range(len(subject_averages)):
    print(f"{subject_names[j]} Average: {subject_averages[j]:.2f}")
