import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv()

def get_available_llm():
    """Get available LLM with priority: Ollama -> OpenAI"""
    
    ollama_models = [
        "codellama:7b-instruct-q4_0",
        "llama2:7b-chat-q4_0",
        "phi:latest",
        "mistral:7b-instruct-q4_0"
    ]
    
    for model in ollama_models:
        try:
            llm = ChatOllama(
                model=model,
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                temperature=0,
                top_k=1,
                top_p=0.1
            )
            
            test_prompt = "Create a PostgreSQL query to count records in table 'artist'. Return only SQL:"
            test_response = llm.invoke(test_prompt)
            
            response_text = test_response.content.strip().lower()
            if any(word in response_text for word in ['select', 'count', 'from', 'artist']):
                return llm, "ollama"
            
        except Exception:
            continue
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key.strip() and not api_key.startswith('your_'):
            llm = ChatOpenAI(
                temperature=0, 
                api_key=api_key, 
                model="gpt-3.5-turbo"
            )
            test_response = llm.invoke("Hi")
            return llm, "openai"
    except Exception:
        pass
    
    raise Exception("No LLM available. Please start Ollama or add valid OpenAI API key")

def get_llm_specific_prompt(llm_type):
    """Get LLM-specific prompts"""
    
    if llm_type == "ollama":
        return {
            "system_template": """You are a PostgreSQL expert. Create ONLY a valid SQL query.

Database tables: {table_info}

Rules:
- Return ONLY the SQL query, no explanations
- Use proper PostgreSQL syntax
- Limit to {top_k} results
- No markdown formatting

Question: {input}

SQL Query:""",
            "answer_template": """Question: {question}
SQL Query: {query}  
Database Result: {result}

Provide a clear, concise answer based on the result:"""
        }
    else:
        return {
            "system_template": """You are a PostgreSQL database expert. Given an input question, create a syntactically correct PostgreSQL query to run. 

Unless the user specifies a specific number of examples, always limit your query to at most {top_k} results using LIMIT clause.

Only use the following tables:
{table_info}

Question: {input}

Return ONLY the SQL query, no explanations or markdown formatting.""",
            "answer_template": """Based on the database query result, provide a clear and concise answer to the user's question.

Question: {question}
SQL Query: {query}
Query Result: {result}

Answer:"""
        }