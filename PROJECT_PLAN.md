\# Project Plan – Local AI Operator



\---



\## 🎯 Objective



Build an offline AI system that:



\* Processes files (Excel, PDF, Word)

\* Provides AI insights

\* Manages tasks

\* Works locally using Gemma



\---



\## 🧠 Architecture



```

User Input

&#x20;  ↓

Planner (intent detection)

&#x20;  ↓

Router

&#x20;  ↓

Tools (Excel / Docs / Scheduler)

&#x20;  ↓

LLM (Gemma via Ollama)

&#x20;  ↓

Response

```



\---



\## 🧩 Modules



\### 1. Tools Layer



\* excel\_tool → data analysis

\* doc\_tool → PDF + OCR + DOCX

\* scheduler → task management



\---



\### 2. Agent Layer



\* planner → detect intent

\* router → execute task



\---



\### 3. LLM Layer



\* llm\_client → connects to Ollama

\* model: gemma3:4b



\---



\### 4. UI Layer



\* Streamlit app



\---



\## 🗂️ Development Phases



\### Phase 1 – Setup



\* environment

\* project structure



\---



\### Phase 2 – Core Tools



\* Excel analysis

\* PDF reader

\* OCR support



\---



\### Phase 3 – AI Integration



\* Ollama connection

\* text summarization



\---



\### Phase 4 – Agent System



\* planner

\* router

\* scheduler



\---



\### Phase 5 – UI + Demo



\* Streamlit UI

\* demo flow



\---



\### Phase 6 – Submission



\* GitHub

\* video

\* Kaggle writeup



\---



\## 🎬 Demo Flow



1\. Upload Excel → insights

2\. Upload PDF → summary

3\. Add tasks → AI plan



\---



\## 🏁 Success Criteria



\* Works offline

\* Uses Gemma

\* Clear demo

\* Strong impact story



\---



