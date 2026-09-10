# Day 11 — Classification Machine Learning Practice

Linkific AI/ML Internship — Month 1 Training

---

## 🎯 Objectives

1. Learn the basics of classification problems in Supervised Learning.
2. Train a **Logistic Regression** model.
3. Train a **Decision Tree** model.
4. Compare both models using **Accuracy**.
5. Record simple observations from the results.
6. Push completed work to GitHub.

---

## 📊 Dataset

- **Dataset:** Scikit-learn built-in **Iris dataset** (`load_iris()`).
- **Samples:** 150 flower samples.
- **Features ($X$):** 4 continuous measurements:
  1. `sepal length (cm)`
  2. `sepal width (cm)`
  3. `petal length (cm)`
  4. `petal width (cm)`
- **Target ($y$):** 3 Iris species (balanced 50 samples each):
  - Class 0: `setosa`
  - Class 1: `versicolor`
  - Class 2: `virginica`

---

## 🤖 Models Used

### 1. Logistic Regression
- A popular linear classification algorithm that estimates class probabilities.
- Trained using `LogisticRegression(max_iter=200)`.

### 2. Decision Tree
- A non-linear classification algorithm that makes decisions using a series of if-else questions.
- Trained using `DecisionTreeClassifier(random_state=42)`.

---

## 🔄 Workflow

1. **Load Dataset:** Loaded the Iris dataset into a pandas DataFrame.
2. **Feature & Target Selection:** Isolated all 4 features ($X$) and the target species code ($y$).
3. **Train-Test Split:** Split the dataset into 80% training (120 samples) and 20% testing (30 samples) using `stratify=y` so all classes are equally represented. The same test data was used for both models for comparison.
4. **Train Models:** Fitted both models on `(X_train, y_train)` using `.fit()`.
5. **Predict & Evaluate:** Generated predictions on `X_test` using `.predict()` and calculated accuracy scores using `accuracy_score()`.

---

## 📈 Accuracy Comparison

Model accuracy is calculated as:
$$\text{Accuracy} = \frac{\text{Correct Predictions}}{\text{Total Test Samples}}$$

### Test Results ($N = 30$):

| Model | Correct Predictions | Total Samples | Accuracy Score | Accuracy (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **29** | **30** | **0.9667** | **96.67%** |
| **Decision Tree** | **28** | **30** | **0.9333** | **93.33%** |

---

## 📉 Visualization

### Model Accuracy Comparison Bar Chart
![Model Accuracy Comparison](model_accuracy_comparison.png)

---

## 📝 Observations (Dynamically Computed)

1. **Logistic Regression** achieved **96.67% accuracy** (29 out of 30 correct predictions).
2. **Decision Tree** achieved **93.33% accuracy** (28 out of 30 correct predictions).
3. **Logistic Regression performed slightly better** on this test split (+3.33% margin, 1 additional correct prediction).

---

## 📁 Files in This Directory

- `classification_practice.ipynb`: Clean Jupyter notebook covering the complete workflow from data loading to accuracy comparison.
- `classification_practice.py`: Python script implementing the classification workflow and dynamic evaluation.
- `model_accuracy_comparison.png`: Bar chart comparing the accuracy of both models.
- `README.md`: Documentation of objectives, workflow, results, and observations.
