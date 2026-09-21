# Prototype Limitations & Future Improvements — Day 19

## 1. Current Prototype Limitations

In keeping with engineering rigor, this project is documented as an educational prototype. The following limitations are acknowledged:

1. **Synthetic Document Scope:**  
   The knowledge base contains four synthetic corporate policy documents (~13 KB total). It is designed to demonstrate stateful retrieval workflows rather than serve as a company-wide knowledge base.
2. **Heuristic Relevance Validation:**  
   Context validation uses a combined condition of chunk count, chunk length, and cosine similarity threshold ($0.45$). While effective for distinguishing relevant policy topics from out-of-domain queries, it is not an LLM-based factual entailment evaluator.
3. **Deterministic Extractive Synthesis:**  
   The deterministic extractive approach reduces the risk of unsupported generated content because the response is constructed from retrieved document chunks. However, it does not guarantee factual correctness or eliminate retrieval errors, while limiting conversational paraphrasing.
4. **Volatile In-Memory Checkpointing:**  
   `InMemorySaver` maintains thread checkpoints in Python process RAM. If the application restarts, session history is lost.
5. **Single-Process Execution:**  
   The current architecture runs synchronously in a single Python process without distributed worker queues or horizontal scaling.

---

## 2. Roadmap for Future Production Improvements

If transitioning this workflow into an enterprise production system, the following upgrades are recommended:

1. **Durable Persistence Tier:**  
   Replace `InMemorySaver` with `PostgresSaver` or `RedisSaver` backed by connection pooling to persist multi-turn sessions across server restarts.
2. **Hybrid Semantic & BM25 Search:**  
   Implement hybrid retrieval combining dense vector embeddings (`all-MiniLM-L6-v2`) with sparse keyword indexing (BM25 or Elasticsearch) for superior precision on specific acronyms and IDs.
3. **Agentic Generative Synthesis:**  
   Integrate a quantized local LLM (such as Llama 3 8B or Mistral 7B) or Gemini API with structured output schema validation for fluent, natural language answers.
4. **LLM-as-a-Judge Validation Node:**  
   Upgrade `validate_context` with a lightweight self-reflection agent (Self-RAG) that scores whether the retrieved context directly answers the user's specific intent before authorizing generation.
5. **Observability & Tracing:**  
   Export traces to OpenTelemetry or LangSmith for real-time latency monitoring, token consumption tracking, and automated failure alerting.

6. **Hugging Face Hub Telemetry & Offline Execution:**  
   During model initialization, `sentence-transformers` checks the Hugging Face Hub cache metadata over HTTPS, producing an unauthenticated warning if `HF_TOKEN` is not configured. Although model weights are cached locally and execute inference offline, initial lookup contacts HF Hub unless `HF_HUB_OFFLINE=1` is explicitly exported in the environment.
