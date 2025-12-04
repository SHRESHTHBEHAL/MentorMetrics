import os
import psycopg2
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote

load_dotenv()

def run_sql_file(file_path):
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables.")
        return False

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False

    try:
        print("Connecting to database...")
        parsed = urlparse(database_url)
        username = parsed.username
        password = unquote(parsed.password) if parsed.password else None
        hostname = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path.lstrip('/')
        
        conn = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print(f"Reading SQL file: {file_path}")
        with open(file_path, 'r') as f:
            sql_content = f.read()
            
        print("Executing SQL...")
        cur.execute(sql_content)
        
        print("SQL executed successfully.")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error executing SQL: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_sql.py <path_to_sql_file>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    if run_sql_file(file_path):
        print("Success!")
    else:
        print("Failed.")
        sys.exit(1)
