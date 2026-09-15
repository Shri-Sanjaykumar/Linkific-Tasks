# Basic Sentiment Analysis using Machine Learning

Linkific AI/ML Internship — Month 1 Training (Day 14 Weekly Mini Project)

---

## Project Overview

This project implements an end-to-end sentiment classification system that determines the emotional polarity of text reviews. Building directly upon the Natural Language Processing (NLP) foundations and TF-IDF feature extraction techniques established on Day 13, this weekly mini-project applies supervised Machine Learning to classify real movie reviews into positive and negative sentiments.

---

## Problem Statement

In customer feedback, entertainment reviews, and social media platforms, opinionated text arrives primarily as unstructured natural language. Identifying consumer sentiment automatically allows organizations to understand public perception at scale. The objective is to preprocess raw text reviews, extract numerical TF-IDF feature weights, and train a supervised classifier capable of predicting sentiment polarity on unseen reviews.

---

## Objective

- Implement a standard four-stage text cleaning pipeline: Lowercasing, Tokenization, Stopword/Punctuation Filtering, and Text Reconstruction.
- Prevent data leakage by enforcing strict featurization ordering (Train/Test split performed before fitting TF-IDF).
- Convert cleaned text into high-dimensional numerical features using Term Frequency-Inverse Document Frequency (TF-IDF).
- Train a binary Logistic Regression classifier on the training set.
- Evaluate model generalization on held-out test data using Accuracy, Precision, Recall, F1-Score, and Confusion Matrix.
- Demonstrate out-of-sample inference on new test sentences using the fitted pipeline without retraining.

---

## Dataset

- **Dataset Name:** IMDb Movie Reviews Dataset
- **Total Records:** 1,000 real movie reviews
- **Class Balance:** Balanced — 500 Positive reviews (50.0%) and 500 Negative reviews (50.0%)
- **Attributes:** `review` (raw text string) and `sentiment` (target class label)
- **Data Quality:** Verified 0 missing values and 0 duplicate entries

---

## Methodology

### Text Preprocessing
1. **Lowercasing:** Converts all characters to lowercase to ensure casing uniformity.
2. **Tokenization:** Breaks continuous text into individual word units using NLTK's `word_tokenize()`.
3. **Stopword Removal:** Eliminates common non-informative English stopwords (NLTK corpus) and non-alphabetic punctuation.
4. **Cleaned Text Reconstruction:** Reassembles filtered tokens into clean, space-delimited text strings (reducing token volume by ~53.6%).

### TF-IDF Vectorization
The cleaned text is converted into numerical feature vectors using Scikit-learn's `TfidfVectorizer(max_features=2500)`. To prevent data leakage, the vectorizer vocabulary and IDF weights are learned strictly from the 800 training reviews, and subsequently applied to transform the 200 testing reviews.

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \left(\log\left(\frac{1 + |D|}{1 + \text{DF}(t, D)}\right) + 1\right)$$

### Machine Learning Model
**Logistic Regression (`max_iter=200`, `random_state=42`)** is used as the classification algorithm. It is ideally suited for high-dimensional, sparse TF-IDF text features, provides calibrated prediction probabilities, and yields an interpretable linear decision boundary.

---

## Model Evaluation

Evaluation was performed on 200 held-out test reviews (100 positive, 100 negative):

| Metric | Score | Percentage |
| :--- | :---: | :---: |
| **Accuracy** | **0.7550** | **75.50%** |
| **Precision (Positive)** | **0.7525** | **75.25%** |
| **Recall (Positive)** | **0.7600** | **76.00%** |
| **F1-Score (Positive)** | **0.7562** | **75.62%** |

### Confusion Matrix Breakdown
- **True Positives (TP):** 76 (Positive reviews correctly identified)
- **True Negatives (TN):** 75 (Negative reviews correctly identified)
- **False Positives (FP):** 25 (Negative reviews misclassified as positive)
- **False Negatives (FN):** 24 (Positive reviews misclassified as negative)
- **Total Correct:** 151 / 200 (75.50%)
- **Total Misclassified:** 49 / 200 (24.50%)

---

## Visualizations

All generated charts are located in [`charts/`](charts/):

