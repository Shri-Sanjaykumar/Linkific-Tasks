"""
Day 12 — Classification Model Evaluation & Performance Metrics
Linkific AI/ML Internship

Objective:
- Recreate and evaluate the classification models from Day 11 (Logistic Regression and Decision Tree).
- Compute key classification metrics: Accuracy, Precision, Recall, and F1 Score (weighted).
- Generate and interpret Confusion Matrices for both models.
- Determine which evaluation metric is most useful for the Iris dataset.
- Save evaluation charts and print data-driven observations.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


def evaluate_model(model_name, y_true, y_pred):
    """Calculate key classification evaluation metrics dynamically."""
    return {
        "Model": model_name,
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred, average="weighted"),
        "Recall": recall_score(y_true, y_pred, average="weighted"),
        "F1 Score": f1_score(y_true, y_pred, average="weighted")
    }


def analyze_confusion_matrix(cm, class_names):
    """Dynamically analyze confusion matrix without hardcoded assumptions."""
    total_samples = int(cm.sum())
    correct_samples = int(np.trace(cm))
    error_samples = total_samples - correct_samples
    
    class_summaries = []
    errors = []
    
    for i, actual_class in enumerate(class_names):
        actual_total = int(cm[i, :].sum())
        correct = int(cm[i, i])
        class_errors = actual_total - correct
        class_summaries.append({
            "class": actual_class,
            "correct": correct,
            "total": actual_total,
            "errors": class_errors
        })
        for j, pred_class in enumerate(class_names):
            if i != j and cm[i, j] > 0:
                errors.append(f"{int(cm[i, j])} sample(s) of '{actual_class}' misclassified as '{pred_class}'")
                
    return {
        "total_samples": total_samples,
        "correct_samples": correct_samples,
        "error_samples": error_samples,
        "class_summaries": class_summaries,
        "errors": errors
    }


def main():
    print("=" * 65)
    print("DAY 12 — CLASSIFICATION MODEL EVALUATION & METRICS")
    print("=" * 65)

    # Output directory for charts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    charts_dir = os.path.join(base_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # 1. Load the Iris Dataset dynamically
    print("\n[Step 1] Loading Iris Dataset...")
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = iris.target
    species_map = {idx: name for idx, name in enumerate(iris.target_names)}
    df["species"] = df["target"].map(species_map)

    print(f"Dataset Shape: {df.shape[0]} samples, {len(iris.feature_names)} features, {len(iris.target_names)} classes.")
    print("\nClass Distribution:")
    print(df["species"].value_counts().to_string())

    # 2. Features and Target
    print("\n[Step 2] Selecting Features and Target...")
    X = df[iris.feature_names]
    y = df["target"]
    print(f"Features: {list(X.columns)}")
    print(f"Target classes: {list(iris.target_names)}")

    # 3. Train-Test Split (Identical to Day 11: 80/20 Stratified)
    print("\n[Step 3] Applying 80/20 Stratified Train-Test Split...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Total samples:    {len(df)}")
    print(f"Training samples: {len(X_train)} (80%)")
    print(f"Testing samples:  {len(X_test)} (20%)")
    print(f"Number of classes: {len(iris.target_names)} ({dict(y_test.value_counts().sort_index())})")

    # 4. Train Day 11 Models
    print("\n[Step 4] Training Day 11 Models...")
    # Logistic Regression
    logistic_model = LogisticRegression(max_iter=200)
    logistic_model.fit(X_train, y_train)
    y_pred_logistic = logistic_model.predict(X_test)
    print(" - Logistic Regression trained successfully.")

    # Decision Tree
    decision_tree = DecisionTreeClassifier(random_state=42)
    decision_tree.fit(X_train, y_train)
    y_pred_tree = decision_tree.predict(X_test)
    print(" - Decision Tree trained successfully.")

    # 5. Dynamic Metrics Calculation
    print("\n[Step 5] Calculating Evaluation Metrics (average='weighted')...")
    metrics_log = evaluate_model("Logistic Regression", y_test, y_pred_logistic)
    metrics_tree = evaluate_model("Decision Tree", y_test, y_pred_tree)

    # 6. Performance Comparison Table
    print("\n[Step 6] Performance Comparison Table:")
    comparison_df = pd.DataFrame([metrics_log, metrics_tree])
    
    # Formatted display table
    display_df = comparison_df.copy()
    for col in ["Accuracy", "Precision", "Recall", "F1 Score"]:
        display_df[col] = display_df[col].apply(lambda v: f"{v:.4f} ({v * 100:.2f}%)")
    print(display_df.to_string(index=False))

    # 7. Confusion Matrices
    print("\n[Step 7] Generating Confusion Matrices...")
    cm_log = confusion_matrix(y_test, y_pred_logistic)
    cm_tree = confusion_matrix(y_test, y_pred_tree)

    # Plot Confusion Matrix: Logistic Regression
    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=150)
    sns.heatmap(
        cm_log, annot=True, fmt="d", cmap="Blues", cbar=False,
        xticklabels=iris.target_names, yticklabels=iris.target_names,
        annot_kws={"size": 13, "weight": "bold"}, ax=ax
    )
    ax.set_title("Logistic Regression - Confusion Matrix", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Predicted Class", fontsize=10, labelpad=8)
    ax.set_ylabel("Actual Class", fontsize=10, labelpad=8)
    plt.tight_layout()
    cm_log_path = os.path.join(charts_dir, "logistic_confusion_matrix.png")
    plt.savefig(cm_log_path)
    plt.close()
    print(f" - Saved Logistic Regression confusion matrix to: {cm_log_path}")

    # Plot Confusion Matrix: Decision Tree
    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=150)
    sns.heatmap(
        cm_tree, annot=True, fmt="d", cmap="Greens", cbar=False,
        xticklabels=iris.target_names, yticklabels=iris.target_names,
        annot_kws={"size": 13, "weight": "bold"}, ax=ax
    )
    ax.set_title("Decision Tree - Confusion Matrix", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Predicted Class", fontsize=10, labelpad=8)
    ax.set_ylabel("Actual Class", fontsize=10, labelpad=8)
    plt.tight_layout()
    cm_tree_path = os.path.join(charts_dir, "decision_tree_confusion_matrix.png")
    plt.savefig(cm_tree_path)
    plt.close()
    print(f" - Saved Decision Tree confusion matrix to: {cm_tree_path}")

    # 8. Dynamic Confusion Matrix Interpretation
    print("\n[Step 8] Dynamic Confusion Matrix Findings:")
    log_analysis = analyze_confusion_matrix(cm_log, iris.target_names)
    tree_analysis = analyze_confusion_matrix(cm_tree, iris.target_names)

    print("\n--- Logistic Regression Matrix Analysis ---")
    for cs in log_analysis["class_summaries"]:
        status = "100% correct" if cs["errors"] == 0 else f"{cs['errors']} misclassification(s)"
        print(f" - {cs['class'].capitalize()}: {cs['correct']}/{cs['total']} correct ({status})")
    if log_analysis["errors"]:
        print(f" - Misclassification detail: {', '.join(log_analysis['errors'])}")
    else:
        print(" - No misclassifications observed.")

    print("\n--- Decision Tree Matrix Analysis ---")
    for cs in tree_analysis["class_summaries"]:
        status = "100% correct" if cs["errors"] == 0 else f"{cs['errors']} misclassification(s)"
        print(f" - {cs['class'].capitalize()}: {cs['correct']}/{cs['total']} correct ({status})")
    if tree_analysis["errors"]:
        print(f" - Misclassification detail: {', '.join(tree_analysis['errors'])}")
    else:
        print(" - No misclassifications observed.")

    # 9. Classification Reports
    print("\n[Step 9] Classification Reports:")
    print("\n--- Logistic Regression Classification Report ---")
    print(classification_report(y_test, y_pred_logistic, target_names=iris.target_names))
    print("--- Decision Tree Classification Report ---")
    print(classification_report(y_test, y_pred_tree, target_names=iris.target_names))

    # 10. Performance Comparison Bar Chart
    print("\n[Step 10] Generating Performance Comparison Bar Chart...")
    metrics_list = ["Accuracy", "Precision", "Recall", "F1 Score"]
    x = np.arange(len(metrics_list))
    width = 0.35

    log_vals = [metrics_log[m] for m in metrics_list]
    tree_vals = [metrics_tree[m] for m in metrics_list]

    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=150)
    rects1 = ax.bar(x - width / 2, log_vals, width, label="Logistic Regression", color="#2b5c8f", edgecolor="#333333", linewidth=1)
    rects2 = ax.bar(x + width / 2, tree_vals, width, label="Decision Tree", color="#2ca02c", edgecolor="#333333", linewidth=1)

    ax.set_title("Classification Model Performance Comparison", fontsize=12, fontweight="bold", pad=14)
    ax.set_xlabel("Evaluation Metric", fontsize=10, labelpad=8)
    ax.set_ylabel("Score (0.0 to 1.0)", fontsize=10, labelpad=8)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_list, fontsize=10)
    ax.set_ylim(0.85, 1.05)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor="#cccccc", fontsize=9.5)

    def add_labels(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height * 100:.1f}%\n({height:.4f})",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center", va="bottom",
                fontsize=8.5, fontweight="bold"
            )

    add_labels(rects1)
    add_labels(rects2)

    plt.tight_layout()
    comp_chart_path = os.path.join(charts_dir, "model_performance_comparison.png")
    plt.savefig(comp_chart_path)
    plt.close()
    print(f" - Saved performance comparison chart to: {comp_chart_path}")

    # 11. Most Useful Metric Discussion
    print("\n" + "=" * 65)
    print("WHICH EVALUATION METRIC IS MOST USEFUL FOR THIS DATASET?")
    print("=" * 65)
    print("Analysis:")
    print("1. Problem Nature: The Iris dataset represents a multiclass classification task")
    print("   with 3 categories (Setosa, Versicolor, Virginica).")
    print("2. Class Balance: The dataset is perfectly balanced (50 samples per class overall,")
    print("   and exactly 10 samples per class in the held-out test split).")
    print("3. Symmetric Error Cost: Unlike cancer diagnosis (where false negatives carry severe consequences)")
    print("   or spam filtering (where false positives drop important emails), all classification errors here")
    print("   carry equal practical weight.")
    print("\nConclusion on Most Useful Metric:")
    print("For this Iris dataset, Accuracy is a suitable primary metric because the classes are")
    print("balanced and the goal is general classification correctness. Precision, Recall, and")
    print("F1 Score provide valuable supplementary insight into how errors are distributed among")
    print("specific individual classes.")

    # 12. Dynamic Observations
    print("\n" + "=" * 65)
    print("DYNAMIC OBSERVATIONS (COMPUTED AT RUNTIME)")
    print("=" * 65)

    # Top model determination
    if metrics_log["Accuracy"] > metrics_tree["Accuracy"]:
        top_model = "Logistic Regression"
        runner_up = "Decision Tree"
        margin = (metrics_log["Accuracy"] - metrics_tree["Accuracy"]) * 100
        better_summary = f"{top_model} achieved higher accuracy than {runner_up} (+{margin:.2f}%)."
    elif metrics_tree["Accuracy"] > metrics_log["Accuracy"]:
        top_model = "Decision Tree"
        runner_up = "Logistic Regression"
        margin = (metrics_tree["Accuracy"] - metrics_log["Accuracy"]) * 100
        better_summary = f"{top_model} achieved higher accuracy than {runner_up} (+{margin:.2f}%)."
    else:
        better_summary = "Both models achieved identical accuracy."

    # Error counts
    log_errs = log_analysis["error_samples"]
    tree_errs = tree_analysis["error_samples"]
    if log_errs < tree_errs:
        err_summary = f"Logistic Regression produced fewer misclassifications ({log_errs} error vs. {tree_errs} errors)."
    elif tree_errs < log_errs:
        err_summary = f"Decision Tree produced fewer misclassifications ({tree_errs} error vs. {log_errs} errors)."
    else:
        err_summary = f"Both models produced the same number of misclassifications ({log_errs} errors)."

    # Perfectly classified classes
    perfect_log = [cs["class"] for cs in log_analysis["class_summaries"] if cs["errors"] == 0]
    perfect_tree = [cs["class"] for cs in tree_analysis["class_summaries"] if cs["errors"] == 0]
    common_perfect = set(perfect_log).intersection(set(perfect_tree))

    print(f"1. {better_summary}")
    print(f"2. {err_summary}")
    if common_perfect:
        classes_str = ", ".join([c.capitalize() for c in common_perfect])
        print(f"3. Class '{classes_str}' was classified with 0 errors (100% accuracy) by both models.")
    else:
        print("3. Confusion matrix reveals differences in class-level classification difficulty.")
    print(f"4. Precision ({metrics_log['Precision']:.4f} vs. {metrics_tree['Precision']:.4f}) and Recall ({metrics_log['Recall']:.4f} vs. {metrics_tree['Recall']:.4f}) closely track Accuracy for both models.")
    print(f"5. The F1 Score confirms balanced overall performance ({metrics_log['F1 Score']:.4f} for Logistic Regression vs. {metrics_tree['F1 Score']:.4f} for Decision Tree).")
    print(f"6. Because the classes are balanced, Accuracy serves as an effective primary benchmark, while the confusion matrix pinpoints where misclassifications occur.")
    print("=" * 65)


if __name__ == "__main__":
    main()
