# Shipping a Data Product - From Raw Telegram Data to an Analytical API

## Business Need

As a Data Engineer at Kara Solutions, you are tasked with building a comprehensive data platform that generates insights about Ethiopian medical businesses using data scraped from public Telegram channels. The goal is to design an end-to-end data pipeline that answers crucial business questions such as:

- What are the top 10 most frequently mentioned medical products or drugs across all channels?
- How do the prices or availability of specific products vary across different channels?
- Which channels feature the most visual content (e.g., images of pills vs. creams)?
- What are the daily and weekly trends in posting volume for health-related topics?

To address these needs, we will implement a modern ELT (Extract, Load, Transform) framework, enabling us to extract raw data from Telegram, load it into a structured database, and transform it into valuable insights.

## Project Phases

### 1. Data Scraping and Collection
Utilizing the Telegram API, we will scrape relevant data from selected channels, including Chemed, Lobelia, and Tikvah. The raw data will be stored in a partitioned "Data Lake" structure, maintaining its integrity for future processing. Logging mechanisms will be in place to track scraping activities and capture errors.

### 2. Data Modeling and Transformation
The raw data will be transformed using dbt (Data Build Tool) to create a clean, reliable, and structured data model in a PostgreSQL data warehouse. We will design a star schema that includes fact and dimension tables to facilitate efficient analytical queries.

### 3. Data Enrichment with Object Detection
We will employ YOLOv8, a modern object detection model, to analyze images collected during scraping. The detected objects will be linked to the core data model, enhancing the dataset with visual insights.

### 4. Building an Analytical API
Using FastAPI, we will expose the transformed data through a well-structured API. This API will provide endpoints tailored to answer the specific business questions identified earlier, allowing for easy access to insights.

### 5. Pipeline Orchestration
To ensure reliability and observability, we will utilize Dagster for orchestrating the entire data pipeline. This will allow us to schedule and monitor the pipeline efficiently, ensuring that data flows smoothly from one stage to the next.

### steps
- **Data Extraction:** Utilizing the Telegram API with Telethon.
- **Data Modeling:** Designing and implementing a star schema.
- **ELT Pipeline Development:** Building layered data pipelines for efficient data flow.
- **Infrastructure Management:** Using Docker for environment consistency.
- **Data Transformation:** Performing robust transformations with dbt.
- **Object Detection:** Enriching data with YOLO.
- **API Development:** Creating analytical endpoints with FastAPI.
- **Pipeline Orchestration:** Managing workflows with Dagster.

### 
- Understanding of ELT vs. ETL architectures.
- Familiarity with layered data architecture (Data Lake, Staging, Data Marts).
- Best practices in data cleaning and validation.
- Structuring data for efficient analytical querying.
- Integrating unstructured data into a structured warehouse.