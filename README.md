# LangChain SQL Q&A System

A natural language to SQL query system using LangChain and LangGraph.

## Quick Start

1. **Setup**
   ```bash
   python setup.py
   ```

2. **Test System**
   ```bash
   python tests/test_system.py
   ```

3. **Run Application**
   ```bash
   python src/main.py
   ```

## Configuration

Update `.env` file:
```env
DATABASE_URL=postgresql://postgres:nooveel@localhost:5432/chinook
OLLAMA_MODEL=tinyllama
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=your_key_here
```

## Project Structure

```
langchain-sql-qa/
├── src/
│   ├── database.py      # Database connection
│   ├── llm_config.py    # LLM configuration  
│   ├── chain.py         # LangGraph workflow
│   └── main.py          # Main application
├── tests/
│   └── test_system.py   # System tests
├── scripts/
│   └── clean_database.py # Database setup
└── requirements.txt     # Dependencies
```

## Usage

```
Your question: How many artists are there?
Processing...
Answer: There are 5 artists in the database.
```