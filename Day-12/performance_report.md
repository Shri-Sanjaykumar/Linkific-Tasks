# Day 12 - Model Evaluation Report

Linkific AI/ML Internship — Month 1 Training

---

## Dataset

- **Dataset Name:** Iris Dataset (Scikit-learn `load_iris()`)
- **Total Samples:** 150 samples
- **Input Features (4):** `sepal length (cm)`, `sepal width (cm)`, `petal length (cm)`, `petal width (cm)`
- **Target Classes (3):** `setosa`, `versicolor`, `virginica` (balanced, 50 samples each)
- **Train/Test Split:** 80% training (120 samples), 20% testing (30 samples) with `stratify=y`

---

## Models Evaluated

1. **Logistic Regression:** Linear classification algorithm (`max_iter=200`).
2. **Decision Tree:** Non-linear rule-based tree classifier (`random_state=42`).

Both models were trained on the exact same training set and evaluated on the exact same unseen test set.

---

## Evaluation Metrics

- **Accuracy:** Measures the proportion of total predictions that were correct:
  $$\text{Accuracy} = \frac{\text{Correct Predictions}}{\text{Total Predictions}}$$
- **Precision (Weighted):** Measures the proportion of positive predictions that were actually correct for each class, weighted by class frequency:
  $$\text{Precision} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$$
- **Recall (Weighted):** Measures the proportion of actual class instances correctly identified by the model, weighted by class frequency:
  $$\text{Recall} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$$
- **F1 Score (Weighted):** The harmonic mean of precision and recall, balancing precision and recall across all classes:
  $$\text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

## Results

### Performance Comparison Table

| Model | Accuracy | Precision (Weighted) | Recall (Weighted) | F1 Score (Weighted) |
| :--- | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **0.9667 (96.67%)** | **0.9697 (96.97%)** | **0.9667 (96.67%)** | **0.9666 (96.66%)** |
| **Decision Tree** | 0.9333 (93.33%) | 0.9333 (93.33%) | 0.9333 (93.33%) | 0.9333 (93.33%) |

---

## Confusion Matrix Findings

The Confusion Matrices allow us to inspect exactly where predictions were correct and which classes were confused:

### 1. Logistic Regression
- **Setosa**: 10/10 samples correctly predicted (100% correct, 0 errors).
- **Versicolor**: 9/10 samples correctly predicted (1 sample(s) predicted as 'Virginica').
- **Virginica**: 10/10 samples correctly predicted (100% correct, 0 errors).
- **Total Errors:** 1 out of 30 test samples.

### 2. Decision Tree
- **Setosa**: 10/10 samples correctly predicted (100% correct, 0 errors).
- **Versicolor**: 9/10 samples correctly predicted (1 sample(s) predicted as 'Virginica').
- **Virginica**: 9/10 samples correctly predicted (1 sample(s) predicted as 'Versicolor').
- **Total Errors:** 2 out of 30 test samples.

---

## Model Comparison

**Logistic Regression** outperformed Decision Tree on this test split by **+3.33%** in accuracy, achieving higher scores across Precision, Recall, and F1 Score with fewer total classification errors (1 error vs. 2 errors).

Both models demonstrated high overall performance (>93% across all metrics), indicating that the 4 morphological features of the Iris dataset provide strong predictive signals.

---

## Most Useful Metric

For this Iris classification problem, **Accuracy is a suitable primary evaluation metric** because:
1. **Class Balance:** The Iris dataset has balanced classes (50 samples per species overall, and exactly 10 samples per species in the test split). Accuracy does not suffer from majority-class distortion on balanced data.
2. **Symmetric Error Costs:** There is no real-world asymmetrical cost where one specific type of misclassification is significantly more damaging than another (unlike medical diagnostics or fraud detection).

However, **Precision, Recall, and F1 Score provide valuable supplementary insights**:
- Precision reveals whether positive predictions for a given class include false alarms.
- Recall reveals whether actual instances of a class were missed.
- F1 Score confirms that precision and recall are harmoniously balanced.
- The Confusion Matrix pinpoints the exact class pairs where confusion occurred.

---

## Conclusion

By expanding our evaluation from simple accuracy to a complete metric suite (Precision, Recall, F1 Score, and Confusion Matrices), we gained a clear answer to the central question: *Where is the model making errors?*

Both models proved effective, with Logistic Regression achieving slightly higher precision and recall on this test split. This exercise highlights the importance of evaluating models from multiple perspectives rather than relying on a single metric.
