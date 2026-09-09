"""
Day 10 — Machine Learning Practice: Simple Linear Regression
Linkific AI/ML Internship

This script demonstrates the complete beginner-friendly Machine Learning workflow:
1. Load clean small dataset (Years of Experience vs Salary)
2. Inspect and understand data (shape, columns, null check)
3. Select Feature (X: YearsExperience) and Target (y: Salary)
4. Split into training (80%) and testing (20%) sets
5. Train a simple Linear Regression model using Scikit-learn
6. Make predictions on unseen test data
7. Evaluate performance (R² score, residuals)
8. Visualize actual data points vs. the fitted regression line
"""

import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend to avoid blocking GUI
import matplotlib.pyplot as plt
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def verify_environment():
    """Verify Scikit-learn installation and Python version."""
    print("=" * 60)
    print("STEP 1: VERIFY ENVIRONMENT")
    print("=" * 60)
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Scikit-learn Version: {sklearn.__version__}")
    print("Environment verified successfully.\n")


def load_dataset():
    """Load the small beginner dataset dynamically."""
    print("=" * 60)
    print("STEP 2: LOAD DATASET")
    print("=" * 60)
    possible_paths = [
        os.path.join("Day-10", "salary_data.csv"),
        "salary_data.csv",
        os.path.join("..", "Day-10", "salary_data.csv"),
        os.path.join("Python", "Day-10", "salary_data.csv"),
    ]
    
    dataset_path = None
    for path in possible_paths:
        if os.path.exists(path):
            dataset_path = path
            break
            
    if not dataset_path:
        raise FileNotFoundError("Could not find salary_data.csv in expected paths.")
        
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print("\nColumns and Data Types:")
    print(df.dtypes)
    print("\nMissing Values Count:")
    print(df.isnull().sum())
    print("\nFirst 5 Records:")
    print(df.head(5).to_string(index=False))
    print()
    return df


def prepare_features(df):
    """
    Select Feature matrix (X) and Target vector (y).
    
    Feature (X): YearsExperience (input feature)
    Target (y): Salary (value to predict)
    """
    print("=" * 60)
    print("STEP 3: SELECT FEATURE AND TARGET")
    print("=" * 60)
    
    # Drop any nulls if present
    model_df = df[["YearsExperience", "Salary"]].dropna()
    
    X = model_df[["YearsExperience"]]
    y = model_df["Salary"]
    
    print(f"Feature (X): YearsExperience -> shape: {X.shape}")
    print(f"Target (y):  Salary          -> shape: {y.shape}")
    print(f"Experience Range: {X['YearsExperience'].min()} to {X['YearsExperience'].max()} years")
    print(f"Salary Range:     ${y.min():,.2f} to ${y.max():,.2f}\n")
    return X, y


def split_data(X, y):
    """
    Split the dataset into training (80%) and testing (20%) subsets.
    random_state=42 guarantees reproducibility.
    """
    print("=" * 60)
    print("STEP 4: TRAIN / TEST SPLIT")
    print("=" * 60)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training Set: {len(X_train)} samples (80% of data)")
    print(f"Testing Set:  {len(X_test)} samples (20% of data)")
    print("Why split? We evaluate the model on unseen data it did not learn from.")
    print("random_state=42 ensures the same split is generated each time.\n")
    return X_train, X_test, y_train, y_test


def train_linear_regression(X_train, y_train):
    """Create and train a simple Linear Regression model."""
    print("=" * 60)
    print("STEP 5: TRAIN LINEAR REGRESSION MODEL")
    print("=" * 60)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    slope = model.coef_[0]
    intercept = model.intercept_
    
    print("Linear Regression model successfully trained using model.fit().")
    print(f"Slope (m / Coefficient): ${slope:,.2f}")
    print(f"Intercept (b):           ${intercept:,.2f}")
    print(f"Learned Equation:        Salary = (${slope:,.2f} * YearsExperience) + ${intercept:,.2f}")
    print("\nInterpretation:")
    print("The model learns an association between years of experience and salary.")
    print(f"On average, each additional year of experience is associated with a ${slope:,.2f} increase in salary.\n")
    return model


