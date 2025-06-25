import subprocess
import sys
import os

def install_requirements():
    """Install Python packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except Exception as e:
        print(f"Package installation failed: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    directories = ["src", "tests", "scripts", "data"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
    return True

def check_postgresql():
    """Check if PostgreSQL is running"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="nooveel"
        )
        conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL check failed: {e}")
        return False

def setup_database():
    """Setup database"""
    try:
        sys.path.append('scripts')
        from clean_database import clean_and_recreate_database
        
        if clean_and_recreate_database():
            return True
        return False
        
    except Exception as e:
        print(f"Database setup failed: {e}")
        return False

def check_ollama():
    """Check if Ollama is available"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return True
        return False
    except Exception:
        return False

def check_chinook_data():
    """Check if Chinook data exists in database"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="chinook",
            user="postgres",
            password="nooveel",
            client_encoding="utf8"
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM artist")
        artist_count = cursor.fetchone()[0]
        
        conn.close()
        return artist_count > 0
            
    except Exception:
        return False

def main():
    print("Setting up LangChain SQL Q&A System")
    print("=" * 40)
    
    critical_steps = [
        ("Creating directories", setup_directories),
        ("Installing packages", install_requirements),
        ("Checking PostgreSQL", check_postgresql),
        ("Setting up database", setup_database),
    ]
    
    optional_steps = [
        ("Checking Ollama", check_ollama),
        ("Checking Chinook data", check_chinook_data),
    ]
    
    for step_name, step_func in critical_steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"Critical step '{step_name}' failed!")
            return False
    
    print(f"\nOptional checks...")
    optional_results = {}
    for step_name, step_func in optional_steps:
        optional_results[step_name] = step_func()
    
    print("\nSetup Summary:")
    print("Critical components: ALL READY")
    
    print("Optional components:")
    for step_name, result in optional_results.items():
        status = "Ready" if result else "Not available"
        print(f"  - {step_name}: {status}")
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Run tests: python tests/test_system.py")
    print("2. Start application: python src/main.py")
    
    return True

if __name__ == "__main__":
    main()