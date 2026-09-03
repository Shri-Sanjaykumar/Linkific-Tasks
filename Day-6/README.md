# Day 6 – Data Visualization

- **Date:** 03 September 2026
- **Training Day:** Day 6
- **Intern:** Shri Sanjaykumar V
- **Role:** AI/ML Intern
- **Verified Environment:** Python 3.14.3 | Pandas 3.0.3 | Matplotlib 3.11.0 | Seaborn 0.13.2

---

## 🎯 Objective

Understand the importance of data visualization in AI/ML workflows and create meaningful graphical charts (Bar, Line, Histogram, and Pie) using Matplotlib and Seaborn by dynamically reading the Day 5 employee dataset.

---

## 🛠️ Tools Used

- Python
- Pandas
- Matplotlib
- Seaborn
- Jupyter Notebook

---

## 📊 Visualizations Created

1. **Bar Chart:** Number of employees by Department (`plt.bar()`).
2. **Line Chart:** Employee salary across employee IDs (`plt.plot()`).
3. **Histogram:** Frequency distribution of employee ages (`plt.hist()`).
4. **Pie Chart:** Percentage proportion of employees by Department (`plt.pie()`).

---

## 📂 Dataset

- **Single Source of Truth:** Uses the **existing Day 5 dataset** directly via dynamic path `../Day-5/dataset.csv`.
- **Zero Duplication:** No duplicate dataset is created inside `Day-6/`. Any change to `Day-5/dataset.csv` automatically updates the visualizations upon running the code.

---

## 🔍 Observations (Based on Current Dataset)

1. **Department Representation:** Engineering has the highest representation with 4 employees (40% of the company).
2. **Department Breakdown:** HR is the second largest department with 3 employees (30%), followed by Data Science with 2 employees (20%), and Marketing with 1 employee (10%).
3. **Age Concentration:** Employee ages range between 24 and 35, with the highest concentration observed in the mid-to-late twenties (25–29).
4. **Salary Range:** Reported employee salaries range from 52,000 to 95,000 across all 10 recorded staff members.
5. **Department Proportions:** The pie chart illustrates that technical and core operations (Engineering & HR) represent 70% of the company's workforce.

---

## 💻 How to Run & Refresh Charts

### Run the Standalone Script
```bash
python data_visualization.py
```
*(Automatically reads `../Day-5/dataset.csv`, recalculates counts, and updates all images in `charts/`).*

### Run the Jupyter Notebook
Open [`data_visualization.ipynb`](data_visualization.ipynb) in VS Code and click **Run All**. It dynamically reads `../Day-5/dataset.csv` and re-renders all charts.

---

## 📦 Deliverables

- [`data_visualization.ipynb`](data_visualization.ipynb) — Interactive visualization notebook with dynamic dataset loading.
- [`data_visualization.py`](data_visualization.py) — Standalone executable script.
- `README.md` — Day 6 summary documentation.

---

## 🔗 Learning References

- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Seaborn Documentation](https://seaborn.pydata.org/)
- [Krish Naik](https://www.youtube.com/@krishnaik06)
- [Codebasics](https://www.youtube.com/@codebasics)
- [CampusX](https://www.youtube.com/@CampusX-official)
- [freeCodeCamp](https://www.youtube.com/@freecodecamp)
