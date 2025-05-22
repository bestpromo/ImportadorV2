import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env at the project root
load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def count_imported_offers(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT merchant_id FROM awin_catalog_import_temp WHERE imported = false
        """)
        result = cur.fetchone()
        return result[0] if result else 0

if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("Database connection established successfully!")
        imported_count = count_imported_offers(conn)
        print(f"Total offers with imported = TRUE: {imported_count}")
        conn.close()
    else:
        print("Failed to establish database connection.")