import os
from datetime import datetime
from PIL import Image
import psycopg2
from ultralytics import YOLO

# Load the pre-trained YOLOv8 model
model = YOLO("yolov8n.pt")  # Use a lightweight model

# Database connection parameters
db_params = {
    "host": "localhost",
    "port": "5432",
    "database": "Shipping_dbt",
    "user": "postgres",
    "password": "1024"
}

# Directories containing scraped images
image_dirs = [
    "data/raw/telegram_messages/2025-07-22/Chemed123/media",
    "data/raw/telegram_messages/2025-07-22/lobelia4cosmetics/media",
    "data/raw/telegram_messages/2025-07-22/tikvahpharma/media"
]

# Result directory for visualized images
result_dir = "data/raw/telegram_messages/2025-07-22/result"

def connect_db():
    return psycopg2.connect(**db_params)

def detect_objects(image_path):

    results = model(image_path)
    detections = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.basename(image_path)
    output_path = os.path.join(result_dir, f"detected_{timestamp}_{base_name}")

    for result in results:
        im_array = result.plot()  # Get BGR numpy array of predictions
        im = Image.fromarray(im_array[..., ::-1])  # Convert to RGB PIL image
        im.save(output_path)
        
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            confidence = float(box.conf[0])
            detections.append((class_name, confidence))
    
    return detections, output_path

def store_staging_detections(message_id, detections):
      conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        
        # Create staging table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.stg_image_detections (
                message_id INTEGER,
                detected_object_class VARCHAR(100),
                confidence_score FLOAT,
                detection_time TIMESTAMP
            )
        """)
        
        for class_name, confidence in detections:
            cur.execute(
                """
                INSERT INTO raw.stg_image_detections (message_id, detected_object_class, confidence_score, detection_time)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (message_id, detected_object_class) DO NOTHING
                """,
                (message_id, class_name, confidence, datetime.now())
            )
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def process_images():
    """Process all images in the specified directories."""
    os.makedirs(result_dir, exist_ok=True)
    
    for image_dir in image_dirs:
        if not os.path.exists(image_dir):
            print(f"Directory not found: {image_dir}")
            continue
            
        print(f"\nProcessing images in: {image_dir}")
        
        for filename in os.listdir(image_dir):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            image_path = os.path.join(image_dir, filename)
            
            try:
                message_id = int(''.join(filter(str.isdigit, filename.split('.')[0])))
            except ValueError:
                print(f"Skipping {filename}: Unable to extract message_id")
                continue
            
            try:
                detections, output_path = detect_objects(image_path)
                store_staging_detections(message_id, detections)
                
                print(f"Processed {filename}:")
                print(f"- Detections: {len(detections)} objects")
                print(f"- Results saved to: {output_path}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    print("Starting image processing...")
    process_images()
    print("\nProcessing complete!")