import psycopg2
import requests
from langchain_ollama import ChatOllama
from langchain_community.utilities import SQLDatabase
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="chinook",
            user="postgres",
            password="nooveel",
            client_encoding="utf8"
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Database OK - Tables found: {table_count}"
        
    except Exception as e:
        return False, f"Database connection failed: {e}"

def test_ollama_connection():
    """Test Ollama connection"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_count = len(models.get('models', []))
            
            llm = ChatOllama(model="tinyllama", base_url="http://localhost:11434", temperature=0)
            response = llm.invoke("What is 2+2?")
            
            return True, f"Ollama OK - {model_count} models available"
        else:
            return False, "Ollama server not responding"
            
    except Exception as e:
        return False, f"Ollama connection failed: {e}"

def test_langchain_database():
    """Test LangChain SQLDatabase"""
    try:
        db_url = "postgresql://postgres:nooveel@localhost:5432/chinook?client_encoding=utf8"
        db = SQLDatabase.from_uri(db_url)
        
        tables = db.get_usable_table_names()
        return True, f"LangChain DB OK - Tables: {tables}"
        
    except Exception as e:
        return False, f"LangChain database failed: {e}"

def test_full_system():
    """Test full system integration"""
    try:
        sys.path.append('src')
        from chain import graph_builder
        
        test_question = "How many artists are there?"
        result = None
        
        for step in graph_builder.stream({"question": test_question}, stream_mode="updates"):
            for node_name, node_output in step.items():
                if node_name == "generate_answer" and "answer" in node_output:
                    result = node_output["answer"]
        
        if result:
            return True, f"Full system OK - Answer generated"
        else:
            return False, "Full system failed - No answer generated"
            
    except Exception as e:
        return False, f"Full system test failed: {e}"

def run_all_tests():
    """Run all tests"""
    print("Running System Tests...")
    print("=" * 40)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Ollama Connection", test_ollama_connection),
        ("LangChain Database", test_langchain_database),
        ("Full System", test_full_system)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        success, message = test_func()
        results[test_name] = success
        status = "PASS" if success else "FAIL"
        print(f"  {status}: {message}")
    
    print("\n" + "=" * 40)
    print("Test Results:")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\nAll tests passed! System is ready.")
    else:
        print("\nSome tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()