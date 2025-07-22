import os
import json
import psycopg2
from psycopg2 import sql
import logging
from datetime import datetime

# Configure logging for this script
logging.basicConfig(filename='data_loading.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

DB_NAME = 'Shipping'
DB_USER = 'postgres'
DB_PASSWORD = '1024'
DB_HOST = 'localhost'  
DB_PORT = '5432' 

# Base directory where your scraped raw data is stored
RAW_DATA_BASE_DIR = "data/raw/telegram_messages"

def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True # Set autocommit to True
        logging.info("Successfully connected to PostgreSQL database.")
        return conn
    except psycopg2.Error as e:
        logging.critical(f"Error connecting to PostgreSQL database: {e}")
        raise

def create_raw_table(cursor):
    """Creates the raw.telegram_messages table if it doesn't exist."""
    try:
        cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {schema_name}").format(
            schema_name=sql.Identifier(RAW_SCHEMA)
        ))
        logging.info(f"Schema '{RAW_SCHEMA}' ensured to exist.")

        # Table to store raw Telegram messages. Using JSONB for flexible storage.
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {schema_name}.telegram_messages (
                id SERIAL PRIMARY KEY,
                channel_username VARCHAR(255) NOT NULL,
                scraped_date DATE NOT NULL,
                message_id BIGINT NOT NULL,
                message_date TIMESTAMP WITH TIME ZONE,
                message_text TEXT,
                sender_id BIGINT,
                is_photo BOOLEAN,
                image_path TEXT,
                raw_json JSONB, -- To store the entire raw message JSON
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """).format(schema_name=sql.Identifier(RAW_SCHEMA))
        cursor.execute(create_table_query)
        logging.info(f"Table '{RAW_SCHEMA}.telegram_messages' ensured to exist.")
        cursor.execute(sql.SQL("""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'uq_telegram_messages_channel_message_date_id'
                ) THEN
                    ALTER TABLE {schema_name}.telegram_messages
                    ADD CONSTRAINT uq_telegram_messages_channel_message_date_id UNIQUE (channel_username, message_id, scraped_date);
                END IF;
            END $$;
        """).format(schema_name=sql.Identifier(RAW_SCHEMA)))
        logging.info("Unique constraint for raw.telegram_messages ensured to exist.")

    except psycopg2.Error as e:
        logging.error(f"Error creating raw table or schema: {e}")
        raise

def load_json_to_postgres(file_path, channel_username, scraped_date, cursor):
    """Loads a single JSON file's content into the PostgreSQL table."""
    logging.info(f"Loading data from {file_path} into PostgreSQL...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            messages = json.load(f)

        for message in messages:
            insert_query = sql.SQL("""
                INSERT INTO {schema_name}.telegram_messages (
                    channel_username, scraped_date, message_id, message_date,
                    message_text, sender_id, is_photo, image_path, raw_json
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
                ) ON CONFLICT (channel_username, message_id, scraped_date) DO NOTHING;
            """).format(schema_name=sql.Identifier(RAW_SCHEMA))

            cursor.execute(insert_query, (
                channel_username,
                scraped_date,
                message.get('id'),
                message.get('date'),
                message.get('text'),
                message.get('sender_id'),
                message.get('is_photo'),
                message.get('image_path'),
                json.dumps(message) # Store the entire message dict as JSONB
            ))
        logging.info(f"Successfully loaded {len(messages)} messages from {os.path.basename(file_path)}.")
    except Exception as e:
        logging.error(f"Error loading {file_path} into PostgreSQL: {e}")
        logging.exception("Detailed error traceback:")


def main():
    """Main function to iterate through raw data and load into PostgreSQL."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        create_raw_table(cur)
        for date_dir in os.listdir(RAW_DATA_BASE_DIR):
            full_date_path = os.path.join(RAW_DATA_BASE_DIR, date_dir)
            if not os.path.isdir(full_date_path):
                continue
            
            try:
                scraped_date = datetime.strptime(date_dir, '%Y-%m-%d').date()
            except ValueError:
                logging.warning(f"Skipping invalid date directory: {date_dir}")
                continue

            for channel_dir in os.listdir(full_date_path):
                full_channel_path = os.path.join(full_date_path, channel_dir)
                if not os.path.isdir(full_channel_path):
                    continue

                channel_username = channel_dir
                json_file_path = os.path.join(full_channel_path, 'messages.json')

                if os.path.exists(json_file_path):
                    load_json_to_postgres(json_file_path, channel_username, scraped_date, cur)
                else:
                    logging.warning(f"JSON file not found for {channel_username} on {date_dir}: {json_file_path}")

    except Exception as e:
        logging.critical(f"An unhandled error occurred during data loading: {e}")
        logging.exception("Detailed error traceback:")
    finally:
        if conn:
            conn.close()
            logging.info("PostgreSQL connection closed.")

if __name__ == "__main__":
    if not os.path.exists(RAW_DATA_BASE_DIR):
        logging.critical(f"Raw data base directory not found: {RAW_DATA_BASE_DIR}. Please run Task 1 scraping first.")
    else:
        main()