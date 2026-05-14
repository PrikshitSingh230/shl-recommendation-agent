# 🤖 SHL Assessment Recommendation Agent

A retrieval first conversational recommendation system that suggests relevant SHL assessments based on hiring needs, job roles, skills, and recruiter style conversations.

The project was designed with a strong focus on retrieval quality rather than relying on a very large language model. The core idea was that if retrieval is strong enough, even a smaller and faster LLM can generate grounded and useful recommendations.

The system supports:
- Role based assessment recommendations
- Conversational refinement
- Clarification handling for vague hiring requests
- Hybrid semantic and keyword retrieval
- Hallucination resistant URL validation
- Multi turn recruiter style interactions
---

# Example Queries

The assistant supports queries such as:

```text
Hiring Java backend developers with Spring Boot experience
```

```text
Need assessments for entry level customer support hiring
```

```text
Add personality assessments for leadership screening
```

```text
Compare cognitive and personality tests for sales hiring
```

---

# Response Format

The API always returns a structured JSON response:

```json
{
  "reply": "...",
  "recommendations": [],
  "end_of_conversation": false
}
```

The assistant is designed to:
- Recommend immediately when meaningful hiring signals exist
- Avoid unnecessary clarifications
- Support iterative refinement
- Stay grounded in SHL catalog data
- Avoid hallucinated products and URLs

---

# API Usage

## Health Check
GET /health
Returns {"status": "ok"} when the service is ready.

## Chat
POST /chat

Request body:
{
  "messages": [
    {"role": "user", "content": "Hiring a mid-level Java developer"},
    {"role": "assistant", "content": "{...previous response...}"},
    {"role": "user", "content": "Add personality testing"}
  ]
}

The API is stateless. Every call must include the full conversation history.

# Retrieval First Architecture

This project was intentionally built as a retrieval heavy system rather than a prompt heavy system.

Instead of depending on a very large reasoning model, most of the engineering effort went into:
- Improving retrieval quality
- Structuring catalog data
- Combining semantic and lexical search
- Controlling hallucinations
- Reducing memory usage and latency

This approach allowed the system to remain lightweight while still producing relevant recommendations.

---

# 🔍 Retrieval Pipeline

## 1. Catalog Preprocessing

The SHL catalog was cleaned and transformed into retrieval friendly representations.

During preprocessing:
- Newline formatting issues inside JSON fields were cleaned
- Assessment metadata was standardized
- Embedding text and BM25 text were separated
- Structured retrieval fields were created

Each assessment contains information such as:
- Assessment name
- Description
- Skills
- Category
- Test type
- Use case

This improved both semantic and lexical retrieval quality.

---

## 2. Hybrid Retrieval

The retrieval layer combines:
- BM25 keyword retrieval
- FAISS vector similarity search

### BM25

BM25 captures exact hiring signals such as:
- Java
- SQL
- Sales manager
- Customer support
- Stakeholder communication

### Semantic Search

FAISS based semantic retrieval captures broader meaning and related hiring intent.

This helps when the exact wording is not present in the catalog.

---

## 3. Retrieval Fusion

Initially the system used direct weighted score fusion between BM25 and semantic similarity scores.

This produced unstable rankings because:
- BM25 scores are unbounded
- Vector similarity scores are normalized

The retrieval pipeline was later improved by normalizing both score distributions before combining them.

The final retrieval system retrieves a small high quality candidate set before passing context to the LLM.

---

# Embeddings and Vector Search

The project initially used:

```text
BAAI/bge-small-en-v1.5
```

for semantic embeddings.

Later the model was replaced with:

```text
all-MiniLM-L6-v2
```

to reduce memory usage and support deployment on free hosting infrastructure.

Embeddings are precomputed offline and stored locally so the server never regenerates them during startup.

FAISS is used for fast vector similarity search.

---

# 🧠 LLM Design

The conversational layer uses:

```text
Groq Llama 3.1 8B Instant
```

The LLM is mainly responsible for:
- Understanding recruiter intent
- Deciding when clarification is necessary
- Formatting grounded JSON responses
- Refining previous recommendations

The system prompt was intentionally kept compact to reduce latency and improve response consistency.

The assistant recommends assessments whenever meaningful hiring signals are detected instead of repeatedly asking questions.

---

# 🛡️ Grounding and Validation

One important issue during development was hallucinated SHL URLs.

For example, the LLM occasionally shortened product URLs for well known assessments like OPQ32r.

To solve this:
- Every recommendation is validated after generation
- Recommendation names are mapped back to catalog URLs
- Only known SHL catalog URLs are returned
- Invalid or hallucinated links are removed

This keeps the final output grounded in the catalog data.

---

# 🚀 Deployment

The API is built using:
- FastAPI
- FAISS
- Sentence Transformers
- BM25
- Groq API

The system was first tested on Render but later deployed on Railway because of memory limitations with transformer based workloads on free hosting tiers.

The deployment was optimized by:
- Precomputing embeddings
- Reducing embedding model size
- Minimizing runtime memory usage
- Avoiding large model loading during startup

---

# 📊 Evaluation

The system was tested across multiple recruiter style conversations covering:
- Vague hiring requests
- Role specific hiring
- Refinement requests
- Comparison queries
- Refusal handling
- Catalog grounding
- Schema consistency

The main evaluation focus areas were:
- Recommendation relevance
- Conversational behavior
- Hallucination resistance
- Deployment stability
- Response consistency

---

# Repository Structure

```text
/project-root

├── app.py                 # FastAPI entry point
├── services/              # LLM logic, parsing, validation
├── retrieval/             # Hybrid retrieval pipeline
├── embeddings/            # Precomputed embedding files
├── faiss_index/           # Saved FAISS vector index
├── data/                  # Processed SHL catalog data
├── requirements.txt       # Project dependencies
└── README.md
```

# 📡 Public API

Base URL:

```text
https://shl-agent-production-469c.up.railway.app
```

Available endpoints:

```text
GET  /health
POST /chat
```

Swagger documentation:

```text
https://shl-agent-production-469c.up.railway.app/docs
```
