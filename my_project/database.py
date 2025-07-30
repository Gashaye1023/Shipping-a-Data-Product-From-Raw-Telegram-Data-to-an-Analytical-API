import psycopg2
from contextlib import contextmanager

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="Shipping_dbt", # Ensure this matches your database name
        user="postgres",
        password="1024" 
    )
    return conn

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()