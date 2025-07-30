import psycopg2
import json
import glob
import os

# Database connection paramers
DB_NAME = 'Shipping'
DB_USER = 'postgres'
DB_PASSWORD = '1024'
DB_HOST = 'localhost'  
DB_PORT = '5432' 
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()
# Base directory containing the folders with JSON files
base_dir = 'data/telegram_messages'

# Iterate through each folder in the base directory
for foldername in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, foldername)
    
    # Check if the path is a directory
    if os.path.isdir(folder_path):
        # Iterate through each JSON file in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    # Insert data into the raw schema
                    for record in data:
                        cursor.execute(
                            "INSERT INTO raw_schema.raw_table (json_data) VALUES (%s)",
                            (json.dumps(record),)
                        )

# Commit changes and close the connection
conn.commit()
cursor.close()
conn.close()
