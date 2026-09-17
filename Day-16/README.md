# Day 16 — Basic Retrieval-Augmented Generation (RAG)

**Linkific AI/ML Internship — Month 1 Training**  
**Intern:** Shri Sanjaykumar V  
**Role:** AI/ML Intern  
**Organization:** Linkific  
**Date:** 17 September 2026  

---

## Objective

The objective of Day 16 is to construct an end-to-end **Retrieval-Augmented Generation (RAG)** pipeline that connects organizational demonstration documentation to a language model. The pipeline dynamically processes user queries, executes dense vector similarity search over chunked document embeddings, retrieves top relevant context, and generates context-grounded answers. In addition, we empirically evaluate three chunk sizes (200, 400, and 800 characters) across five benchmark questions to **identify the best-performing chunk-size configuration for the selected demonstration dataset and evaluation questions**.

---

## Learning Objectives

1. **Embeddings:** Understand how transformer-based embedding models map raw text into continuous, high-dimensional vector spaces that capture semantic meaning.
2. **Vector Databases:** Study the storage, indexing, and retrieval mechanics of vector databases for nearest-neighbor similarity search.
3. **ChromaDB:** Implement an open-source vector store to manage document chunks, embeddings, and metadata collections.
4. **FAISS:** Implement Meta's Facebook AI Similarity Search (FAISS) library as a high-performance vector retrieval engine.
5. **Semantic Search:** Differentiate keyword-based lexical search from embedding-based semantic retrieval.
6. **RAG Pipeline:** Integrate document chunking, dense vector retrieval, and local sequence-to-sequence answer generation.
7. **Chunk Size Experimentation:** Empirically evaluate the impact of different document chunk sizes (200, 400, and 800 characters) on retrieval precision and answer completeness to **identify the best-performing chunk-size configuration for the selected demonstration dataset and evaluation questions**.

---

## Technologies Used

- **Programming Language:** Python 3.13
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors)
- **Primary Vector Database:** ChromaDB 1.5.9
- **Vector Search Library:** FAISS (faiss-cpu 1.15.1, `IndexFlatIP`)
- **Language Model / Generator:** Hugging Face `t5-small` (60M parameter sequence-to-sequence transformer)
- **Deep Learning Framework:** PyTorch 2.13.0+cpu, Hugging Face Transformers 5.17.0
- **Data Analysis & Visualization:** Pandas 3.0.1, NumPy 2.4.3, Matplotlib 3.10.8
- **Version Control:** Git & GitHub

---

## Dataset / Documents

> **Confidentiality Notice:** To strictly uphold organizational data security and confidentiality, no real proprietary Linkific documents, internal source code, credentials, or private URLs are used. 

The demonstration knowledge base consists of **five synthetic company documents** (~10,657 characters, 1,345 words) created specifically for RAG evaluation:

| File Name | Primary Topic Covered | Characters | Words | Lines |
| :--- | :--- | :---: | :---: | :---: |
| `onboarding.txt` | Orientation schedule, workstation setup (Python, VS Code, Git), mentor assignment, and onboarding checklist. | 2,128 | 262 | 21 |
| `leave_policy.txt` | Standard hours (9:30 AM–6:30 PM), 85% attendance rule, 24-hour advance leave notice to mentor/HR (Rebecca Mam), medical procedures. | 1,905 | 256 | 16 |
| `training_guidelines.txt` | 4-week training curriculum, daily schedule (10:00 AM task brief, 7:00 PM review), and PEP 8 code quality standards. | 2,286 | 288 | 19 |
| `project_workflow.txt` | 5-stage project lifecycle (Requirements → Data → Model → Evaluation → Delivery), pre-submission checklist, and code review. | 2,102 | 259 | 23 |
| `submission_guidelines.txt` | Daily 6:00 PM deadline, required deliverables (.ipynb, .py, README, outputs, screenshots), Git sync, and tracker sheet logging. | 2,236 | 280 | 24 |

---

## RAG Architecture

```text
  [ Raw Company Documents (5 Text Files) ]
                    │
                    ▼
  [ Document Chunking (200 / 400 / 800 chars) ]
                    │
                    ▼
  [ Embedding Generation (all-MiniLM-L6-v2, 384-dim) ]
                    │
                    ▼
  [ Vector Indexing (ChromaDB Collection / FAISS Index) ]
                    │
        User Query ──┴──► [ Semantic Search / Vector Similarity ]
                                    │
                                    ▼
                      [ Top-K Retrieved Context Chunks ]
                                    │
                                    ▼
            [ Prompt Construction: Context + Question ]
                                    │
                                    ▼
                    [ Language Model (T5 Seq2Seq LM) ]
                                    │
                                    ▼
                     [ Context-Grounded Final Answer ]
```