1. **Sentiment Class Distribution:** [`charts/sentiment_distribution.png`](charts/sentiment_distribution.png) — Verifies equal 50/50 balance of the dataset.
2. **Confusion Matrix Heatmap:** [`charts/confusion_matrix.png`](charts/confusion_matrix.png) — Annotated display of true vs. false predictions.
3. **Model Performance Metrics:** [`charts/model_performance.png`](charts/model_performance.png) — Direct comparison of Accuracy, Precision, Recall, and F1-Score.
4. **Sample Prediction Probabilities:** [`charts/sentiment_prediction.png`](charts/sentiment_prediction.png) — Decision threshold visualization for new out-of-sample sentences.

Project execution captures are documented in [`screenshots/`](screenshots/):
- [`screenshots/dataset_overview.png`](screenshots/dataset_overview.png)
- [`screenshots/preprocessing_output.png`](screenshots/preprocessing_output.png)
- [`screenshots/model_evaluation.png`](screenshots/model_evaluation.png)
- [`screenshots/prediction_output.png`](screenshots/prediction_output.png)

---

## Key Findings

1. **Balanced Generalization:** The model achieves 75.25% precision and 76.00% recall on held-out reviews, demonstrating balanced detection capability without bias toward either polarity.
2. **Noise Reduction Enhances Features:** Preprocessing eliminated over 53% of raw tokens (stopwords and punctuation), allowing TF-IDF to highlight sentiment-bearing keywords.
3. **Leakage Prevention:** By fitting `TfidfVectorizer` exclusively on the training split, test set evaluation accurately reflects real-world inference on unseen data.
4. **Out-of-Sample Inference:** The fitted pipeline successfully classified newly supplied positive and negative review sentences with confident probabilities (>74% and >75%).

---

## Limitations

1. **Context and Sarcasm:** Bag-of-words and n-gram TF-IDF representations ignore word sequence order, making complex sarcasm and irony difficult to detect.
2. **Domain Specificity:** The learned vocabulary is tuned to film terminology; applying the model directly to product reviews or financial sentiment may require domain adaptation.
3. **Binary Assumption:** Neutral, mixed, or ambiguous reviews are forced into a binary classification.

---

## Tools and Technologies

- **Programming Language:** Python 3.14
- **NLP & Tokenization:** NLTK (Natural Language Toolkit)
- **Machine Learning & Feature Extraction:** Scikit-learn (`TfidfVectorizer`, `LogisticRegression`)
- **Data Manipulation:** Pandas, NumPy
- **Visualization:** Matplotlib, Seaborn
- **Development Environment:** Jupyter Notebook, VS Code, Git

---

## Project Structure

```text
Day-14/
│
├── sentiment_analysis.ipynb          # Step-by-step interactive notebook with executed outputs
├── sentiment_analysis.py             # Reproducible standalone execution script
├── sentiment_data.csv                # 1,000 balanced IMDb reviews dataset
├── model_evaluation_results.csv      # Exported quantitative performance metrics
├── README.md                         # Comprehensive project documentation
│
├── charts/                           # Generated evaluation and analysis charts
│   ├── sentiment_distribution.png
│   ├── confusion_matrix.png
│   ├── model_performance.png
│   └── sentiment_prediction.png
│
└── screenshots/                      # Project execution visual captures
    ├── dataset_overview.png
    ├── preprocessing_output.png
    ├── model_evaluation.png
    ├── prediction_output.png
    └── README.md
```

---

## How to Run

1. Clone or navigate to the repository:
   ```bash
   cd Day-14
   ```
2. Execute the standalone Python script:
   ```bash
   python sentiment_analysis.py
   ```
3. Open and run the interactive notebook:
   ```bash
   jupyter notebook sentiment_analysis.ipynb
   ```

---

## Conclusion

This project successfully bridges text preprocessing and supervised machine learning into a complete sentiment analysis workflow. By combining lowercasing, tokenization, stopword removal, and TF-IDF feature extraction with Logistic Regression, the pipeline demonstrates how raw, unstructured human reviews can be processed into actionable sentiment predictions.

---

## Dataset Source

- **Citation:** Bo Pang and Lillian Lee. (2004). *A Sentimental Education: Sentiment Analysis Using Subjectivity Summarization Based on Minimum Cuts.* Proceedings of the 42nd Annual Meeting of the Association for Computational Linguistics (ACL-04), pp. 271–278.
- **Corpus Access:** NLTK `movie_reviews` corpus / Cornell Movie Review Data Archive.
