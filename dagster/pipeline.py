from dagster import job, op, Out, In, String, ScheduleDefinition
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

@op(out=Out(String))
def scrape_telegram_data():
    """Scrape Telegram data and return the raw data path."""
    raw_path = "data/raw/telegram_messages/2025-07-DD"
    script_path = "src/scraper.py"

    logging.info("Scraping data from Telegram channels...")
    subprocess.run([
        "Scripts/python.exe",
        script_path
    ], check=True)
    
    return raw_path

@op(ins={"raw_path": In(String)}, out=Out(String))
def load_raw_to_postgres(raw_path):
    """Load scraped data into PostgreSQL raw tables."""
    dbt_path = "dbt/telegrahm_dbt"
    
    logging.info("Loading raw data to PostgreSQL...")
    subprocess.run([
        "Scripts/dbt.exe",
        "run", "--project-dir", dbt_path, "--select", "stg_messages"
    ], check=True)
    
    return dbt_path

@op(ins={"dbt_path": In(String)}, out=Out(String))
def run_dbt_transformations(dbt_path):
    """Run dbt transformations to create data marts."""
    logging.info("Running DBT transformations...")
    subprocess.run([
        "Scripts/dbt.exe",
        "run", "--project-dir", dbt_path
    ], check=True)
    
    return dbt_path

@op(ins={"dbt_path": In(String)})
def run_yolo_enrichment(dbt_path):
    """Run YOLO enrichment on images and store detections."""
    script_path = "Scripts/enrich_images.py"

    logging.info("Running YOLO enrichment on images...")
    subprocess.run([
        "Scripts/python.exe",
        script_path
    ], check=True)
    subprocess.run([
        "Scripts/dbt.exe",
        "run", "--project-dir", dbt_path, "--select", "fct_image_detections"
    ], check=True)

# Define the job
@job
def telegram_pipeline():
    raw_path = scrape_telegram_data()
    dbt_path = load_raw_to_postgres(raw_path)
    run_dbt_transformations(dbt_path)
    run_yolo_enrichment(dbt_path)

# Define a schedule
telegram_schedule = ScheduleDefinition(
    job=telegram_pipeline,
    cron_schedule="0 0 * * *",  # Runs daily at midnight UTC (3:00 AM EAT)
)