**RAG provides retrieved source context to the language model, which can help ground responses in the available documentation.**

---

## Implementation Steps

1. **Document Ingestion:** Loaded 5 demonstration text documents dynamically and extracted structural metadata.
2. **Chunking & Overlap:** Implemented character-based sliding-window chunking across three test configurations:
   - Chunk Size 200 (overlap 50 chars) → 71 chunks
   - Chunk Size 400 (overlap 50 chars) → 32 chunks
   - Chunk Size 800 (overlap 100 chars) → 17 chunks
3. **Dense Vectorization:** Converted text chunks into normalized 384-dimensional dense vectors using `sentence-transformers/all-MiniLM-L6-v2`.
4. **Vector Database Storage:** Populated three separate ChromaDB collections (`rag_chunks_200`, `rag_chunks_400`, `rag_chunks_800`) with chunk text, embeddings, and document source metadata.
5. **FAISS Integration:** Implemented FAISS `IndexFlatIP` (Cosine Similarity) to demonstrate raw vector indexing alongside ChromaDB.
6. **Semantic Querying:** Executed semantic retrieval on five benchmark questions using both distance-based (ChromaDB) and inner-product (FAISS) metrics.
7. **Context-Grounded Answer Generation:** Formatted retrieved passages into structured prompts and passed them to `t5-small` to generate factual answers.
8. **Empirical Evaluation:** Evaluated all combinations across Relevance, Correctness against source, Completeness, and Context Grounding using a transparent, deterministic rule-based rubric.

---

## Embeddings

An **embedding** is a dense continuous vector representation where semantic relationships correspond to geometric proximity in vector space.

- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Dimensionality:** 384 dimensions
- **Semantic Distance Verification:**
  - *"Interns must submit daily project code by 6:00 PM."* vs *"The task submission deadline is 18:00 every evening."* → Cosine Similarity: **0.8412** (High semantic proximity)
  - *"Interns must submit daily project code by 6:00 PM."* vs *"Pizza recipe includes tomato sauce and mozzarella cheese."* → Cosine Similarity: **0.0521** (Orthogonal / Unrelated)

---

## ChromaDB

**ChromaDB** serves as the primary vector store for this project:
- Stores text content, embeddings, unique IDs, and metadata dictionaries in unified collections.
- Enables filtering by source document (e.g., `{"source": "leave_policy.txt"}`).
- Performs Approximate Nearest Neighbor (ANN) search via HNSW indexing.
- Three collections were created: `rag_chunks_200`, `rag_chunks_400`, and `rag_chunks_800`.

---

## FAISS

**FAISS (Facebook AI Similarity Search)** was implemented as an alternative high-performance retrieval library:
- Employs `faiss.IndexFlatIP` on L2-normalized embeddings to compute exact Cosine Similarity.
- Verified that top retrieved chunks in FAISS matched ChromaDB results for identical queries (e.g., Question 1 top source: `submission_guidelines.txt` with cosine similarity `0.5709`).

### ChromaDB vs FAISS Educational Comparison:

| Feature | ChromaDB | FAISS |
| :--- | :--- | :--- |
| **Primary Purpose** | Full Vector Database & Document Store | Low-Level Similarity Search Library |
| **Metadata Support** | Native (stores text strings, IDs, dicts) | Requires separate application-level mapping |
| **Persistence** | Built-in SQLite / DuckDB backend | Manual binary serialization (`write_index`) |
| **Ease of Use** | High (few lines of Python) | Medium (requires vector matrix conversions) |
| **Target Scale** | Prototyping, small-to-medium production apps | High-throughput, multi-million vector search |

---

## Semantic Search

### Lexical (Keyword) Search vs Semantic Search:
- **Lexical Search (BM25 / TF-IDF):** Requires exact or stemmed word token overlap. Searching for *"rules when intern is absent"* would miss passages containing *"leave request protocol"*.
- **Semantic Search (Dense Vector):** Compares meaning in 384-dimensional embedding space. Correctly routes *"rules when intern is absent"* to `leave_policy.txt` with distance `0.3703`.

---

## LLM / Answer Generation

Answer generation is handled by `t5-small` via Hugging Face `AutoModelForSeq2SeqLM`, operating locally on CPU:
- **Prompt Structure:**
  ```text
  question: {user_query} context: {retrieved_chunks}
  ```
- **Context Grounding:** The model generates answers using the retrieved context provided in the prompt. When information is omitted from retrieved text, fallback rules return: *"Information not specified in the provided documentation."*

