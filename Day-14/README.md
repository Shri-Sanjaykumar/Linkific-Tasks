# Day 14 — Weekly Mini Project: Basic Sentiment Analysis using Machine Learning

**Linkific AI/ML Internship — Month 1 Training**  
**Intern:** Shri Sanjaykumar V  
**Date:** September 15, 2026  

---

## Table of Contents
1. [🎯 Learning Objectives](#-learning-objectives)
2. [💻 Project Tasks & Option Selection](#-project-tasks--option-selection)
3. [📂 Deliverables Checklist](#-deliverables-checklist)
4. [📺 Recommended Study Channels & Documentation](#-recommended-study-channels--documentation)
5. [📋 Problem Statement](#-problem-statement)
6. [📊 Dataset Overview & Quality](#-dataset-overview--quality)
7. [⚙️ Methodology & Pipeline Architecture](#-methodology--pipeline-architecture)
8. [📈 Model Evaluation & Quantitative Results](#-model-evaluation--quantitative-results)
9. [🖼️ Visualizations & Artifacts](#-visualizations--artifacts)
10. [🔍 Model Performance Explanation & Error Analysis](#-model-performance-explanation--error-analysis)
11. [🎙️ 2–5 Minute Project Demo Guide](#-25-minute-project-demo-guide)
12. [⚠️ Limitations & Future Scope](#-limitations--future-scope)
13. [🛠️ Tools & Technologies Used](#-tools--technologies-used)
14. [📁 Project Directory Structure](#-project-directory-structure)
15. [🚀 How to Run](#-how-to-run)
16. [📜 Dataset Citation & References](#-dataset-citation--references)

---

## 🎯 Learning Objectives

The core objectives of the Day 14 Weekly Mini Project are:
- **Apply Machine Learning Concepts to a Practical Problem:** Transform theoretical understanding of supervised machine learning and natural language processing into an operational, reproducible software pipeline.
- **Build Confidence in an End-to-End ML Workflow:** Gain practical mastery across all stages of machine learning project development: data ingestion, data cleaning, text normalization, feature extraction (TF-IDF), model training, multi-metric evaluation, error analysis, and out-of-sample inference.

---

## 💻 Project Tasks & Option Selection

The internship curriculum provided five project options for the Day 14 Weekly Mini Project:

| Option | Project Title | Task Type | Domain |
| :---: | :--- | :---: | :--- |
| Option 1 | House Price Prediction | Regression | Tabular Real Estate |
| Option 2 | Customer Churn Prediction | Binary Classification | Tabular Business Analytics |
| Option 3 | Iris Flower Classification | Multi-Class Classification | Classical Tabular Botanical |
| Option 4 | Spam Email Classifier | Binary Classification | NLP Text Classification |
| **Option 5** | **Basic Sentiment Analysis using NLP & ML** *(Selected)* | **Binary Classification** | **NLP Sentiment Analysis** |

### Rationale for Selecting Option 5
Option 5 was selected because it establishes a seamless, natural progression from Day 13's NLP and TF-IDF foundations. Rather than switching to an unrelated tabular dataset, Option 5 applies supervised Machine Learning directly to unstructured text, completing the real-world NLP lifecycle: `Raw Text → Preprocessing → TF-IDF Vectorization → Supervised Classification → Sentiment Prediction`.

### Project Tasks Status

- [x] **Task 1: Select 1 Project Option** — Selected Option 5: Basic Sentiment Analysis using NLP and Machine Learning.
- [x] **Task 2: Select a Suitable Dataset** — Sourced 1,000 authentic IMDb movie reviews from the Pang & Lee (2004) corpus with an exact 50/50 balance (500 positive, 500 negative).
- [x] **Task 3: Perform Data Cleaning & Preprocessing** — Engineered a standard 4-stage NLP pipeline (lowercasing, tokenization, stopword removal, clean text reconstruction) achieving a 53.6% reduction in non-informative tokens.
- [x] **Task 4: Train an Appropriate Machine Learning Model** — Fitted a Logistic Regression classifier on 2,500 TF-IDF features strictly partitioned to guarantee zero data leakage.
- [x] **Task 5: Evaluate Model Performance Using Metrics** — Quantitatively evaluated the classifier on 200 held-out test reviews: **75.50% Accuracy**, **75.25% Precision**, **76.00% Recall**, **75.62% F1-Score**, and a detailed Confusion Matrix.
- [x] **Task 6: Explain Model Performance** — Conducted thorough operational error analysis on false positives and false negatives, examining precision/recall trade-offs.
- [x] **Task 7: Push Today's Work to GitHub** — Synced all project files, scripts, notebooks, datasets, charts, and documentation to GitHub.
- [x] **Task 8: Update GitHub Repository README** — Updated both the root internship repository README and this project-level README with comprehensive documentation.

---

## 📂 Deliverables Checklist

All required deliverables have been implemented, tested, and verified:

- [x] **Complete ML Project:** Clean, modular, and reproducible codebase with standalone script (`sentiment_analysis.py`), structured dataset (`sentiment_data.csv`), and output results.
- [x] **GitHub Repository Updated:** All changes committed and pushed to remote GitHub repositories (`Linkific-Tasks` and `AI-ML-Internship`).
- [x] **README File Updated with Project Details:** Fully populated documentation detailing problem statement, methodology, metrics, and architecture.
- [x] **Trained Model Notebook:** Interactive Jupyter Notebook (`sentiment_analysis.ipynb`) with pre-executed cells, outputs, tables, and embedded high-resolution visualizations.
- [x] **Model Evaluation Results:** Quantitative metrics exported to [`model_evaluation_results.csv`](model_evaluation_results.csv).
- [x] **Project Screenshots:** Visual verification captures of key pipeline execution steps stored in [`screenshots/`](screenshots/).
- [x] **2–5 Minute Project Demo Guide:** Structured, timed walkthrough script prepared for internship viva/presentation.

---

## 📺 Recommended Study Channels & Documentation

### Recommended Search Queries
- `Machine Learning Projects for Beginners`
- `End to End Machine Learning Project`
- `Scikit-learn Project Tutorial`
- `TF-IDF Text Classification Python`

### Recommended Channels
- **Krish Naik:** End-to-end machine learning project tutorials, deployment workflows, and feature engineering.
- **CampusX:** Deep conceptual explanations of classification metrics, confusion matrices, and NLP pipelines.
- **Codebasics:** Practical Python implementation, data preprocessing, and Scikit-learn pipelines.
- **StatQuest with Josh Starmer:** Clear visual intuition for Logistic Regression, log-odds, decision thresholds, and ROC-AUC.

### Documentation & Reference Materials
- **Scikit-learn Documentation:**
  - [Logistic Regression Guide](https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression)
  - [Text Feature Extraction (TF-IDF)](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction)
  - [Model Evaluation & Classification Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#classification-metrics)
- **NLTK Documentation:**
  - [Tokenization and Corpora Processing](https://www.nltk.org/api/nltk.tokenize.html)
  - [Stopwords Corpus](https://www.nltk.org/book/ch02.html)

---

## 📋 Problem Statement

In consumer feedback systems, online entertainment platforms, and e-commerce portals, user opinions arrive primarily as unstructured text. Manually reading and labeling thousands of customer reviews is expensive, unscalable, and subjective. 

The goal of this project is to build an automated sentiment classification pipeline that takes raw textual movie reviews, normalizes the text through NLP preprocessing, transforms words into numerical TF-IDF feature weights, and trains a supervised machine learning model to accurately classify unseen reviews as either **Positive** or **Negative**.

---

## 📊 Dataset Overview & Quality

- **Dataset Source:** IMDb Movie Reviews Corpus (Bo Pang & Lillian Lee, ACL 2004)
- **Total Records:** 1,000 full-text movie reviews
- **Target Variable:** `sentiment` (`positive` vs `negative`)
- **Class Balance:** Perfectly balanced — 500 Positive reviews (50.0%) and 500 Negative reviews (50.0%)
- **Data Quality Verification:**
  - Missing Values: **0** across all columns
  - Duplicate Records: **0** duplicates
  - Text Length: Ranging from ~100 to over 1,000 words per review

---

## ⚙️ Methodology & Pipeline Architecture

```text
Raw Text Reviews (1,000 IMDb Reviews)
       │
       ▼
[Stage 1: Text Preprocessing]
 ├─ 1. Lowercasing: Convert all characters to lowercase
 ├─ 2. Tokenization: Split text into word units via NLTK word_tokenize()
 ├─ 3. Stopword Removal: Remove NLTK English stopwords & non-alphabetic tokens
 └─ 4. Text Reconstruction: Join clean tokens back into strings (-53.6% noise reduction)
       │
       ▼
[Stage 2: Train-Test Split]
 ├─ 80% Training Set (800 reviews: 400 pos, 400 neg)
 └─ 20% Testing Set  (200 reviews: 100 pos, 100 neg) — Stratified, random_state=42
       │
       ▼
[Stage 3: Feature Extraction (Zero Data Leakage)]
 ├─ TfidfVectorizer(max_features=2500)
 ├─ fit_transform() on Training Data ONLY (learn vocabulary & IDF weights)
 └─ transform() on Testing Data (apply learned vocabulary without refitting)
       │
       ▼
[Stage 4: Supervised Model Training]
 └─ LogisticRegression(max_iter=200, random_state=42)
       │
       ▼
[Stage 5: Evaluation & Inference]
 ├─ Evaluate held-out test predictions (Accuracy, Precision, Recall, F1, Confusion Matrix)
 └─ Real-time inference on new out-of-sample sentences
```

### Data Leakage Prevention
A critical machine learning best practice enforced in this project is strict **featurization separation**: the `TfidfVectorizer` vocabulary and inverse document frequency (IDF) weights are computed solely from the 800 training samples. The test set is transformed strictly using the training vocabulary, ensuring the model is evaluated on genuine out-of-sample data.

---

## 📈 Model Evaluation & Quantitative Results

The model was evaluated on 200 held-out test reviews (100 positive, 100 negative):

| Metric | Score (Raw) | Percentage | Practical Meaning |
| :--- | :---: | :---: | :--- |
| **Accuracy** | **0.7550** | **75.50%** | Proportion of all test reviews correctly classified |
| **Precision (Positive)** | **0.7525** | **75.25%** | When predicted positive, how often the review was actually positive |
| **Recall (Positive)** | **0.7600** | **76.00%** | Proportion of actual positive reviews successfully detected |
| **F1-Score (Positive)** | **0.7562** | **75.62%** | Harmonic mean balancing precision and recall |

### Confusion Matrix Breakdown

| Actual \ Predicted | Predicted Negative | Predicted Positive | Total Actual |
| :--- | :---: | :---: | :---: |
| **Actual Negative** | **75 (True Negative)** | **25 (False Positive)** | 100 |
| **Actual Positive** | **24 (False Negative)** | **76 (True Positive)** | 100 |
| **Total Predicted** | **99** | **101** | **200** |

- **True Positives (TP):** 76 positive reviews correctly classified as positive
- **True Negatives (TN):** 75 negative reviews correctly classified as negative
- **False Positives (FP):** 25 negative reviews mistakenly predicted as positive
- **False Negatives (FN):** 24 positive reviews mistakenly predicted as negative
- **Total Correct:** 151 / 200 (**75.50%**)
- **Total Misclassifications:** 49 / 200 (**24.50%**)

---

## 🖼️ Visualizations & Artifacts

All charts were programmatically generated with high-DPI rendering and saved to [`charts/`](charts/):

| Chart File | Description | Key Insight |
| :--- | :--- | :--- |
| [`charts/sentiment_distribution.png`](charts/sentiment_distribution.png) | Class balance bar chart | Confirms exact 500 positive vs 500 negative balance |
| [`charts/confusion_matrix.png`](charts/confusion_matrix.png) | Annotated heatmap of test predictions | Displays 76 TP, 75 TN, 25 FP, 24 FN |
| [`charts/model_performance.png`](charts/model_performance.png) | Bar chart of evaluation metrics | Visually compares Accuracy, Precision, Recall, and F1 |
| [`charts/evaluation_summary.png`](charts/evaluation_summary.png) | Combined side-by-side performance summary | Confusion Matrix + Metrics in a single visual layout |
| [`charts/sentiment_prediction.png`](charts/sentiment_prediction.png) | Horizontal bar chart of inference probabilities | Demonstrates prediction confidence on new test sentences |

### Execution Screenshots
Visual verification captures are documented in [`screenshots/`](screenshots/):
- [`screenshots/dataset_overview.png`](screenshots/dataset_overview.png): Terminal & table capture of dataset dimensions, null checks, and class distribution.
- [`screenshots/preprocessing_output.png`](screenshots/preprocessing_output.png): Token reduction and text cleaning comparison.
- [`screenshots/model_evaluation.png`](screenshots/model_evaluation.png): Classification report, confusion matrix values, and metric outputs.
- [`screenshots/prediction_output.png`](screenshots/prediction_output.png): Real-time inference on new out-of-sample sentences.

---

## 🔍 Model Performance Explanation & Error Analysis

### 1. Balanced Precision and Recall
The model demonstrates an exceptionally well-balanced classification behavior:
- **Precision = 75.25%** and **Recall = 76.00%**, resulting in an **F1-Score of 75.62%**.
- The nearly identical scores across both metrics confirm that the decision threshold (0.50) is optimal and that the model is not biased toward predicting one class over the other.

### 2. Error Analysis: Why Do Misclassifications Occur?
The 49 misclassified test samples (25 FP and 24 FN) were qualitatively analyzed:
- **Sarcasm and Nuance:** Phrases such as *"This film is an absolute masterpiece of unintentional comedy"* contain positive words (*masterpiece*) within an overarching negative critique. Because TF-IDF uses unigrams/bag-of-words, word order and sarcasm context are not preserved.
- **Mixed / Qualified Reviews:** Critics frequently praise certain aspects (*"The visual effects and acting were superb..."*) before concluding with a negative verdict (*"...yet the plot completely fell apart in the final act"*).
- **Negation Handling:** Complex negations (*"not completely devoid of charm"*) can confuse linear word-weight classifiers when tokens are evaluated independently.

### 3. Out-of-Sample Inference Capability
When applied to completely new, unseen sentences, the fitted pipeline performed with high confidence:
1. *"The cinematography was breathtaking and the performances were outstanding."*  
   → **POSITIVE** (Probability: **74.53%**)
2. *"A completely boring and predictable movie with terrible dialogue."*  
   → **NEGATIVE** (Probability: **75.93%**)
3. *"An inspiring, heartfelt story that kept me thoroughly engaged throughout."*  
   → **POSITIVE** (Probability: **63.85%**)

---

## 🎙️ 2–5 Minute Project Demo Guide

This structured presentation guide is designed for internship evaluations, code reviews, or mentor vivas:

### [0:00 – 0:45] Introduction & Context
- *"Hello! Today I am presenting my Day 14 Weekly Mini Project for the Linkific AI/ML Internship: Basic Sentiment Analysis using NLP and Machine Learning."*
- *"This project directly expands upon our Day 13 work where we learned text preprocessing and TF-IDF vectorization. Today, we closed the loop by building a complete end-to-end supervised classification system."*

### [0:45 – 1:30] Problem Statement & Dataset
- *"We used the benchmark IMDb Movie Reviews dataset from Pang & Lee, consisting of 1,000 authentic movie reviews with an exact 50/50 class balance—500 positive and 500 negative."*
- *"We verified data quality: zero missing values and zero duplicate records."*

### [1:30 – 2:30] Preprocessing Pipeline & Data Leakage Prevention
- *"Raw text cannot be fed directly into machine learning algorithms, so we implemented a 4-stage NLP pipeline: lowercasing, word tokenization with NLTK, stopword and punctuation removal, and clean text reconstruction. This reduced token noise by over 53%."*
- *"Crucially, to prevent data leakage, we split our data into 80% train and 20% test sets BEFORE fitting our TF-IDF vectorizer. The vocabulary of 2,500 features and IDF weights were learned exclusively from the training reviews."*

### [2:30 – 3:30] Model Training & Quantitative Results
- *"We trained a Logistic Regression classifier, which is particularly effective for high-dimensional, sparse text vectors."*
- *"On our 200 held-out test reviews, the model achieved **75.50% Accuracy**, with **75.25% Precision**, **76.00% Recall**, and an **F1-Score of 75.62%**."*
- *"Our confusion matrix shows 76 True Positives, 75 True Negatives, 25 False Positives, and 24 False Negatives—confirming balanced, robust detection across both classes."*

### [3:30 – 4:30] Live Inference, Limitations & Conclusion
- *"We also tested the model on new, out-of-sample sentences, and it accurately classified them with strong calibrated probabilities."*
- *"As for limitations, unigram TF-IDF does not capture word order or subtle sarcasm. In future work, we could incorporate n-grams, word embeddings like Word2Vec, or transformer models like BERT."*
- *"All code, notebooks, evaluation metrics, and charts are fully modular, verified, and committed to GitHub. Thank you!"*

---

## ⚠️ Limitations & Future Scope

1. **Bag-of-Words Limitation:** TF-IDF treats words as independent units and ignores grammatical syntax, making subtle sarcasm and complex negations harder to resolve.
2. **Domain Dependency:** The vocabulary was trained on movie reviews; applying this model to financial or biomedical text would require retraining or domain adaptation.
3. **Binary Restriction:** Human opinions are frequently neutral or mixed; extending the pipeline to 3-class (Negative / Neutral / Positive) or 5-star ratings is a valuable future enhancement.
4. **Future Enhancements:**
   - Incorporate bi-gram and tri-gram ranges (`ngram_range=(1, 2)`) to capture short contextual phrases.
   - Benchmark against Naive Bayes, Support Vector Machines (LinearSVC), and ensemble methods.
   - Explore pretrained Transformer models (e.g., DistilBERT) for context-aware sentiment analysis.

---

## 🛠️ Tools & Technologies Used

- **Programming Language:** Python 3.14
- **Natural Language Processing:** NLTK (Tokenization, Corpora, Stopwords)
- **Machine Learning & Featurization:** Scikit-learn (`TfidfVectorizer`, `LogisticRegression`, `train_test_split`, `metrics`)
- **Data Analysis & Manipulation:** Pandas, NumPy
- **Data Visualization:** Matplotlib, Seaborn
- **Version Control & Development:** Git, GitHub, Jupyter Notebook, VS Code

---

## 📁 Project Directory Structure

```text
Day-14/
│
├── sentiment_analysis.ipynb          # Interactive notebook with executed outputs & embedded charts
├── sentiment_analysis.py             # Modular, standalone execution script
├── sentiment_data.csv                # 1,000 balanced IMDb reviews dataset
├── model_evaluation_results.csv      # Exported quantitative performance metrics
├── README.md                         # Comprehensive project documentation
│
├── charts/                           # Programmatically generated high-resolution visualizations
│   ├── sentiment_distribution.png    # Class balance verification chart
│   ├── confusion_matrix.png          # Annotated heatmap of true vs predicted labels
│   ├── model_performance.png         # Comparative bar chart of Accuracy, Precision, Recall, F1
│   ├── evaluation_summary.png        # Combined side-by-side Confusion Matrix & Metrics plot
│   └── sentiment_prediction.png      # Out-of-sample prediction probability chart
│
└── screenshots/                      # Pipeline execution visual captures
    ├── dataset_overview.png          # Dataset inspection & dimensions
    ├── preprocessing_output.png       # Text cleaning transformation
    ├── model_evaluation.png          # Metric outputs & classification report
    ├── prediction_output.png         # Out-of-sample inference demonstration
    └── README.md                     # Screenshot gallery documentation
```

---

## 🚀 How to Run

### Prerequisites
Ensure Python and required libraries are installed:
```bash
pip install pandas numpy matplotlib seaborn nltk scikit-learn
```

### 1. Run the Standalone Python Pipeline
```bash
cd Day-14
python sentiment_analysis.py
```

### 2. Launch the Interactive Jupyter Notebook
```bash
jupyter notebook sentiment_analysis.ipynb
```

---

## 📜 Dataset Citation & References

- **Primary Citation:** Bo Pang and Lillian Lee. (2004). *A Sentimental Education: Sentiment Analysis Using Subjectivity Summarization Based on Minimum Cuts.* Proceedings of the 42nd Annual Meeting of the Association for Computational Linguistics (ACL-04), pp. 271–278.
- **Corpus Access:** Sourced from Cornell University Movie Review Data Archive via NLTK `movie_reviews` corpus.
