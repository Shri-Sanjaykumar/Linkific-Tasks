# Day 15 — LLM and Hugging Face Model Comparison

Linkific AI/ML Internship — Month 1 Training  
Intern: Shri Sanjaykumar V  
Date: September 16, 2026  
Hugging Face Profile: [https://huggingface.co/Sanjay326](https://huggingface.co/Sanjay326) (Username: `Sanjay326`)  

---

## Overview

Day 15 marks the transition from classical supervised machine learning into Generative Artificial Intelligence and Large Language Models (LLMs). Building directly upon the NLP foundations from Day 13 and Day 14, this module explores the Hugging Face ecosystem, pretrained transformer models, and the `pipeline` API. We evaluate three distinct foundation models across text generation, sentiment classification, and document summarization.

---

## Learning Objectives

1. **Understand what Large Language Models are:** Gain a clear conceptual understanding of foundation models, transformer self-attention mechanisms, subword tokenization, and parameter scaling.
2. **Learn how modern AI applications use LLMs:** Understand how modern software integrates pretrained models through standardized inference pipelines to deliver real-world language processing capabilities without training models from scratch.
3. **Study AI Evolution:** Trace the transition from traditional programming through machine learning and deep learning to Generative AI and LLMs.
4. **Explore Hugging Face Ecosystem:** Set up an active Hugging Face profile, navigate the Model Hub, and inspect model cards.
5. **Comparative Model Evaluation:** Run local CPU inference on three distinct pretrained models and evaluate outputs using task-specific criteria.

---

## AI Evolution

Artificial Intelligence has progressed through five key development eras:

1. **Traditional Programming:** Human engineers manually code deterministic if-else rules and algorithms.
   $$\\text{Rules} + \\text{Data} \\longrightarrow \\text{Answers}$$
2. **Machine Learning:** Statistical algorithms infer mathematical patterns directly from labeled training data.
   $$\\text{Data} + \\text{Answers} \\longrightarrow \\text{Rules (Learned Model)}$$
3. **Deep Learning:** Multi-layered Artificial Neural Networks automatically extract hierarchical features from raw data (e.g., CNNs for computer vision, RNNs/LSTMs for sequential text).
4. **Generative AI:** Probability distribution modeling capable of synthesizing novel, realistic content (text, code, images, speech).
5. **Large Language Models:** LLMs are a major class of Generative AI systems focused on processing and generating natural language. They use transformer-based foundation architectures trained on internet-scale text corpora using self-supervised next-token prediction.

```text
Traditional Programming
        ↓
Machine Learning
        ↓
Deep Learning
        ↓
Generative AI
        ↓
Large Language Models
```

---

## What are LLMs?

- **Definition:** Deep neural networks built upon the Transformer architecture (Vaswani et al., 2017) trained on vast unstructured text corpora.
- **How LLMs Process Text:** Text is segmented into numerical tokens via a subword tokenizer (e.g., Byte-Pair Encoding or WordPiece), transformed into high-dimensional embedding vectors, and contextualized through multi-head self-attention layers.
- **High-Level Training:**
  - *Pretraining:* Self-supervised learning predicting the next token across billions of sentences to learn syntax, facts, and reasoning.
  - *Fine-Tuning / Alignment:* Supervised instruction tuning and reinforcement learning from human feedback (RLHF).
- **Tokens:** A token can represent a whole word, part of a word, a character, or punctuation, depending on the tokenizer.
- **Parameters:** Numerical weights and biases within the neural network that store learned linguistic patterns.
- **Inference Lifecycle:**
  $$\\text{Prompt} \\longrightarrow \\text{Tokenization} \\longrightarrow \\text{Model Forward Pass} \\longrightarrow \\text{Sampling / Decoding} \\longrightarrow \\text{Output}$$
- **Limitations:** Possible hallucinations, context-length limitations, training-data bias, dependence on input quality, and substantial computational/memory requirements.

---

## Hugging Face

- **Platform Overview:** Hugging Face is an open-source AI and machine learning platform providing pretrained models, datasets, libraries, and tools.
- **Model Hub:** A unified repository providing open access to state-of-the-art models across NLP, computer vision, audio, and multimodal tasks.
- **Pretrained Models:** Models whose weights have already been trained on massive datasets. Developers can download pretrained weights and use them for inference without training the model from scratch.
- **Model Cards:** Detailed documentation sheets provided with each model, outlining training methodology, intended domain, evaluation benchmarks, and known limitations.
- **Transformers Pipelines:** The `pipeline()` abstraction encapsulates tokenization, model loading, hardware dispatch, and output decoding into a clean, intuitive Python interface.
- **Intern Profile:** [https://huggingface.co/Sanjay326](https://huggingface.co/Sanjay326) (Username: `Sanjay326`).

---

## Models Used

For this project, three real pretrained models were selected and evaluated locally on CPU:

| Task | Model | Architecture | Parameters | Purpose |
| :--- | :--- | :--- | :---: | :--- |
| **Text Generation** | `distilbert/distilgpt2` | Autoregressive Decoder-only Transformer | 82M | Autoregressively continue open-ended prompts using a lightweight distilled GPT-2 model. |
| **Sentiment Analysis** | `distilbert/distilbert-base-uncased-finetuned-sst-2-english` | Bidirectional Encoder-only Transformer | 66M | A pretrained DistilBERT model fine-tuned on the Stanford Sentiment Treebank (SST-2) for binary sentiment classification. |
| **Summarization** | `t5-small` | Encoder-Decoder Sequence-to-Sequence | 60M | Condense multi-sentence text into an abstractive summary using a compact Text-to-Text Transfer Transformer. |

---

## Experiments

### 1. Text Generation
- **Input Prompt:**
  `"Artificial Intelligence is changing the way people work because"`
- **Model:** `distilbert/distilgpt2`
- **Settings:** `max_new_tokens=40`, `temperature=0.7`, `do_sample=True`
- **Output:**
  > *"Artificial Intelligence is changing the way people work because it's becoming so much more and more clear that real-world AI is not just a game. It's a real problem. Artificial intelligence is changing the way people work because it's becoming so much"*
- **Observation:** Generated a syntactically fluent continuation addressing the real-world nature of AI in workplaces, demonstrating autoregressive token-by-token prediction.

### 2. Sentiment Analysis
- **Input Text:**
  `"The movie had excellent performances and an engaging story."`
- **Model:** `distilbert/distilbert-base-uncased-finetuned-sst-2-english`
- **Prediction:** `POSITIVE`
- **Confidence Score:** `0.9999` (99.99%)
- **Observation:** The model predicted POSITIVE with a confidence score of 99.99%, indicating strong confidence in the positive class for this input. Contextual self-attention identified positive qualifying descriptors (*"excellent performances"*, *"engaging story"*) without manual feature engineering.

### 3. Text Summarization
- **Input Text:**
  `"Artificial Intelligence is increasingly being used in healthcare, finance, education, and software development. Machine Learning systems can analyze large datasets and identify patterns that are difficult to detect manually. Generative AI has also introduced systems that can create text, images, and other forms of content."`
- **Model:** `t5-small`
- **Settings:** `max_length=60`, `min_length=20`, `do_sample=False`
- **Output:**
  > *"artificial intelligence is increasingly being used in healthcare, finance, education, and software development. machine learning systems can analyze large datasets and identify patterns that are difficult to detect manually."*
- **Observation:** The summary retained the main ideas from the original text in a shorter form, compressing the 45-word input into 29 words (35.6% word count reduction).

---

## Model Comparison

The three tested models represent fundamentally different architectural families, operational objectives, and computational profiles within natural language processing:

### Detailed Technical Comparison Matrix

| Dimension | Text Generation | Sentiment Analysis | Text Summarization |
| :--- | :--- | :--- | :--- |
| **Model Name** | `distilbert/distilgpt2` | `distilbert-base-uncased-finetuned-sst-2-english` | `t5-small` |
| **Task Category** | Open-Ended Text Generation | Sequence Classification | Abstractive Sequence-to-Sequence |
| **Transformer Family** | Decoder-only | Encoder-only | Encoder-Decoder |
| **Attention Mechanism** | Causal (Masked) Self-Attention | Bidirectional Self-Attention | Bidirectional Encoder + Causal Decoder + Cross-Attention |
| **Parameter Count** | 82 Million | 66 Million | 60 Million |
| **Model Weights File** | `model.safetensors` (336.5 MB) | `model.safetensors` (255.4 MB) | `model.safetensors` (230.8 MB) |
| **Tokenization Algorithm** | Byte-Pair Encoding (BPE) | WordPiece (with `[CLS]`, `[SEP]`) | SentencePiece (Unigram) |
| **Vocabulary Size** | 50,257 tokens | 30,522 tokens | 32,128 tokens |
| **Pretraining Objective** | Autoregressive Next-Token Prediction | Masked Language Modeling (MLM) | Span Corruption / Denoising |
| **Fine-Tuning Domain** | General WebText | Stanford Sentiment Treebank (SST-2) | Multi-task supervised mixture (C4, CNN/DM) |
| **Input Structure** | Prompt text string (10 words) | Sentence review (9 words) | Prefixed string (`"summarize: ..."`, 45 words) |
| **Output Structure** | Text continuation (40 new tokens) | Class label (`POSITIVE`) + Confidence (`0.9999`) | Condensed abstractive summary (29 words) |
| **CPU Inference Pattern** | Iterative autoregressive loop (40 passes) | Single forward pass (1 pass) | Encoder pass + Beam Search decoding (4 beams) |
| **Observed Output Quality** | Topical and fluent continuation | Decisive positive classification (99.99%) | Informative summary with 35.6% length reduction |

### Architectural Paradigm & Information Flow
- **Decoder-only Transformer (`distilgpt2`):** Uses causal self-attention where each token can only attend to previous tokens ($t' \le t$). This strict triangular attention mask prevents lookahead leakage, making it suited for step-by-step next-token prediction. However, because it lacks bidirectional context, it cannot incorporate subsequent words when interpreting earlier tokens.
- **Encoder-only Transformer (`distilbert-sst2`):** Uses unmasked bidirectional self-attention where every token attends to all other tokens simultaneously. This allows the model to build contextual representations of each word influenced by both preceding and succeeding text. The final hidden state of the first token (`[CLS]`) serves as a pooled representation passed into a linear classification layer with Softmax to produce class probabilities.
- **Encoder-Decoder Transformer (`t5-small`):** Decouples sequence understanding from sequence generation. The bidirectional encoder reads the complete input paragraph to produce contextual representations. The causal decoder then autoregressively generates the summary, attending to previously generated summary tokens via self-attention and querying the encoder representations via cross-attention.

### Tokenization Strategies & Input Preprocessing
- **BPE (`distilgpt2`):** Segments text into subwords based on frequency; does not use explicit prefix tokens.
- **WordPiece (`distilbert-sst2`):** Prepends `[CLS]` (classification token) and appends `[SEP]` (separator token) to frame the input sequence.
- **SentencePiece with Task Prefix (`t5-small`):** Operates under a unified "text-to-text" framework where the task type is explicitly prompted in the input text (`"summarize: ..."`), allowing a single network to perform varied NLP tasks without changing architecture.

### Computational Profile & Latency on CPU
- **Sentiment Analysis (`distilbert-sst2`):** Fastest inference (< 100ms on CPU). A single forward pass through 6 layers immediately outputs classification logits.
- **Text Generation (`distilgpt2`):** Moderate latency (~1–3s on CPU). Requires 40 consecutive forward passes, generating one token per forward pass using sampling at temperature 0.7.
- **Text Summarization (`t5-small`):** Highest computational workload (~2–4s on CPU). Runs the encoder once, then executes Beam Search across 4 parallel candidate beams until the end-of-sequence token `</s>` is reached.

---

## Best Output for Chosen Input

Since the three models perform different NLP tasks, they are not directly comparable using a single numerical performance score.

The outputs were therefore evaluated using task-specific criteria:

1. Text Generation:
   Relevance, coherence, and natural continuation of the prompt.

2. Sentiment Analysis:
   Predicted sentiment label and model confidence.

3. Text Summarization:
   Relevance, conciseness, and preservation of the main information.

For the selected inputs, all three models produced usable task-specific outputs. The sentiment model produced a highly confident POSITIVE prediction for the selected review, while the summarization model produced a concise summary and the text-generation model produced a relevant continuation.

Therefore, no universal "best model" is declared because each model is designed for a different task.

---

## Key Learnings

1. **Pretrained Foundation Models:** Complex NLP capabilities can be achieved without collecting massive datasets or training neural networks from scratch.
2. **Architecture Matters:** Different transformer configurations (Encoder-only vs. Decoder-only vs. Encoder-Decoder) are suited to different NLP tasks.
3. **Prompt Conditioning:** Model outputs are directly influenced by prompt phrasing, temperature settings, and generation parameters.
4. **Critical Output Verification:** Language models are prone to hallucination and repetition; programmatic constraints and human review are essential.
5. **Operational Tradeoffs:** Model parameter size, latency on CPU environments, and memory consumption must be evaluated before deployment.

---

## Limitations

- **Evaluation Scope:** The project evaluates individual outputs using task-specific qualitative criteria rather than a common benchmark dataset.
- **Single Model per Task:** Explored one representative model per task without cross-model benchmark evaluation against larger architectures (e.g., LLaMA, RoBERTa, BART-large).
- **Small Test Inputs:** Evaluated on specific test prompts rather than comprehensive evaluation benchmark suites (e.g., GLUE, SuperGLUE).
- **Sampling Variability:** Text generation results vary across runs due to stochastic sampling parameters (`temperature`, `top_k`).
- **Pretraining Biases:** Foundation models reflect biases inherent in their web-scraped pretraining corpora.

---

## Project Structure

```text
Day-15/
│
├── llm_model_comparison.ipynb        # Fully executed interactive notebook
├── llm_model_comparison.py           # Standalone reproducible execution script
├── README.md                         # Comprehensive technical documentation
│
├── outputs/                          # Saved genuine model outputs
│   ├── text_generation_output.txt    # Continuation generated by distilgpt2
│   ├── sentiment_output.txt          # Classification & confidence by DistilBERT
│   └── summarization_output.txt      # Abstractive summary produced by T5-small
│
└── screenshots/                      # Visual execution evidence
    ├── text_generation.png           # Visual capture of text generation experiment
    ├── sentiment_analysis.png        # Visual capture of sentiment analysis experiment
    ├── summarization.png             # Visual capture of summarization experiment
    └── README.md                     # Screenshot gallery & manual evidence guide
```

---

## How to Run

### Prerequisites
Install required dependencies:
```bash
pip install transformers torch sentencepiece nltk
```

### 1. Run the Python Script
```bash
cd Day-15
python llm_model_comparison.py
```

### 2. Launch the Jupyter Notebook
```bash
jupyter notebook llm_model_comparison.ipynb
```
Select the Python 3 kernel and run all cells sequentially.

---

## References

- [Hugging Face Transformers Documentation](https://huggingface.co/docs/transformers)
- [Hugging Face Model Hub](https://huggingface.co/models)
- [distilbert/distilgpt2 Model Card](https://huggingface.co/distilbert/distilgpt2)
- [distilbert-base-uncased-finetuned-sst-2-english Model Card](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)
- [t5-small Model Card](https://huggingface.co/t5-small)
- Vaswani et al. (2017). *Attention Is All You Need.* Advances in Neural Information Processing Systems (NeurIPS).
