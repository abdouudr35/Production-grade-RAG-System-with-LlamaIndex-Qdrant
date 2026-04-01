# 🚀 Production-grade RAG System with LlamaIndex & Qdrant

A robust, ultra-fast, and production-ready Retrieval-Augmented Generation (RAG) system. This project allows users to chat with and extract information from PDF documents using a modern asynchronous architecture and state-of-the-art AI models.

## ✨ Key Features

* ⚡ **Ultra-Fast Inference:** Utilizes the **Groq** API (`llama-3.3-70b-versatile` model) powered by LPU technology for millisecond response times.
* 🔍 **High-Performance Vector Search:** Optimized indexing and semantic search using **Qdrant**.
* ⚙️ **Intelligent Orchestration:** Full data pipeline integration via **LlamaIndex**.
* ⏱️ **Asynchronous Processing & Security:** Background task management, event streaming, and rate-limiting powered by **Inngest**.
* 🖥️ **Interactive Web Interface:** Smooth and responsive frontend built with **Streamlit**, featuring caching techniques for optimal performance.

## 🛠️ Tech Stack

* **Language:** Python
* **AI Orchestrator:** LlamaIndex
* **Vector Database:** Qdrant
* **LLM:** Groq (via AsyncOpenAI adapter)
* **Event-Driven Backend:** Inngest
* **Frontend:** Streamlit

## ⚙️ Installation and Setup

### Prerequisites
* Python 3.9 or higher
* A valid Groq API key (`gsk_...`)

### 1. Clone the repository
```bash
git clone [https://github.com/abdouudr35/Production-grade-RAG-System-with-LlamaIndex-Qdrant.git](https://github.com/abdouudr35/Production-grade-RAG-System-with-LlamaIndex-Qdrant.git)
cd Production-grade-RAG-System-with-LlamaIndex-Qdrant
