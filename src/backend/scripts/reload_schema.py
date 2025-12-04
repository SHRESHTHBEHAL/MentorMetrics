import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def reload_schema():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in environment variables.")
        print("Please ensure DATABASE_URL is set in your .env file.")
        return False

    try:
        print("Connecting to database...")
        from urllib.parse import urlparse, unquote
        
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
        
        print("Executing schema reload notification...")
        cur.execute("NOTIFY pgrst, 'reload schema';")
        
        print("Schema reload notification sent successfully.")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error reloading schema: {str(e)}")
        return False

if __name__ == "__main__":
    if reload_schema():
        print("Success!")
    else:
        print("Failed.")
