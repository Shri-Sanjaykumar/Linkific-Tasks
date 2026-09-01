# Day 4 – NumPy Fundamentals & Student Marks Analysis

- **Date:** 01 September 2026
- **Training Day:** Day 4
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Verified Environment:** Python 3.14.3 | NumPy 2.5.0

---

## 🎯 Objective

Understand why NumPy is the core foundational library for AI/ML and numerical computing, and practice creating, indexing, slicing, and performing mathematical operations on 1D and 2D arrays, followed by a practical **Student Marks Analysis**.

---

## 📖 Topics Practiced

- **NumPy Arrays:** Introduction to the `ndarray` object and why it is critical for AI/ML workflows (vectorization, contiguous memory layout, matrix mathematics).
- **1D and 2D Arrays:** Creating vectors and matrices, checking `.shape`, `.ndim`, and `.dtype`.
- **Indexing & Slicing:** Extracting individual elements and sub-arrays across rows and columns.
- **Mathematical Operations:** Using `sum()`, `mean()`, `max()`, and `min()` for fast array computations.
- **Python Lists vs. NumPy Arrays:** Comparing memory efficiency, data homogeneity, and vectorized arithmetic.

---

## 💻 How to Run

### Run the Python Script via Terminal
```bash
python numpy_practice.py
```

### Run the Jupyter Notebook
Open [`numpy_practice.ipynb`](numpy_practice.ipynb) in VS Code or JupyterLab and run all cells.

---

## 🖥️ Execution Output

```text
NumPy Version: 2.5.0

1D Array   : [10 20 30 40 50]
Shape      : (5,)
Dimensions : 1
Data Type  : int64

2D Array:
 [[10 20 30]
 [40 50 60]]
Shape      : (2, 3)
Dimensions : 2
Total Size : 6

1D Element [0]        : 10
1D Element [-1]       : 50
2D Element [Row 0, Col 1]: 20
2D Element [Row 1, Col 2]: 60

1D Slice [1:4]         : [20 30 40]
1D Slice [:3]          : [10 20 30]
2D First Row [0, :]    : [10 20 30]
2D Columns 1 to end:
 [[20 30]
 [50 60]]

Numbers Array          : [10 25 40 55 70]
Sum                    : 200
Mean                   : 40.0
Max                    : 70
Min                    : 10
Add 5                  : [15 30 45 60 75]
Multiply by 2          : [ 20  50  80 110 140]

List '+' (Concatenation): [1, 2, 3, 1, 2, 3]
NumPy '+' (Vector Addition): [2 4 6]

Student Marks Matrix:
 [[85 78 90]
 [92 88 95]
 [70 65 80]
 [88 82 84]]
Total Marks Across Class : 997
Overall Class Average     : 83.08
Highest Score in Class    : 95
Lowest Score in Class     : 65

Student 1: Total = 253, Average = 84.33%
Student 2: Total = 275, Average = 91.67%
Student 3: Total = 215, Average = 71.67%
Student 4: Total = 254, Average = 84.67%

Python Average: 83.75
Math Average: 78.25
AI Basics Average: 87.25
```

---

## 📦 Deliverables Summary

- [`numpy_practice.py`](numpy_practice.py) — Clean, executable Python script.
- [`numpy_practice.ipynb`](numpy_practice.ipynb) — Interactive Jupyter Notebook with all outputs.
- [`README.md`](README.md) — Documentation, concept mapping, and execution log.

---

## 🔗 Learning References

- [NumPy Official Documentation — Getting Started](https://numpy.org/doc/stable/user/absolute_beginners.html)
- [Krish Naik](https://www.youtube.com/@krishnaik06)
- [CampusX](https://www.youtube.com/@CampusX-official)
- [Codebasics](https://www.youtube.com/@codebasics)
