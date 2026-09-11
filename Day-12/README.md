# Day 12 — Classification Model Evaluation

Linkific AI/ML Internship — Month 1 Training

---

## 🎯 Objective

Evaluate the classification models trained on Day 11 using standard Machine Learning evaluation metrics and answer the question: *Where is the model making its mistakes?*

---

## 📊 Dataset

- **Dataset:** Iris Dataset from Scikit-learn (`sklearn.datasets.load_iris`).
- **Samples:** 150 flower records.
- **Features (4):** Sepal Length, Sepal Width, Petal Length, Petal Width.
- **Target (3):** Setosa, Versicolor, Virginica (balanced, 50 samples each).

---

## 🤖 Models

1. **Logistic Regression:** `LogisticRegression(max_iter=200)`
2. **Decision Tree:** `DecisionTreeClassifier(random_state=42)`

Both models were trained on 80% training data (120 samples) and evaluated on the same 20% stratified test data (30 samples) as Day 11.

---

## 📐 Metrics Evaluated

- **Accuracy:** Overall proportion of correct predictions across all classes.
- **Precision (Weighted):** Exactness of positive class predictions (minimizing false alarms).
- **Recall (Weighted):** Completeness of positive class detections (minimizing missed samples).
- **F1 Score (Weighted):** Harmonic mean balancing precision and recall.
- **Confusion Matrix:** Breakdown of actual vs. predicted labels for each class.

---

## 🔄 Workflow

```text
Iris Dataset
     ↓
Same Day-11 80/20 Stratified Split
     ↓
 ┌───────────────┬────────────────┐
 ↓               ↓
Logistic       Decision Tree
Regression
 ↓               ↓
Predictions     Predictions
 └───────┬───────┘
         ↓
 Calculate Metrics (Accuracy, Precision, Recall, F1)
         ↓
 Confusion Matrices & Heatmaps
         ↓
 Performance Comparison & Bar Chart
         ↓
 Dynamic Observations & Metric Selection
```

---

## 📈 Results Summary

| Model | Accuracy | Precision (Weighted) | Recall (Weighted) | F1 Score (Weighted) | Errors |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **0.9667 (96.67%)** | **0.9697 (96.97%)** | **0.9667 (96.67%)** | **0.9666 (96.66%)** | **1 / 30** |
| **Decision Tree** | 0.9333 (93.33%) | 0.9333 (93.33%) | 0.9333 (93.33%) | 0.9333 (93.33%) | 2 / 30 |

---

## 📉 Visualizations

All charts are saved in [`Day-12/charts/`](charts/):

1. **Logistic Regression Confusion Matrix:** [`charts/logistic_confusion_matrix.png`](charts/logistic_confusion_matrix.png)
2. **Decision Tree Confusion Matrix:** [`charts/decision_tree_confusion_matrix.png`](charts/decision_tree_confusion_matrix.png)
3. **Model Performance Comparison:** [`charts/model_performance_comparison.png`](charts/model_performance_comparison.png)

---

## 💡 Key Learning

Model accuracy alone does not always provide the complete picture. For classification problems, combining multiple evaluation metrics (Precision, Recall, F1 Score) with Confusion Matrices reveals exactly which classes a model handles with ease and where specific misclassifications occur.

---

## 📁 Files in This Directory

- `model_evaluation.ipynb`: Interactive Jupyter notebook with complete step-by-step evaluation, embedded charts, and classification reports.
- `model_evaluation.py`: Standalone Python script executing the evaluation and generating charts.
- `performance_report.md`: Detailed performance report document.
- `README.md`: Overview documentation.
- `charts/`: Directory containing all evaluation figures.
