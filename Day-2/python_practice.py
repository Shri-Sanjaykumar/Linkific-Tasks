# Day 2 - Python Fundamentals Practice
# Topic: Variables, Data Types, Conditionals, Loops, and Functions

# ==========================================
# 1. Variables and Basic Data Types
# ==========================================

# String (text)
student_name = "Shri Sanjaykumar"

# Integer (whole number)
student_age = 20

# Float (decimal number)
course_completion = 75.5

# Boolean (True or False)
is_enrolled = True

print("=== 1. Variables & Data Types ===")
print("Name:", student_name, "| Type:", type(student_name))
print("Age:", student_age, "| Type:", type(student_age))
print("Completion:", course_completion, "% | Type:", type(course_completion))
print("Enrolled:", is_enrolled, "| Type:", type(is_enrolled))
print()

# ==========================================
# 2. Basic Arithmetic Operations
# ==========================================
num1 = 15
num2 = 4

print("=== 2. Arithmetic Operations ===")
print(f"{num1} + {num2} = {num1 + num2}")
print(f"{num1} - {num2} = {num1 - num2}")
print(f"{num1} * {num2} = {num1 * num2}")
print(f"{num1} / {num2} = {num1 / num2}")
print(f"{num1} // {num2} = {num1 // num2} (Integer Division)")
print(f"{num1} % {num2} = {num1 % num2} (Modulus / Remainder)")
print()

# ==========================================
# 3. Conditional Statements (if / elif / else)
# ==========================================
score = 82

print("=== 3. Conditional Statements ===")
print(f"Checking performance for score: {score}")

if score >= 90:
    print("Result: Excellent Performance")
elif score >= 75:
    print("Result: Good Performance")
elif score >= 50:
    print("Result: Average Performance")
else:
    print("Result: Needs Improvement")
print()

# ==========================================
# 4. Loops (for loop & while loop)
# ==========================================

print("=== 4. Loops Practice ===")

# For loop: Iterating through a range of numbers
print("Counting from 1 to 5 using for loop:")
for i in range(1, 6):
    print(f"Number: {i}")

# While loop: Repeating until a condition becomes False
print("\nCountdown using while loop:")
count = 3
while count > 0:
    print(f"Timer: {count}")
    count -= 1
print("Timer finished!")
print()

# ==========================================
# 5. Functions
# ==========================================

print("=== 5. Basic Functions ===")

# A simple greeting function
def greet_student(name):
    return f"Hello {name}, welcome to Day 2 Python training!"

# A function to calculate the square of a number
def calculate_square(number):
    return number * number

# Calling the functions
greeting_message = greet_student(student_name)
print(greeting_message)

test_number = 7
square_result = calculate_square(test_number)
print(f"The square of {test_number} is: {square_result}")
