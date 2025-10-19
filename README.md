# Clinical Question Copilot

A specialized AI assistant for ICU and hospital clinical questions, grounded in MIMIC-IV demo data and clinical protocols.

## Features

- **Clinical Knowledge Base**: Built on MIMIC-IV demo data with real clinical notes and protocols
- **ICU/Hospital Focus**: Specialized for critical care and hospital medicine questions
- **Guardrails**: Ensures questions stay within clinical scope
- **RAG Architecture**: Retrieval-Augmented Generation for accurate, source-grounded answers

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. Open your browser to `http://localhost:8000`

## Example Questions

- "What was the blood gas threshold for acidosis management?"
- "What ventilator settings are standard for ARDS?"
- "What are the criteria for sepsis diagnosis?"
- "How do you manage acute respiratory failure?"

## Architecture

- **Backend**: FastAPI with async support
- **Vector Database**: ChromaDB for clinical knowledge retrieval
- **Embeddings**: Sentence Transformers for semantic search
- **Frontend**: Modern web interface with real-time chat
