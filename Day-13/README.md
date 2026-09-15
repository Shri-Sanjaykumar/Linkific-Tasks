# Day 13 — Natural Language Processing (NLP)

Linkific AI/ML Internship — Month 1 Training

---

## 1. Objective

Understand the fundamental principles of Natural Language Processing (NLP), implement a standard four-step text preprocessing pipeline (Lowercasing, Tokenization, Stopword Removal, and Text Reconstruction) on a domain-specific dataset, and transform unstructured textual data into a structured numerical feature matrix using Term Frequency-Inverse Document Frequency (TF-IDF) vectorization.

---

## 2. Dataset

- **Dataset Source:** Domain-specific corpus (`text_data.csv`)
- **Document Count:** 12 sentences covering Artificial Intelligence, Machine Learning, Data Science, and Programming.
- **Attributes:** `id`, `text`

---

## 3. NLP Preprocessing Workflow

```text
Original Text
    ↓
Lowercasing
    ↓
Tokenization
    ↓
Stopword Removal
    ↓
TF-IDF Vectorization
    ↓
Numerical Feature Matrix
    ↓
Term Analysis and Visualization
```

---

## 4. Preprocessing Methodology

1. **Lowercasing:** Normalizes all character casing across documents so that variations in capitalization (e.g., `"Machine"` and `"machine"`) map to identical vocabulary entries.
2. **Tokenization:** Segments continuous text strings into discrete syntactic units (tokens) using NLTK's `word_tokenize()`.
3. **Stopword Removal:** Eliminates high-frequency grammatical function words (such as `"is"`, `"the"`, `"and"`, `"for"`) using NLTK's English stopword corpus along with non-alphabetic filtering.
4. **Cleaned Text Reconstruction:** Reassembles the filtered tokens into space-delimited text strings suitable for vectorization.
5. **TF-IDF Vectorization:** Computes the composite product of Term Frequency (occurrence rate within a document) and Inverse Document Frequency (penalization for terms appearing across the entire corpus) via Scikit-learn's `TfidfVectorizer()`.

---

## 5. Results and Observations

| Metric | Measured Value |
| :--- | :--- |
| **Total Documents** | 12 sentences |
| **Original Word Tokens** | 118 tokens |
| **Tokens After Preprocessing** | 82 tokens |
| **Noise Reduction** | 30.5% (stopwords and punctuation filtered) |
| **Unique Vocabulary Size** | 63 terms |
| **TF-IDF Matrix Dimensions** | 12 rows × 63 columns |
| **Export File** | `tfidf_output.csv` |

### Top 10 Terms by Mean TF-IDF Score

| Rank | Term | Mean TF-IDF Score |
| :---: | :--- | :---: |
| 1 | `learning` | 0.1089 |
| 2 | `language` | 0.0981 |
| 3 | `data` | 0.0974 |
| 4 | `machine` | 0.0826 |
| 5 | `intelligence` | 0.0620 |
| 6 | `artificial` | 0.0620 |
| 7 | `models` | 0.0605 |
| 8 | `programming` | 0.0600 |
| 9 | `science` | 0.0600 |
| 10 | `natural` | 0.0548 |

---

## 6. Visualization

The top 10 terms with the highest mean TF-IDF scores across the corpus are plotted as a horizontal bar chart:

- **Top 10 TF-IDF Features:** [`charts/tfidf_visualization.png`](charts/tfidf_visualization.png)

---

## 7. Technical Insights

1. **Structured Numerical Representation:** Machine learning models require quantitative matrices; NLP text preprocessing standardizes unstructured text into a clean format suitable for mathematical modeling.
2. **Noise Reduction:** Removing non-informative stopwords and punctuation reduced the total token volume by 30.5%, preserving vocabulary with domain relevance.
3. **TF-IDF Weighting:** Unlike simple bag-of-words counts, TF-IDF reduces the impact of terms that appear ubiquitously while prioritizing domain-discriminative vocabulary.

---

## 8. Directory Files

- `nlp_practice.ipynb`: Interactive Jupyter notebook containing step-by-step preprocessing, TF-IDF vectorization, dynamic feature inspection, and embedded visualizations.
- `nlp_practice.py`: Standalone Python script executing the full pipeline, saving output matrices, and generating charts.
- `text_data.csv`: Domain text corpus containing 12 sentences.
- `tfidf_output.csv`: Exported 12 × 63 TF-IDF numerical feature matrix.
- `charts/tfidf_visualization.png`: Horizontal bar chart of top 10 TF-IDF terms.
- `README.md`: Technical documentation.