---

## Rule-Based Evaluation Rubric Derived from Known Facts in the Synthetic Corpus

To evaluate retrieval and generation performance objectively on this training demonstration dataset without arbitrary scoring, we employ a rule-based evaluation rubric derived from known facts in the synthetic demonstration corpus:
- **Relevance (1.0 to 5.0):** Compares query intent keywords with retrieved context and verifies retrieval of the primary authority document.
- **Correctness against source (1.0 to 5.0):** Validates generated answer facts against known ground truth statements from the demonstration documents.
- **Completeness (1.0 to 5.0):** Measures the proportion of expected procedural facts captured by the retrieved context.
- **Context Grounding (1.0 to 5.0):** Verifies the percentage of answer content words derived directly from retrieved context.
- **Overall Score (1.0 to 5.0):** Arithmetic mean of the four dimensions.

---

## Benchmark Response Evaluation Table

Empirical evaluation results across all 5 questions and 3 chunk sizes:

| Question | Chunk Size | Top Document | Generated Answer | Relevance | Correctness | Completeness | Grounding | Overall Score |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| What is the process for submitting an internship task? | 200 | `submission_guidelines.txt` | 6:00 PM IST | 4.44 | 5.00 | 3.00 | 5.00 | **4.36** |
| What happens when an intern takes leave? | 200 | `leave_policy.txt` | they remain responsible for completing all missed technical modules | 3.33 | 5.00 | 3.00 | 5.00 | **4.08** |
| What are the main steps in the training workflow? | 200 | `project_workflow.txt` | handle missing values, remove noise, and perform exploratory sanity checks | 3.12 | 5.00 | 2.60 | 5.00 | **3.93** |
| What should an intern complete before submitting a project? | 200 | `submission_guidelines.txt` | validation steps | 2.89 | 3.50 | 2.60 | 5.00 | **3.50** |
| What are the basic onboarding requirements? | 200 | `onboarding.txt` | Python (version 3.10 or higher), Visual Studio Code | 4.06 | 5.00 | 3.40 | 5.00 | **4.37** |
| What is the process for submitting an internship task? | 400 | `submission_guidelines.txt` | task verification | 3.61 | 3.50 | 4.00 | 5.00 | **4.03** |
| What happens when an intern takes leave? | 400 | `leave_policy.txt` | they remain responsible for completing all missed technical modules | 4.44 | 5.00 | 5.00 | 5.00 | **4.86** |
| What are the main steps in the training workflow? | 400 | `project_workflow.txt` | Implement baseline models, engineer relevant features, and optimize model parameters | 3.44 | 5.00 | 4.20 | 5.00 | **4.41** |
| What should an intern complete before submitting a project? | 400 | `project_workflow.txt` | the following validation steps | 4.72 | 3.50 | 4.20 | 5.00 | **4.35** |
| What are the basic onboarding requirements? | 400 | `onboarding.txt` | introductory Python and environment verification test. - Review and acknowledge company information confidentiality and data security rules | 4.06 | 5.00 | 5.00 | 5.00 | **4.76** |
| What is the process for submitting an internship task? | 800 | `submission_guidelines.txt` | Daily Submission Deadline | 4.72 | 5.00 | 4.00 | 5.00 | **4.68** |
| What happens when an intern takes leave? | 800 | `leave_policy.txt` | they remain responsible for completing all missed technical modules | 4.44 | 5.00 | 5.00 | 5.00 | **4.86** |
| What are the main steps in the training workflow? | 800 | `project_workflow.txt` | Implement baseline models, engineer relevant features, and optimize model parameters | 3.75 | 5.00 | 4.20 | 5.00 | **4.49** |
| What should an intern complete before submitting a project? | 800 | `project_workflow.txt` | validation steps | 4.72 | 3.50 | 4.20 | 5.00 | **4.35** |
| What are the basic onboarding requirements? | 800 | `onboarding.txt` | - Submit digital identity and internship acceptance verification | 4.06 | 5.00 | 5.00 | 5.00 | **4.76** |

---

## Aggregated Chunk Size Performance Comparison

| Chunk Size | Total Chunks | Overlap | Average Relevance | Average Correctness | Average Completeness | Average Grounding | Average Overall Score |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **200 chars** | 71 chunks | 50 chars | 3.57 | 4.70 | 2.92 | 5.00 | **4.05** |
| **400 chars** | 32 chunks | 50 chars | 4.05 | 4.40 | 4.48 | 5.00 | **4.48** |
| **800 chars** | 17 chunks | 100 chars | **4.34** | **4.70** | **4.48** | **5.00** | **4.63 (Best)** |

---

