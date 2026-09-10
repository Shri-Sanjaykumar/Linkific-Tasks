"""
Day 11 — Classification Machine Learning Task
Linkific AI/ML Internship

This script demonstrates the complete beginner-friendly classification workflow:
1. Load the standard Iris dataset dynamically from Scikit-learn
2. Inspect and understand dataset structure (150 samples, 4 features, 3 classes)
3. Select features (X) and target class (y)
4. Split into training (80%) and testing (20%) sets using stratified sampling
5. Train and evaluate a Logistic Regression model
6. Train and evaluate a Decision Tree model
7. Compare both models dynamically using accuracy
8. Save model accuracy comparison and class distribution charts
"""

import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend to avoid blocking GUI
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


def verify_environment():
    """Verify environment and library availability."""
    print("=" * 65)
    print("STEP 1: VERIFY ENVIRONMENT")
    print("=" * 65)
    print(f"Python Version: {sys.version.split()[0]}")
    import sklearn
    print(f"Scikit-learn Version: {sklearn.__version__}")
    print("Environment verified successfully.\n")


def load_dataset():
    """Load the Iris dataset dynamically from Scikit-learn."""
    print("=" * 65)
    print("STEP 2: LOAD IRIS DATASET")
    print("=" * 65)
    iris = load_iris()
    
    # Create DataFrame from Iris data and feature names
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["target"] = iris.target
    
    # Add human-readable species name mapping for exploration
    species_map = {idx: name for idx, name in enumerate(iris.target_names)}
    df["species"] = df["target"].map(species_map)
    
    print(f"Dataset Loaded Successfully: {df.shape[0]} samples, {len(iris.feature_names)} features, {len(iris.target_names)} classes.")
    print("\nFeature Names:")
    for feat in iris.feature_names:
        print(f" - {feat}")
    print("\nTarget Classes:")
    for idx, name in species_map.items():
        print(f" - Class {idx}: {name}")
    print(f"\nMissing Values:\n{df.isnull().sum().to_dict()}")
    print("\nClass Distribution:")
    print(df["species"].value_counts().to_string())
    print("\nFirst 5 Records:")
    print(df.head(5).to_string(index=False))
    print()
    return df, iris


def select_features_and_target(df, iris):
    """Isolate feature matrix X and target vector y."""
    print("=" * 65)
    print("STEP 3: FEATURE AND TARGET SELECTION")
    print("=" * 65)
    X = df[iris.feature_names]
    y = df["target"]
    
    print(f"Feature Matrix (X) Shape: {X.shape} (4 continuous flower measurements)")
    print(f"Target Vector  (y) Shape: {y.shape} (discrete species codes 0, 1, 2)\n")
    return X, y


def split_dataset(X, y):
    """
    Split into 80% training and 20% testing sets.
    Using stratify=y preserves class proportions across both splits.
    random_state=42 ensures exact reproducibility.
    """
    print("=" * 65)
    print("STEP 4: STRATIFIED TRAIN-TEST SPLIT")
    print("=" * 65)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training Set: {len(X_train)} samples (80%)")
    print(f"Testing Set:  {len(X_test)} samples (20%)")
    print(f"Testing Class Counts:\n{y_test.value_counts().sort_index().to_dict()} (Exactly 10 per class)")
    print("Both models will be trained and evaluated on these exact identical splits.\n")
    return X_train, X_test, y_train, y_test


def train_logistic_regression(X_train, y_train, X_test, y_test):
    """Train and evaluate Logistic Regression classifier."""
    print("=" * 65)
    print("STEP 5: LOGISTIC REGRESSION MODEL")
    print("=" * 65)
    logistic_model = LogisticRegression(max_iter=200)
    logistic_model.fit(X_train, y_train)
    logistic_pred = logistic_model.predict(X_test)
    logistic_acc = accuracy_score(y_test, logistic_pred)
    
    print("Logistic Regression model trained with max_iter=200.")
    print(f"Logistic Regression Accuracy: {logistic_acc:.4f} ({logistic_acc * 100:.2f}%)")
    correct = (y_test == logistic_pred).sum()
    print(f"Correct Predictions on Test Set: {correct} / {len(y_test)}\n")
    return logistic_model, logistic_pred, logistic_acc


def train_decision_tree(X_train, y_train, X_test, y_test):
    """Train and evaluate Decision Tree classifier."""
    print("=" * 65)
    print("STEP 6: DECISION TREE MODEL")
    print("=" * 65)
    decision_tree = DecisionTreeClassifier(random_state=42)
    decision_tree.fit(X_train, y_train)
    tree_pred = decision_tree.predict(X_test)
    tree_acc = accuracy_score(y_test, tree_pred)
    
    print("Decision Tree model trained with random_state=42.")
    print(f"Decision Tree Accuracy:       {tree_acc:.4f} ({tree_acc * 100:.2f}%)")
    correct = (y_test == tree_pred).sum()
    print(f"Correct Predictions on Test Set: {correct} / {len(y_test)}\n")
    return decision_tree, tree_pred, tree_acc


