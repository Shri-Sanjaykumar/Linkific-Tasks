"""
Day 14 — Basic Sentiment Analysis using Machine Learning
Linkific AI/ML Internship — Month 1 Training

Objective:
- Build an end-to-end binary sentiment classification pipeline.
- Apply Day 13 NLP preprocessing techniques: Lowercasing, Tokenization, Stopword Removal.
- Transform text into numerical features using TF-IDF Vectorization without data leakage.
- Train and evaluate a Logistic Regression classifier on IMDb movie reviews.
- Generate dynamic evaluation metrics, confusion matrix, sample predictions, and charts.
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


def ensure_nltk_resources():
    """Ensure required NLTK resources are available."""
    for res in ["punkt", "punkt_tab", "stopwords"]:
        try:
            nltk.download(res, quiet=True)
        except Exception:
            pass


def tokenize_text(text):
    """Tokenize text into words with regex fallback."""
    try:
        return word_tokenize(text)
    except Exception:
        return re.findall(r"\b\w+\b", text)


def preprocess_text(text, stop_words):
    """
    Standard 4-step text preprocessing pipeline:
    1. Lowercasing
    2. Word Tokenization
    3. Stopword & non-alphabetic removal
    4. Reconstructing clean text string
    """
    lowered = text.lower()
    tokens = tokenize_text(lowered)
    filtered = [w for w in tokens if w.isalpha() and w not in stop_words]
    return " ".join(filtered)


def main():
    print("=" * 65)
    print("DAY 14 — BASIC SENTIMENT ANALYSIS USING MACHINE LEARNING")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    charts_dir = os.path.join(base_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # 1. Setup NLTK resources
    ensure_nltk_resources()
    stop_words = set(stopwords.words("english"))

    # 2. Load Dataset
    data_path = os.path.join(base_dir, "sentiment_data.csv")
    print(f"\n[1] Loading Dataset from: {data_path}")
    df = pd.read_csv(data_path)
    
    total_records = len(df)
    sentiment_counts = df["sentiment"].value_counts()
    null_counts = df.isnull().sum().sum()
    duplicate_counts = df.duplicated().sum()

    print(f"Total reviews loaded: {total_records}")
    print(f"Dataset Dimensions:   {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns:              {list(df.columns)}")
    print(f"Missing Values:       {null_counts}")
    print(f"Duplicate Records:    {duplicate_counts}")
    print("Sentiment Class Distribution:")
    for label, count in sentiment_counts.items():
        print(f" - {label.capitalize()}: {count} ({count / total_records * 100:.1f}%)")

    # 3. Clean Text Preprocessing
    print("\n[2] Preprocessing Text (Lowercasing, Tokenization, Stopword Removal)...")
    df["cleaned_text"] = df["review"].apply(lambda t: preprocess_text(t, stop_words))
    
    # Calculate sample preprocessing reduction
    sample_raw = df["review"].iloc[0]
    sample_clean = df["cleaned_text"].iloc[0]
    raw_tok_len = len(tokenize_text(sample_raw.lower()))
    clean_tok_len = len(sample_clean.split())
    print("\nSample Review Transformation:")
    print(f"Original Text (first 100 chars): \"{sample_raw[:100]}...\"")
    print(f"Cleaned Text  (first 100 chars): \"{sample_clean[:100]}...\"")
    print(f"Sample Token Reduction: {raw_tok_len} -> {clean_tok_len} tokens")

    # 4. Train-Test Split (Strict Leakage Prevention: Split before TF-IDF)
    print("\n[3] Splitting Dataset into Train and Test Sets (80/20 Stratified)...")
    X = df["cleaned_text"]
    y = df["sentiment"]

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training Samples: {len(X_train_text)} ({y_train.value_counts().to_dict()})")
    print(f"Testing Samples:  {len(X_test_text)} ({y_test.value_counts().to_dict()})")

    # 5. TF-IDF Vectorization
    print("\n[4] Fitting TF-IDF Vectorizer on Training Text...")
    vectorizer = TfidfVectorizer(max_features=2500)
    X_train_tfidf = vectorizer.fit_transform(X_train_text)
    X_test_tfidf = vectorizer.transform(X_test_text)
    vocab_size = len(vectorizer.get_feature_names_out())

    print(f"Vocabulary Size:          {vocab_size} terms")
    print(f"Training Feature Matrix:  {X_train_tfidf.shape}")
    print(f"Testing Feature Matrix:   {X_test_tfidf.shape}")

    # 6. Model Training — Logistic Regression
    print("\n[5] Training Logistic Regression Classifier...")
    model = LogisticRegression(random_state=42, max_iter=200)
    model.fit(X_train_tfidf, y_train)

    # 7. Model Prediction
    print("\n[6] Generating Predictions on Held-Out Test Set...")
    y_pred = model.predict(X_test_tfidf)
    y_pred_proba = model.predict_proba(X_test_tfidf)

    # 8. Evaluation Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label="positive")
    recall = recall_score(y_test, y_pred, pos_label="positive")
    f1 = f1_score(y_test, y_pred, pos_label="positive")
    cm = confusion_matrix(y_test, y_pred, labels=["negative", "positive"])

    tn, fp, fn, tp = cm.ravel()
    total_test = len(y_test)
    correct_count = tp + tn
    error_count = fp + fn

    print("\n" + "=" * 65)
    print("MODEL EVALUATION RESULTS")
    print("=" * 65)
    print(f"Accuracy:        {accuracy:.4f} ({accuracy * 100:.2f}%)")
    print(f"Precision (pos): {precision:.4f} ({precision * 100:.2f}%)")
    print(f"Recall (pos):    {recall:.4f} ({recall * 100:.2f}%)")
    print(f"F1-Score (pos):  {f1:.4f} ({f1 * 100:.2f}%)")
    print(f"Correct:         {correct_count} / {total_test}")
    print(f"Misclassified:   {error_count} / {total_test}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # 9. Save Evaluation Results CSV
    results_df = pd.DataFrame([
        {"Metric": "Accuracy", "Score": round(accuracy, 4)},
        {"Metric": "Precision", "Score": round(precision, 4)},
        {"Metric": "Recall", "Score": round(recall, 4)},
        {"Metric": "F1-Score", "Score": round(f1, 4)},
        {"Metric": "Test Samples", "Score": total_test},
        {"Metric": "Correct Predictions", "Score": correct_count},
        {"Metric": "Misclassifications", "Score": error_count}
    ])
    results_csv = os.path.join(base_dir, "model_evaluation_results.csv")
    results_df.to_csv(results_csv, index=False)
    print(f"Saved results to: {results_csv}")

    # 10. Visualizations
    print("\n[7] Generating Visualizations...")

    # Chart 1: Sentiment Distribution
    plt.figure(figsize=(6, 4.5), dpi=150)
    bars = plt.bar(
        [c.capitalize() for c in sentiment_counts.index],
        sentiment_counts.values,
        color=["#c0392b", "#27ae60"],
        edgecolor="#333333",
        width=0.5
    )
    plt.title("Sentiment Class Distribution in Dataset", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Sentiment Class", fontsize=10, labelpad=8)
    plt.ylabel("Number of Reviews", fontsize=10, labelpad=8)
    plt.ylim(0, max(sentiment_counts.values) * 1.2)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, h + 15, f"{int(h)}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    plt.tight_layout()
    chart1_path = os.path.join(charts_dir, "sentiment_distribution.png")
    plt.savefig(chart1_path)
    plt.close()
    print(f"Saved: {chart1_path}")

    # Chart 2: Confusion Matrix Heatmap
    plt.figure(figsize=(6, 5), dpi=150)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Negative", "Positive"],
        yticklabels=["Negative", "Positive"],
        cbar=False,
        annot_kws={"size": 13, "weight": "bold"}
    )
    plt.title("Confusion Matrix — Logistic Regression", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Predicted Sentiment", fontsize=10, labelpad=8)
    plt.ylabel("Actual Sentiment", fontsize=10, labelpad=8)
    plt.tight_layout()
    chart2_path = os.path.join(charts_dir, "confusion_matrix.png")
    plt.savefig(chart2_path)
    plt.close()
    print(f"Saved: {chart2_path}")

    # Chart 3: Model Performance Metrics
    plt.figure(figsize=(7, 4.8), dpi=150)
    metric_names = ["Accuracy", "Precision", "Recall", "F1-Score"]
    metric_vals = [accuracy, precision, recall, f1]
    perf_bars = plt.bar(
        metric_names,
        metric_vals,
        color=["#2980b9", "#16a085", "#8e44ad", "#d35400"],
        edgecolor="#333333",
        width=0.55
    )
    plt.title("Model Performance Metrics (Logistic Regression)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Evaluation Metric", fontsize=10, labelpad=8)
    plt.ylabel("Score (0 to 1.0)", fontsize=10, labelpad=8)
    plt.ylim(0, 1.15)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    for bar, val in zip(perf_bars, metric_vals):
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, h + 0.02, f"{val:.4f}\n({val*100:.1f}%)", ha="center", va="bottom", fontsize=9, fontweight="bold")
    plt.tight_layout()
    chart3_path = os.path.join(charts_dir, "model_performance.png")
    plt.savefig(chart3_path)
    plt.close()
    print(f"Saved: {chart3_path}")

    # Chart 3b: Combined Evaluation Summary (Confusion Matrix & Performance Metrics side-by-side)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), dpi=150)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Negative", "Positive"],
        yticklabels=["Negative", "Positive"],
        cbar=False,
        annot_kws={"size": 13, "weight": "bold"},
        ax=axes[0]
    )
    axes[0].set_title("Confusion Matrix", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Predicted Sentiment", fontsize=10)
    axes[0].set_ylabel("Actual Sentiment", fontsize=10)

    bars_comb = axes[1].bar(
        metric_names,
        metric_vals,
        color=["#2980b9", "#16a085", "#8e44ad", "#d35400"],
        edgecolor="#333333",
        width=0.5
    )
    axes[1].set_title("Model Evaluation Metrics", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Score (0 to 1.0)", fontsize=10)
    axes[1].set_ylim(0, 1.15)
    axes[1].grid(axis="y", linestyle="--", alpha=0.5)
    for bar, val in zip(bars_comb, metric_vals):
        h = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width() / 2.0, h + 0.02, f"{val:.4f}\n({val*100:.1f}%)", ha="center", va="bottom", fontsize=9, fontweight="bold")
    plt.tight_layout()
    chart_summary_path = os.path.join(charts_dir, "evaluation_summary.png")
    plt.savefig(chart_summary_path)
    plt.close()
    print(f"Saved: {chart_summary_path}")

    # Chart 4: Sample Prediction Probabilities
    demo_sentences = [
        "The cinematography was breathtaking and the performances were outstanding.",
        "A completely boring and predictable movie with terrible dialogue.",
        "An inspiring, heartfelt story that kept me thoroughly engaged throughout."
    ]
    demo_cleaned = [preprocess_text(s, stop_words) for s in demo_sentences]
    demo_tfidf = vectorizer.transform(demo_cleaned)
    demo_preds = model.predict(demo_tfidf)
    demo_probs = model.predict_proba(demo_tfidf)

    plt.figure(figsize=(8, 4.5), dpi=150)
    y_pos = np.arange(len(demo_sentences))
    pos_probs = [p[1] for p in demo_probs]
    colors = ["#27ae60" if p >= 0.5 else "#c0392b" for p in pos_probs]
    bars4 = plt.barh(y_pos, pos_probs, color=colors, edgecolor="#333333", height=0.5)
    plt.yticks(y_pos, [f"Sample {i+1}" for i in range(len(demo_sentences))], fontsize=10)
    plt.axvline(0.5, color="#7f8c8d", linestyle="--", linewidth=1.2, label="Decision Threshold (0.5)")
    plt.xlabel("Predicted Positive Probability", fontsize=10, labelpad=8)
    plt.title("Inference on New Out-of-Sample Sentences", fontsize=12, fontweight="bold", pad=12)
    plt.xlim(0, 1.2)
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.legend(loc="lower right")

    for bar, prob, pred in zip(bars4, pos_probs, demo_preds):
        w = bar.get_width()
        plt.text(w + 0.02, bar.get_y() + bar.get_height() / 2.0, f"P(Pos)={prob:.3f} -> {pred.upper()}", ha="left", va="center", fontsize=9, fontweight="bold")
    plt.tight_layout()
    chart4_path = os.path.join(charts_dir, "sentiment_prediction.png")
    plt.savefig(chart4_path)
    plt.close()
    print(f"Saved: {chart4_path}")

    # 11. Print Out-of-Sample Predictions
    print("\n[8] Inference on New Test Sentences:")
    for i, (sentence, pred, prob) in enumerate(zip(demo_sentences, demo_preds, demo_probs), 1):
        print(f" {i}. \"{sentence}\"")
        print(f"    -> Predicted Sentiment: {pred.upper()} (Positive Prob: {prob[1]:.4f}, Negative Prob: {prob[0]:.4f})")

    # 12. Dynamic Key Observations
    print("\n" + "=" * 65)
    print("KEY OBSERVATIONS (DYNAMICALLY COMPUTED)")
    print("=" * 65)
    print(f"1. Overall Accuracy: The Logistic Regression classifier achieved {accuracy * 100:.2f}% accuracy on 200 held-out test reviews.")
    print(f"2. Balanced Performance: Precision ({precision * 100:.2f}%) and Recall ({recall * 100:.2f}%) yielded an F1-Score of {f1 * 100:.2f}%.")
    print(f"3. Confusion Matrix Breakdown: {tp} True Positives, {tn} True Negatives, {fp} False Positives, and {fn} False Negatives.")
    print(f"4. Total Correct Classifications: {correct_count} out of {total_test} ({correct_count / total_test * 100:.1f}%).")
    print(f"5. Inference Capability: Successfully predicted out-of-sample sentiment using the fitted pipeline without retraining.")
    print("=" * 65)


if __name__ == "__main__":
    main()
