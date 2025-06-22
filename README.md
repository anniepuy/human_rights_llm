# Human Rights LLM

This project is an AI-powered assistant that answers human rights-related questions using Retrieval-Augmented Generation (RAG) and a ReAct agent. It uses a local LLM (Mistral:latest via Ollama), LangChain, and Streamlit to deliver chat-based and structured report capabilities. It can also publish detailed markdown reports directly to Notion.

---

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com/) installed locally
- `llama3` model pulled in Ollama
- Virtual environment (recommended)

---

## LLM Setup (Ollama)

1. **Install Ollama**
2. ollama pull mistral:latest

## Clone repo

git clone https://github.com/yourusername/human_rights_llm.git
cd human_rights_llm

## Create virtual environment

python3 -m venv .venv
source .venv/bin/activate

## Install dependencies

pip install -r requirements.txt

# To run the load RAG documents from /data to ChromaDB

python backend/ingest_documents.py

#To run and test the RAG Chain
python backend/tools/rag_chain.py

# Start backend

python routes.py

#Start Streamlit
cd frontend
streamlit run app.py

Technologies Used
• LangChain
• Ollama
• ChromaDB
• Streamlit
• Notion SDK

⸻

Author

Ann Hagan

⸻

License

This project is licensed under the MIT License.