## Best-Performing Chunk Size

### Winner: **Chunk Size 800 Characters** (Average Overall Score: **4.63 / 5.00**)

### Empirical Findings:
1. **Chunk Size 200 (Overall: 4.05, Completeness: 2.92):**  
   A 200-character window holds only ~25–35 words. Procedural policies (such as multi-stage training workflows or onboarding checklists) span several sentences. Slicing at 200 characters split sentences mid-procedure, causing the lowest completeness score (**2.92**).
2. **Chunk Size 400 (Overall: 4.48, Completeness: 4.48):**  
   A 400-character window corresponds to ~55–80 words, roughly the length of an individual operational policy clause. It significantly improved completeness over 200 characters while maintaining strong query alignment.
3. **Chunk Size 800 (Overall: 4.63, Relevance: 4.34, Completeness: 4.48):**  
   An 800-character window encompasses ~120–160 words. In this demonstration corpus, 800 characters provided sufficient context window to preserve complete multi-step instructions and achieved the highest relevance (**4.34**) without truncating necessary guidelines.

---

## Limitations

- **Demonstration Data:** Relies on a synthetic demonstration corpus (~10.6K characters) to maintain confidentiality.
- **Fixed-Character Windows:** Character slicing does not respect natural Markdown headers or semantic section boundaries.
- **Local Model Capacity:** `t5-small` generates concise, extractive-like answers; larger models (Flan-T5, LLaMA-3) would generate richer, multi-sentence syntheses.
- **Single-Turn Context:** The pipeline evaluates independent single-turn queries without conversational chat history.

---

## Key Learnings

1. **Pretrained Models Accelerate Development:** Pretrained models reduce the need to train a model from scratch and can accelerate prototyping and development.
2. **Context-Grounding Improves Factual Alignment:** In this experiment, providing explicit retrieved context helped keep the generated responses aligned with the demonstration documentation, illustrating the value of RAG for domain-specific question answering.
3. **Chunk Size Directly Dictates Performance:** Chunking is not an arbitrary parameter; selecting an optimal chunk size is critical to balancing granular retrieval with context completeness.
4. **Embeddings Standardize Search:** Dense vectors overcome vocabulary mismatch between user questions and official documentation.
5. **Vector Stores Simplify Metadata:** Storing source file names alongside vectors enables immediate citation and transparency.

---

## Project Structure

```text
Day-16/
│
├── rag_pipeline.ipynb                 # Fully executed 20-section interactive notebook
├── rag_pipeline.py                    # Standalone reproducible execution script
├── README.md                          # Comprehensive technical project documentation
│
├── documents/                         # Synthetic demonstration company documentation
│   ├── onboarding.txt                 # Workstation setup & orientation guide
│   ├── leave_policy.txt               # Working hours & attendance procedures
│   ├── training_guidelines.txt        # 4-week curriculum & review schedule
│   ├── project_workflow.txt           # 5-stage project development lifecycle
│   └── submission_guidelines.txt      # Daily submission deadlines & deliverables
│
├── outputs/                           # Exported experimental outputs
│   ├── retrieval_results/
│   │   ├── retrieval_chunk200.json    # Retrieved context for 200-char chunks
│   │   ├── retrieval_chunk400.json    # Retrieved context for 400-char chunks
│   │   └── retrieval_chunk800.json    # Retrieved context for 800-char chunks
│   ├── response_comparison/
│   │   └── response_comparison.csv    # Full response comparison across questions
│   └── evaluation_results/
│       ├── evaluation_results.json    # Granular scoring metrics
│       └── chunk_size_summary.txt     # Formatted empirical results summary
│
└── screenshots/                       # Visual execution evidence
    ├── rag_workflow_architecture.png  # End-to-end RAG architecture diagram
    ├── chunk_size_comparison.png      # Score comparison across chunk sizes
    ├── retrieval_results_sample.png   # Chunks generated per size configuration
    ├── response_evaluation_table.png  # Complete evaluation matrix
    └── README.md                      # Screenshot gallery and documentation
```

---

## How to Run

### Prerequisites
Install dependencies:
```bash
pip install sentence-transformers chromadb faiss-cpu transformers torch pandas numpy matplotlib
```

### 1. Run the Python Standalone Script
```bash
cd Day-16
python rag_pipeline.py
```

### 2. Launch the Jupyter Notebook
```bash
jupyter notebook rag_pipeline.ipynb
```
Run all cells sequentially. All 13 code cells will execute with **0 errors**.

---

## Conclusion

For this demonstration dataset and evaluation set, the **800-character chunk size** provided the best observed balance between retrieval relevance and response completeness.
