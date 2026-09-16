"""
Day 15 — Introduction to Large Language Models and Hugging Face
Linkific AI/ML Internship — Month 1 Training

Tasks Covered:
1. Text Generation with a lightweight GPT-2 model (distilbert/distilgpt2)
2. Sentiment Analysis with DistilBERT (distilbert/distilbert-base-uncased-finetuned-sst-2-english)
3. Text Summarization with T5-small (t5-small)
4. Model output logging and exporting to the outputs/ directory
"""

import os
import sys
import warnings

# Suppress verbose warnings for clean CLI output
warnings.filterwarnings("ignore")
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM


def run_text_generation(prompt, model_name="distilbert/distilgpt2"):
    """
    Generate text continuation from an input prompt using a lightweight GPT-2 model.
    """
    print(f"Task:         Text Generation")
    print(f"Model:        {model_name}")
    print(f"Input Prompt: \"{prompt}\"")
    print("Running inference...")

    generator = pipeline("text-generation", model=model_name)
    result = generator(
        prompt,
        max_new_tokens=40,
        do_sample=True,
        temperature=0.7,
        pad_token_id=50256
    )
    generated_text = result[0]["generated_text"].strip()
    return generated_text


def run_sentiment_analysis(text, model_name="distilbert/distilbert-base-uncased-finetuned-sst-2-english"):
    """
    Classify emotional sentiment and predict confidence score using DistilBERT.
    """
    print(f"Task:         Sentiment Analysis")
    print(f"Model:        {model_name}")
    print(f"Input Text:   \"{text}\"")
    print("Running inference...")

    classifier = pipeline("sentiment-analysis", model=model_name)
    result = classifier(text)[0]
    label = result["label"]
    score = float(result["score"])
    return label, score


def run_summarization(text, model_name="t5-small"):
    """
    Condense a paragraph into a concise summary using the T5-small sequence-to-sequence model.
    Supports both pipeline and AutoModelForSeq2SeqLM for cross-version compatibility.
    """
    print(f"Task:         Text Summarization")
    print(f"Model:        {model_name}")
    print(f"Input Text:   \"{text}\"")
    print("Running inference...")

    try:
        summarizer = pipeline("summarization", model=model_name)
        result = summarizer(text, max_length=60, min_length=20, do_sample=False)[0]["summary_text"]
        return result.strip()
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(
            inputs,
            max_length=60,
            min_length=20,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True
        )
        return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


def main():
    print("=" * 75)
    print("DAY 15 — INTRODUCTION TO LARGE LANGUAGE MODELS AND HUGGING FACE")
    print("Linkific AI/ML Internship — Month 1 Training")
    print("=" * 75)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(base_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. Text Generation Experiment
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("EXPERIMENT 1: TEXT GENERATION")
    print("-" * 75)
    gen_model = "distilbert/distilgpt2"
    gen_prompt = "Artificial Intelligence is changing the way people work because"
    
    generated_text = run_text_generation(gen_prompt, model_name=gen_model)
    print(f"\nGenerated Output:\n{generated_text}")

    gen_out_file = os.path.join(outputs_dir, "text_generation_output.txt")
    with open(gen_out_file, "w", encoding="utf-8") as f:
        f.write(f"Task: Text Generation\n")
        f.write(f"Model: {gen_model}\n")
        f.write(f"Input Prompt: {gen_prompt}\n")
        f.write(f"Generation Settings: max_new_tokens=40, temperature=0.7, do_sample=True, pad_token_id=50256\n\n")
        f.write(f"Generated Output:\n{generated_text}\n")
    print(f"Saved: {gen_out_file}")

    # -------------------------------------------------------------
    # 2. Sentiment Analysis Experiment
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("EXPERIMENT 2: SENTIMENT ANALYSIS")
    print("-" * 75)
    sent_model = "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
    sent_input = "The movie had excellent performances and an engaging story."

    sent_label, sent_score = run_sentiment_analysis(sent_input, model_name=sent_model)
    print(f"\nPredicted Label:  {sent_label}")
    print(f"Confidence Score: {sent_score:.4f} ({sent_score * 100:.2f}%)")

    sent_out_file = os.path.join(outputs_dir, "sentiment_output.txt")
    with open(sent_out_file, "w", encoding="utf-8") as f:
        f.write(f"Task: Sentiment Analysis\n")
        f.write(f"Model: {sent_model}\n")
        f.write(f"Input Text: {sent_input}\n\n")
        f.write(f"Predicted Label: {sent_label}\n")
        f.write(f"Confidence Score: {sent_score:.4f} ({sent_score * 100:.2f}%)\n")
    print(f"Saved: {sent_out_file}")

    # -------------------------------------------------------------
    # 3. Text Summarization Experiment
    # -------------------------------------------------------------
    print("\n" + "-" * 75)
    print("EXPERIMENT 3: TEXT SUMMARIZATION")
    print("-" * 75)
    summ_model = "t5-small"
    summ_input = (
        "Artificial Intelligence is increasingly being used in healthcare, finance, "
        "education, and software development. Machine Learning systems can analyze "
        "large datasets and identify patterns that are difficult to detect manually. "
        "Generative AI has also introduced systems that can create text, images, and other forms of content."
    )

    summary_text = run_summarization(summ_input, model_name=summ_model)
    print(f"\nGenerated Summary:\n{summary_text}")

    summ_out_file = os.path.join(outputs_dir, "summarization_output.txt")
    with open(summ_out_file, "w", encoding="utf-8") as f:
        f.write(f"Task: Text Summarization\n")
        f.write(f"Model: {summ_model}\n")
        f.write(f"Input Text: {summ_input}\n")
        f.write(f"Settings: max_length=60, min_length=20, do_sample=False\n\n")
        f.write(f"Generated Summary:\n{summary_text}\n")
    print(f"Saved: {summ_out_file}")

    # -------------------------------------------------------------
    # 4. Model Comparison Table
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 75)
    print(f"{'Task':<22} | {'Model':<28} | {'Output Summary':<25}")
    print("-" * 75)
    print(f"{'Text Generation':<22} | {gen_model:<28} | {'Fluent continuation':<25}")
    print(f"{'Sentiment Analysis':<22} | {sent_model:<28} | {f'{sent_label} ({sent_score*100:.2f}%)':<25}")
    print(f"{'Summarization':<22} | {summ_model:<28} | {'Concise 2-sentence summary':<25}")
    print("=" * 75)
    print("All 3 models executed successfully and outputs exported to outputs/ directory.")


if __name__ == "__main__":
    main()
