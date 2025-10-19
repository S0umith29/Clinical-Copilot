# Clinical Question Copilot - Usage Guide

## Overview

The Clinical Question Copilot is an AI assistant specialized for ICU and hospital clinical questions, grounded in MIMIC-IV demo data and clinical protocols. It provides evidence-based answers while maintaining strict guardrails to ensure questions stay within the clinical domain.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python3 main.py
```

### 3. Access the Web Interface
Open your browser to: `http://localhost:8000`

## Example Questions

### Clinical Questions (Supported)
- "What are the ventilator settings for ARDS?"
- "What is the blood gas threshold for acidosis management?"
- "What are the criteria for sepsis diagnosis?"
- "How do you manage acute respiratory failure?"
- "What are the standard sedation protocols in ICU?"
- "How do you titrate vasopressors in cardiogenic shock?"
- "What are the guidelines for central line insertion?"

### Non-Clinical Questions (Blocked)
- "How do you cook pasta?"
- "What's the weather like today?"
- "Tell me about programming"
- "What's the best restaurant in town?"

## API Usage

### Ask a Question
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the ventilator settings for ARDS?"}'
```

### Get System Stats
```bash
curl http://localhost:8000/api/stats
```

### Get Suggested Questions
```bash
curl http://localhost:8000/api/suggestions
```

## Guardrails

The system includes robust guardrails that:

1. **Detect Clinical Content**: Uses keyword matching and pattern recognition to identify clinical questions
2. **Block Non-Clinical Questions**: Prevents answers to questions outside the ICU/hospital domain
3. **Provide Suggestions**: Offers relevant clinical question examples when guardrails are triggered
4. **Maintain Focus**: Ensures all responses are grounded in clinical protocols and MIMIC-IV data

## Knowledge Base

The system includes:

- **8 Clinical Protocols**: Covering ARDS, acidosis, sepsis, respiratory failure, hemodynamics, sedation, nutrition, and infection control
- **9 Clinical Cases**: Real-world examples from MIMIC-IV demo data
- **17 Total Documents**: All indexed for semantic search

## Search Features

- **Semantic Search**: Uses sentence transformers for intelligent matching
- **Similarity Scoring**: Ranks results by relevance (threshold: 0.3)
- **Source Attribution**: Shows which protocols or cases informed the answer
- **Context Awareness**: Provides relevant clinical context for each answer

## Testing

Run the test suite:
```bash
python3 test_copilot.py
```

This will test:
- Clinical question recognition
- Guardrail functionality
- Knowledge base search
- Response generation

## Project Structure

```
├── main.py                 # FastAPI web application
├── copilot_engine.py       # Main copilot logic
├── knowledge_base.py       # ChromaDB knowledge management
├── guardrails.py          # Clinical scope validation
├── config.py              # Configuration settings
├── test_copilot.py        # Test suite
├── run.py                 # Startup script
├── requirements.txt       # Dependencies
├── data/mimic_demo/       # Clinical knowledge base
│   ├── clinical_protocols.json
│   └── clinical_notes.json
└── templates/             # Web interface
    └── index.html
```

## Important Notes

1. **Demo Data**: This system uses MIMIC-IV demo data, not real patient data
2. **Clinical Disclaimer**: Always consult current guidelines and your clinical team for patient care decisions
3. **Scope Limitation**: The system is designed specifically for ICU/hospital clinical questions
4. **Educational Purpose**: Intended for educational and research purposes

## Configuration

Key settings in `config.py`:
- `similarity_threshold`: Minimum similarity score for search results (default: 0.3)
- `embedding_model`: Sentence transformer model for embeddings
- `clinical_keywords`: Keywords used for clinical content detection

## Troubleshooting

### Common Issues

1. **Dependencies**: Make sure all packages are installed with `pip install -r requirements.txt`
2. **Port Conflicts**: If port 8000 is busy, modify the port in `main.py`
3. **Memory Issues**: The system loads ML models on startup - ensure sufficient RAM
4. **Search Issues**: If no results found, try rephrasing the question or check similarity threshold

### Getting Help

- Check the console output for error messages
- Verify the knowledge base loaded correctly (should show 17 documents)
- Test with the provided example questions
- Use the test suite to verify functionality

## Best Practices

1. **Ask Specific Questions**: More specific questions yield better results
2. **Use Clinical Terminology**: Include relevant medical terms in your questions
3. **Check Sources**: Always review the source information provided
4. **Verify Information**: Cross-reference with current clinical guidelines
5. **Stay in Scope**: Keep questions focused on ICU/hospital clinical topics
