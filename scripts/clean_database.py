import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import subprocess
import os

def clean_and_recreate_database():
    """Clean and recreate database with correct encoding"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="nooveel"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'chinook'
            AND pid <> pg_backend_pid()
        """)
        
        cursor.execute("DROP DATABASE IF EXISTS chinook")
        
        cursor.execute("""
            CREATE DATABASE chinook 
            WITH ENCODING 'UTF8' 
            LC_COLLATE='C' 
            LC_CTYPE='C' 
            TEMPLATE=template0
        """)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error recreating database: {e}")
        return False

def import_chinook_data():
    """Import Chinook data from SQL file"""
    sql_files = [
        "scripts/Chinook_PostgreSql.sql",
        "data/Chinook_PostgreSql.sql", 
        "Chinook_PostgreSql.sql"
    ]
    
    sql_file = None
    for file_path in sql_files:
        if os.path.exists(file_path):
            sql_file = file_path
            break
    
    if not sql_file:
        print("Chinook SQL file not found")
        return create_sample_data()
    
    try:
        env = os.environ.copy()
        env["PGPASSWORD"] = "nooveel"
        env["PGCLIENTENCODING"] = "UTF8"
        
        cmd = [
            "psql",
            "-h", "localhost",
            "-U", "postgres",
            "-d", "chinook",
            "-f", sql_file,
            "--set", "ON_ERROR_STOP=off"
        ]
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"Error importing data: {e}")
        return create_sample_data()

def create_sample_data():
    """Create minimal sample data"""
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
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS artist (
            artist_id SERIAL PRIMARY KEY,
            name VARCHAR(120) NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS album (
            album_id SERIAL PRIMARY KEY,
            title VARCHAR(160) NOT NULL,
            artist_id INTEGER REFERENCES artist(artist_id)
        );
        
        CREATE TABLE IF NOT EXISTS track (
            track_id SERIAL PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            album_id INTEGER REFERENCES album(album_id),
            milliseconds INTEGER,
            unit_price DECIMAL(10,2)
        );
        
        CREATE TABLE IF NOT EXISTS customer (
            customer_id SERIAL PRIMARY KEY,
            first_name VARCHAR(40) NOT NULL,
            last_name VARCHAR(20) NOT NULL,
            email VARCHAR(60),
            country VARCHAR(40)
        );
        
        CREATE TABLE IF NOT EXISTS employee (
            employee_id SERIAL PRIMARY KEY,
            first_name VARCHAR(20) NOT NULL,
            last_name VARCHAR(20) NOT NULL,
            title VARCHAR(30),
            reports_to INTEGER,
            email VARCHAR(60)
        );
        """)
        
        cursor.execute("""
        INSERT INTO artist (name) VALUES 
        ('AC/DC'), ('Accept'), ('Aerosmith'), ('Alanis Morissette'), ('Alice in Chains')
        ON CONFLICT DO NOTHING;
        
        INSERT INTO album (title, artist_id) VALUES 
        ('For Those About To Rock', 1), ('Balls to the Wall', 2), ('Restless and Wild', 2)
        ON CONFLICT DO NOTHING;
        
        INSERT INTO track (name, album_id, milliseconds, unit_price) VALUES 
        ('For Those About To Rock', 1, 343719, 0.99), ('Put The Finger On You', 1, 205662, 0.99)
        ON CONFLICT DO NOTHING;
        
        INSERT INTO customer (first_name, last_name, email, country) VALUES 
        ('Luis', 'Goncalves', 'luis@test.com', 'Brazil'), ('Leonie', 'Kohler', 'leonie@test.com', 'Germany')
        ON CONFLICT DO NOTHING;
        
        INSERT INTO employee (first_name, last_name, title, email) VALUES 
        ('Andrew', 'Adams', 'General Manager', 'andrew@test.com'), ('Nancy', 'Edwards', 'Sales Manager', 'nancy@test.com')
        ON CONFLICT DO NOTHING;
        """)
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

def verify_database():
    """Verify database tables and data"""
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
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"Available tables: {[t[0] for t in tables]}")
        
        main_tables = ['artist', 'album', 'track', 'customer', 'employee']
        for table in main_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} records")
            except:
                print(f"{table}: table not found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error verifying database: {e}")
        return False

if __name__ == "__main__":
    print("Setting up Chinook Database...")
    
    if clean_and_recreate_database():
        print("Database created successfully")
        if import_chinook_data():
            print("Data imported successfully")
        verify_database()
    else:
        print("Failed to create database")