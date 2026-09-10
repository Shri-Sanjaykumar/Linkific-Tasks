"""
Day 11 — Classification Machine Learning Task
Linkific AI/ML Internship

Objective:
- Learn the basics of classification problems.
- Train Logistic Regression and Decision Tree models on the Iris dataset.
- Compare both models using accuracy.
- Record simple observations.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


def main():
    print("=" * 60)
    print("DAY 11 — CLASSIFICATION MACHINE LEARNING PRACTICE")
    print("=" * 60)

    # 1. Load Iris Dataset
    print("\n[Step 1] Loading Iris Dataset...")
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = iris.target
    species_map = {idx: name for idx, name in enumerate(iris.target_names)}
    df["species"] = df["target"].map(species_map)

    print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nClass Distribution:")
    print(df["species"].value_counts().to_string())
    print("\nFirst 5 Rows:")
    print(df.head(5).to_string())

    # 2. Feature and Target Selection
    print("\n[Step 2] Selecting Features and Target...")
    X = df[iris.feature_names]
    y = df["target"]
    print(f"Features: {list(X.columns)}")
    print(f"Target classes: {list(iris.target_names)}")

    # 3. Train-Test Split (80% Train, 20% Test)
    print("\n[Step 3] Splitting Dataset into Train and Test Sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Training set: {len(X_train)} samples")
    print(f"Testing set:  {len(X_test)} samples")
    print("The same test data was used for both models for comparison.")

    # 4. Train Logistic Regression Model
    print("\n[Step 4] Training Logistic Regression Model...")
    logistic_model = LogisticRegression(max_iter=200)
    logistic_model.fit(X_train, y_train)
    logistic_pred = logistic_model.predict(X_test)
    logistic_accuracy = accuracy_score(y_test, logistic_pred)
    logistic_correct = (y_test == logistic_pred).sum()

    print(f"Logistic Regression Accuracy: {logistic_accuracy:.4f} ({logistic_accuracy * 100:.2f}%)")
    print(f"Correct Predictions: {logistic_correct} out of {len(y_test)}")

    # 5. Train Decision Tree Model
    print("\n[Step 5] Training Decision Tree Model...")
    decision_tree = DecisionTreeClassifier(random_state=42)
    decision_tree.fit(X_train, y_train)
    tree_pred = decision_tree.predict(X_test)
    tree_accuracy = accuracy_score(y_test, tree_pred)
    tree_correct = (y_test == tree_pred).sum()

    print(f"Decision Tree Accuracy:       {tree_accuracy:.4f} ({tree_accuracy * 100:.2f}%)")
    print(f"Correct Predictions: {tree_correct} out of {len(y_test)}")

    # 6. Accuracy Comparison Table
    print("\n[Step 6] Accuracy Comparison Table:")
    comparison = pd.DataFrame({
        "Model": ["Logistic Regression", "Decision Tree"],
        "Correct / Total": [f"{logistic_correct} / {len(y_test)}", f"{tree_correct} / {len(y_test)}"],
        "Accuracy Score": [logistic_accuracy, tree_accuracy],
        "Accuracy (%)": [f"{logistic_accuracy * 100:.2f}%", f"{tree_accuracy * 100:.2f}%"]
    })
    print(comparison.to_string(index=False))

    # Sample Predictions Comparison
    species_names = iris.target_names
    sample_preds = pd.DataFrame({
        "Actual Class": [species_names[i] for i in y_test.values[:10]],
        "Logistic Regression": [species_names[i] for i in logistic_pred[:10]],
        "Decision Tree": [species_names[i] for i in tree_pred[:10]]
    })
    print("\nSample Predictions on First 10 Test Samples:")
    print(sample_preds.to_string(index=False))

    # 7. Visualization: Accuracy Comparison Bar Chart
    print("\n[Step 7] Generating Accuracy Comparison Bar Chart...")
    output_dir = os.path.dirname(os.path.abspath(__file__))
    chart_path = os.path.join(output_dir, "model_accuracy_comparison.png")

    plt.figure(figsize=(7, 4.8), dpi=150)
    models = ["Logistic Regression", "Decision Tree"]
    accuracies = [logistic_accuracy, tree_accuracy]
    colors = ["#2b5c8f", "#2ca02c"]

    bars = plt.bar(models, accuracies, color=colors, width=0.45, edgecolor="#333333", linewidth=1.1)
    plt.title("Model Accuracy Comparison (Iris Dataset)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Classification Model", fontsize=10, labelpad=8)
    plt.ylabel("Accuracy Score", fontsize=10, labelpad=8)
    plt.ylim(0, 1.15)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.03,
            f"{acc * 100:.2f}%\n({acc:.4f})",
            ha="center", va="bottom", fontsize=10, fontweight="bold"
        )

    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    print(f"Saved accuracy comparison chart to: {chart_path}")

    # 8. Dynamic Observations (2-3 simple points)
    print("\n" + "=" * 60)
    print("OBSERVATIONS (DYNAMICALLY COMPUTED)")
    print("=" * 60)

    if logistic_accuracy > tree_accuracy:
        better_model = "Logistic Regression"
        diff_pct = (logistic_accuracy - tree_accuracy) * 100
        better_text = f"{better_model} performed slightly better on this test split (+{diff_pct:.2f}%)."
    elif tree_accuracy > logistic_accuracy:
        better_model = "Decision Tree"
        diff_pct = (tree_accuracy - logistic_accuracy) * 100
        better_text = f"{better_model} performed slightly better on this test split (+{diff_pct:.2f}%)."
    else:
        better_text = "Both models achieved the same accuracy on this test split."

    print(f"1. Logistic Regression achieved {logistic_accuracy * 100:.2f}% accuracy ({logistic_correct}/{len(y_test)} correct).")
    print(f"2. Decision Tree achieved {tree_accuracy * 100:.2f}% accuracy ({tree_correct}/{len(y_test)} correct).")
    print(f"3. {better_text}")
    print("=" * 60)


if __name__ == "__main__":
    main()
