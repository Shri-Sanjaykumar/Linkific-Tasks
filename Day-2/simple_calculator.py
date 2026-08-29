# Day 2 - Simple Calculator
# A beginner-friendly calculator demonstrating Python functions and arithmetic operations.

# Function for addition
def add(num1, num2):
    return num1 + num2

# Function for subtraction
def subtract(num1, num2):
    return num1 - num2

# Function for multiplication
def multiply(num1, num2):
    return num1 * num2

# Function for division with zero-check
def divide(num1, num2):
    if num2 == 0:
        return "Error: Division by zero is not allowed."
    return num1 / num2

def main():
    print("========================================")
    print("           SIMPLE CALCULATOR            ")
    print("========================================")
    print("Supported Operations: +, -, *, /")
    print("----------------------------------------")

    # Taking inputs from user
    try:
        first_number = float(input("Enter First Number: "))
        operator = input("Enter Operator (+, -, *, /): ").strip()
        second_number = float(input("Enter Second Number: "))

        # Performing calculation based on selected operator
        if operator == "+":
            result = add(first_number, second_number)
            print(f"\nResult: {first_number} + {second_number} = {result}")
        elif operator == "-":
            result = subtract(first_number, second_number)
            print(f"\nResult: {first_number} - {second_number} = {result}")
        elif operator == "*":
            result = multiply(first_number, second_number)
            print(f"\nResult: {first_number} * {second_number} = {result}")
        elif operator == "/":
            result = divide(first_number, second_number)
            if isinstance(result, str):
                print(f"\n{result}")
            else:
                print(f"\nResult: {first_number} / {second_number} = {result}")
        else:
            print("\nError: Invalid operator entered. Please use +, -, *, or /.")

    except ValueError:
        print("\nError: Invalid numeric input entered.")

    print("========================================")

if __name__ == "__main__":
    main()
