"""
Day 13 — Natural Language Processing (NLP) Practice
Linkific AI/ML Internship

Objective:
- Learn the fundamentals of Natural Language Processing.
- Perform text preprocessing: Lowercasing, Tokenization, Stopword Removal.
- Reconstruct preprocessed tokens into cleaned text.
- Apply TF-IDF Vectorization to convert text into numerical features.
- Export TF-IDF matrix and visualize top terms.
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer


def ensure_nltk_resources():
    """Ensure required NLTK resources are available."""
    for res in ["punkt", "punkt_tab", "stopwords"]:
        try:
            nltk.download(res, quiet=True)
        except Exception:
            pass


def tokenize_text(text):
    """Tokenize text into words with fallback."""
    try:
        return word_tokenize(text)
    except Exception:
        return re.findall(r"\b\w+\b", text)


def preprocess_document(text, stop_words):
    """
    Step-by-step preprocessing pipeline:
    1. Lowercasing
    2. Tokenization
    3. Stopword & punctuation removal
    4. Reconstructing cleaned text string
    """
    # 1. Lowercase
    lowered = text.lower()
    
    # 2. Tokenize
    tokens = tokenize_text(lowered)
    
    # 3. Stopword & punctuation removal
    filtered_tokens = [w for w in tokens if w.isalpha() and w not in stop_words]
    
    # 4. Reconstruct cleaned text string
    cleaned_text = " ".join(filtered_tokens)
    
    return lowered, tokens, filtered_tokens, cleaned_text


def main():
    print("=" * 65)
    print("DAY 13 — NATURAL LANGUAGE PROCESSING (NLP)")
    print("=" * 65)

    # Output directory for charts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    charts_dir = os.path.join(base_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # 1. Ensure NLTK resources
    ensure_nltk_resources()
    stop_words = set(stopwords.words("english"))

    # 2. Load text dataset
    data_path = os.path.join(base_dir, "text_data.csv")
    print(f"\n[1] Loading Dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Total documents loaded: {len(df)}")
    print("\nSample raw sentences:")
    for idx, row in df.head(3).iterrows():
        print(f" {idx + 1}. \"{row['text']}\"")

    # 3. Apply Text Preprocessing
    print("\n[2] Executing Preprocessing Pipeline...")
    lowered_list = []
    tokens_list = []
    filtered_list = []
    cleaned_list = []

    for text in df["text"]:
        lowered, tokens, filtered, cleaned = preprocess_document(text, stop_words)
        lowered_list.append(lowered)
        tokens_list.append(tokens)
        filtered_list.append(filtered)
        cleaned_list.append(cleaned)

    df["lowercased"] = lowered_list
    df["tokens"] = tokens_list
    df["filtered_tokens"] = filtered_list
    df["cleaned_text"] = cleaned_list

    # 4. Sample Preprocessing Transformation
    print("\n[3] Sample Preprocessing Transformation:")
    sample_idx = 0
    print(f"Original Text:        \"{df['text'].iloc[sample_idx]}\"")
    print(f"1. Lowercase:         \"{df['lowercased'].iloc[sample_idx]}\"")
    print(f"2. Tokenized:         {df['tokens'].iloc[sample_idx]}")
    print(f"3. Stopwords Removed: {df['filtered_tokens'].iloc[sample_idx]}")
    print(f"4. Reconstructed:     \"{df['cleaned_text'].iloc[sample_idx]}\"")

    # 5. TF-IDF Vectorization
    print("\n[4] Applying TF-IDF Vectorization...")
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["cleaned_text"])
    feature_names = tfidf_vectorizer.get_feature_names_out()

    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

    # 6. Save TF-IDF Output
    output_csv = os.path.join(base_dir, "tfidf_output.csv")
    tfidf_df.to_csv(output_csv, index=False)
    print(f"Saved TF-IDF matrix to: {output_csv}")

    # 7. TF-IDF Summary Statistics
    num_docs = tfidf_df.shape[0]
    vocab_size = tfidf_df.shape[1]
    print("\n[5] TF-IDF Matrix Summary:")
    print(f" - Number of documents:      {num_docs}")
    print(f" - Unique vocabulary terms:  {vocab_size}")
    print(f" - TF-IDF Matrix shape:      {tfidf_df.shape}")

    # Dynamic Top Features Inspection
    top_features = tfidf_df.mean(axis=0).sort_values(ascending=False).head(10)
    print("\n[6] Dynamic Top Features Inspection (First 5 Documents):")
    sample_inspection = tfidf_df[top_features.index].head(5).round(4)
    print(sample_inspection.to_string())

    # 8. Top TF-IDF Terms Analysis
    top10_terms = top_features.head(10)
    print("\nTop 10 Terms by Mean TF-IDF Score:")
    for rank, (term, score) in enumerate(top10_terms.items(), 1):
        print(f" {rank:2d}. {term:15s} : {score:.4f}")

    # 9. Visualization (Top 10 TF-IDF Terms)
    print("\n[7] Generating Top 10 TF-IDF Terms Chart...")
    plt.figure(figsize=(8, 5), dpi=150)
    
    y_pos = np.arange(len(top10_terms))
    terms = list(top10_terms.index)[::-1]
    scores = list(top10_terms.values)[::-1]

    bars = plt.barh(y_pos, scores, color="#2b5c8f", edgecolor="#333333", height=0.6)
    plt.yticks(y_pos, terms, fontsize=10)
    plt.xlabel("Mean TF-IDF Score", fontsize=10, labelpad=8)
    plt.title("Top 10 Terms by Mean TF-IDF Score", fontsize=12, fontweight="bold", pad=12)
    plt.xlim(0, max(scores) * 1.25)
    plt.grid(axis="x", linestyle="--", alpha=0.5)

    for bar, score in zip(bars, scores):
        width = bar.get_width()
        plt.text(
            width + 0.002,
            bar.get_y() + bar.get_height() / 2.0,
            f"{score:.4f}",
            ha="left", va="center", fontsize=9, fontweight="bold"
        )

    plt.tight_layout()
    chart_path = os.path.join(charts_dir, "tfidf_visualization.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"Saved chart to: {chart_path}")

    # 10. Key Observations (Computed at Runtime)
    print("\n" + "=" * 65)
    print("KEY OBSERVATIONS (DYNAMICALLY COMPUTED)")
    print("=" * 65)
    top_term, top_score = top10_terms.index[0], top10_terms.values[0]
    runner_up_term, runner_up_score = top10_terms.index[1], top10_terms.values[1]
    
    orig_total_words = sum(len(t) for t in df["tokens"])
    clean_total_words = sum(len(t) for t in df["filtered_tokens"])
    reduction_pct = ((orig_total_words - clean_total_words) / orig_total_words) * 100

    print(f"1. Top TF-IDF Term: '{top_term}' achieved the highest mean score of {top_score:.4f}, followed by '{runner_up_term}' ({runner_up_score:.4f}).")
    print(f"2. Stopword Filtering: Reduced total corpus words from {orig_total_words} to {clean_total_words} tokens ({reduction_pct:.1f}% reduction in non-informative words).")
    print(f"3. Vocabulary Size: The vectorizer identified {vocab_size} unique terms across all {num_docs} documents.")
    print(f"4. Matrix Dimensions: Produced an exact {num_docs}x{vocab_size} feature matrix with zero missing values.")
    print(f"5. Term Specificity: Domain-specific terms like '{top_term}', '{runner_up_term}', and '{top10_terms.index[2]}' carry the highest weights because they define document topics.")
    print("=" * 65)


if __name__ == "__main__":
    main()