def evaluate_predictions(model, X_test, y_test):
    """Generate predictions on the test set and calculate evaluation metrics."""
    print("=" * 60)
    print("STEP 6: MAKE PREDICTIONS & EVALUATE")
    print("=" * 60)
    
    y_pred = model.predict(X_test)
    
    results = pd.DataFrame({
        "Years Experience": X_test["YearsExperience"].values,
        "Actual Salary ($)": y_test.values,
        "Predicted Salary ($)": y_pred.round(2),
        "Residual Error ($)": (y_test.values - y_pred).round(2)
    })
    
    print("Prediction Results on Unseen Test Data:")
    print(results.to_string(index=False))
    
    r2 = r2_score(y_test, y_pred)
    print(f"\nR² Score on Test Data: {r2:.4f} ({r2 * 100:.1f}% of variance explained)")
    print("The model demonstrates a strong linear relationship on this dataset.\n")
    return results, y_pred, r2


def create_visualization(X, y, model, output_path="Day-10/regression_plot.png"):
    """Create a clean scatter plot of actual data points and the fitted regression line."""
    print("=" * 60)
    print("STEP 7: REGRESSION VISUALIZATION")
    print("=" * 60)
    
    plt.figure(figsize=(8.5, 5.2), dpi=150)
    
    # Scatter plot of actual observations
    plt.scatter(
        X["YearsExperience"], y,
        color="#1f77b4", s=55, alpha=0.85, edgecolors="#0f4c81",
        label="Actual Employees (Data Points)"
    )
    
    # Fitted regression line
    sorted_exp = pd.DataFrame({"YearsExperience": sorted(X["YearsExperience"].unique())})
    line_pred = model.predict(sorted_exp)
    
    plt.plot(
        sorted_exp["YearsExperience"], line_pred,
        color="#d62728", linewidth=2.5,
        label="Fitted Linear Regression Line"
    )
    
    plt.title("Linear Regression: Years of Experience vs Salary", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Years of Experience", fontsize=11)
    plt.ylabel("Salary ($)", fontsize=11)
    
    # Format y-axis with currency labels
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda val, loc: f"${int(val):,}"))
    
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(frameon=True, facecolor="white", edgecolor="#cccccc", loc="upper left")
    plt.tight_layout()
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close()
    print(f"Regression plot successfully saved to: {output_path}\n")


def demonstrate_single_prediction(model, X_test):
    """Demonstrate a dynamic single prediction using an actual test sample."""
    print("=" * 60)
    print("STEP 8: DYNAMIC PREDICTION EXAMPLE")
    print("=" * 60)
    
    sample_exp = float(X_test.iloc[0]["YearsExperience"])
    sample_df = pd.DataFrame({"YearsExperience": [sample_exp]})
    sample_prediction = float(model.predict(sample_df)[0])
    
    print(f"Sample Input (Years of Experience): {sample_exp}")
    print(f"Predicted Salary:                   ${sample_prediction:,.2f}")
    print("Prediction was generated directly using model.predict().\n")


def main():
    print("\n" + "=" * 60)
    print("LINKIFIC AI/ML INTERNSHIP — DAY 10 ML PRACTICE")
    print("=" * 60 + "\n")
    
    # Step 1: Verify environment
    verify_environment()
    
    # Step 2: Load data
    df = load_dataset()
    
    # Step 3: Prepare feature and target
    X, y = prepare_features(df)
    
    # Step 4: Split data
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Step 5: Train model
    model = train_linear_regression(X_train, y_train)
    
    # Step 6: Make predictions and evaluate
    results, y_pred, r2 = evaluate_predictions(model, X_test, y_test)
    
    # Step 7: Visualize
    output_chart = "Day-10/regression_plot.png"
    if not os.path.exists("Day-10") and os.path.exists("Python/Day-10"):
        output_chart = "Python/Day-10/regression_plot.png"
    elif not os.path.exists("Day-10") and os.path.basename(os.getcwd()) == "Day-10":
        output_chart = "regression_plot.png"
    create_visualization(X, y, model, output_path=output_chart)
    
    # Step 8: Single sample demonstration
    demonstrate_single_prediction(model, X_test)
    
    print("=" * 60)
    print("MODEL INTERPRETATION & LIMITATION")
    print("=" * 60)
    print("The model demonstrates the core Machine Learning workflow from raw data")
    print("to evaluation. In real-world applications, salary is influenced by multiple")
    print("factors such as job role, industry, education, and geographic location.")
    print("This single-feature model serves as an accessible, hands-on learning foundation.\n")
    print("Day 10 execution completed successfully.")


if __name__ == "__main__":
    main()