def compare_models(logistic_acc, tree_acc, y_test, logistic_pred, tree_pred, iris):
    """Compare both models dynamically and record observations."""
    print("=" * 65)
    print("STEP 7: ACCURACY COMPARISON & OBSERVATIONS")
    print("=" * 65)
    comparison_df = pd.DataFrame({
        "Model": ["Logistic Regression", "Decision Tree"],
        "Accuracy": [logistic_acc, tree_acc],
        "Accuracy (%)": [f"{logistic_acc * 100:.2f}%", f"{tree_acc * 100:.2f}%"]
    })
    print("Model Accuracy Comparison Table:")
    print(comparison_df.to_string(index=False))
    
    difference = abs(logistic_acc - tree_acc)
    print(f"\nAccuracy Difference: {difference:.4f} ({difference * 100:.2f}%)")
    
    # Dynamic comparison observation
    if logistic_acc > tree_acc:
        better_model = "Logistic Regression"
        print("Observation: Logistic Regression achieved higher accuracy on the test set.")
    elif tree_acc > logistic_acc:
        better_model = "Decision Tree"
        print("Observation: Decision Tree achieved higher accuracy on the test set.")
    else:
        better_model = "Both models tied"
        print("Observation: Both models achieved the same accuracy on the test set.")
        
    print("\nSample Prediction Results on Test Data (First 10 records):")
    species_names = iris.target_names
    pred_results_df = pd.DataFrame({
        "Actual Class": [species_names[i] for i in y_test.values[:10]],
        "Logistic Regression": [species_names[i] for i in logistic_pred[:10]],
        "Decision Tree": [species_names[i] for i in tree_pred[:10]]
    })
    print(pred_results_df.to_string(index=False))
    print()
    return comparison_df, better_model, difference


def create_visualizations(comparison_df, df, iris, output_dir="Day-11"):
    """Create and save comparison bar chart and class distribution plot."""
    print("=" * 65)
    print("STEP 8: VISUALIZATIONS")
    print("=" * 65)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Model Accuracy Comparison Bar Chart
    chart_path1 = os.path.join(output_dir, "model_accuracy_comparison.png")
    plt.figure(figsize=(7.5, 5), dpi=150)
    
    models = comparison_df["Model"].tolist()
    accuracies = comparison_df["Accuracy"].tolist()
    colors = ["#2b5c8f", "#2ca02c"]
    
    bars = plt.bar(models, accuracies, color=colors, width=0.48, edgecolor="#333333", linewidth=1.2)
    plt.title("Model Accuracy Comparison (Iris Dataset)", fontsize=13, fontweight="bold", pad=14)
    plt.xlabel("Classification Model", fontsize=11, labelpad=8)
    plt.ylabel("Accuracy Score", fontsize=11, labelpad=8)
    plt.ylim(0, 1.15)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    
    # Annotate accuracy percentages above bars dynamically
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.03,
            f"{acc * 100:.2f}%\n({acc:.4f})",
            ha="center", va="bottom", fontsize=10.5, fontweight="bold"
        )
        
    plt.tight_layout()
    plt.savefig(chart_path1)
    plt.close()
    print(f"Accuracy comparison chart saved to: {chart_path1}")
    
    # 2. Iris Class Distribution Scatter Plot (Petal Length vs Petal Width)
    chart_path2 = os.path.join(output_dir, "iris_class_distribution.png")
    plt.figure(figsize=(8, 5.2), dpi=150)
    
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    markers = ["o", "s", "^"]
    
    for idx, target_name in enumerate(iris.target_names):
        subset = df[df["target"] == idx]
        plt.scatter(
            subset["petal length (cm)"],
            subset["petal width (cm)"],
            label=f"Class {idx}: {target_name.capitalize()}",
            color=palette[idx],
            marker=markers[idx],
            s=50, alpha=0.85, edgecolors="#333333", linewidth=0.8
        )
        
    plt.title("Iris Class Distribution: Petal Length vs Petal Width", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Petal Length (cm)", fontsize=11)
    plt.ylabel("Petal Width (cm)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(frameon=True, facecolor="white", edgecolor="#cccccc", loc="upper left")
    plt.tight_layout()
    plt.savefig(chart_path2)
    plt.close()
    print(f"Iris class distribution chart saved to: {chart_path2}\n")


def main():
    print("\n" + "=" * 65)
    print("LINKIFIC AI/ML INTERNSHIP — DAY 11 CLASSIFICATION TASK")
    print("=" * 65 + "\n")
    
    # Step 1: Verify environment
    verify_environment()
    
    # Step 2: Load data
    df, iris = load_dataset()
    
    # Step 3: Feature and target selection
    X, y = select_features_and_target(df, iris)
    
    # Step 4: Train-test split
    X_train, X_test, y_train, y_test = split_dataset(X, y)
    
    # Step 5: Logistic Regression
    log_model, log_pred, log_acc = train_logistic_regression(X_train, y_train, X_test, y_test)
    
    # Step 6: Decision Tree
    tree_model, tree_pred, tree_acc = train_decision_tree(X_train, y_train, X_test, y_test)
    
    # Step 7: Compare models & record observations
    comparison_df, better_model, diff = compare_models(log_acc, tree_acc, y_test, log_pred, tree_pred, iris)
    
    # Step 8: Visualizations
    out_dir = "Day-11"
    if not os.path.exists("Day-11") and os.path.exists("Python/Day-11"):
        out_dir = "Python/Day-11"
    create_visualizations(comparison_df, df, iris, output_dir=out_dir)
    
    print("=" * 65)
    print("DAY 11 EXECUTION COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    main()
