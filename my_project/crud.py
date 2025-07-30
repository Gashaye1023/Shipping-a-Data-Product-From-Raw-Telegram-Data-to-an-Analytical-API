from database import get_db
from models import Message, Detection, Item
from schemas import ItemCreate
from sqlalchemy.orm import Session

def get_top_products(limit: int):
    """Fetch the top products based on detection count."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT d.detected_object_class, COUNT(*) as count
            FROM dbt-demo_marts.fct_image_detections d
            JOIN dbt-demo_marts.fct_messages m ON d.message_id = m.message_id
            GROUP BY d.detected_object_class
            ORDER BY count DESC
            LIMIT %s
        """, (limit,))
        return [{"detected_object_class": row[0], "count": row[1]} for row in cur.fetchall()]

def get_channel_activity(channel_name: str):
    """Retrieve message activity for a specified channel."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT DATE(m.date) as date, COUNT(*) as message_count
            FROM dbt-demo_marts.fct_messages m
            WHERE m.channel_name = %s
            GROUP BY DATE(m.date)
            ORDER BY date
        """, (channel_name,))
        return [{"date": str(row[0]), "message_count": row[1]} for row in cur.fetchall()]

def search_messages(query: str):
    """Search for messages containing a specific query."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.message_id, m.channel_name, m.message_text,
                   d.detected_object_class
            FROM dbt-demo_marts.fct_messages m
            LEFT JOIN dbt-demo_marts.fct_image_detections d
            ON m.message_id = d.message_id
            WHERE m.message_text ILIKE %s
            LIMIT 10
        """, (f'%{query}%',))
        return [
            {
                "message_id": row[0],
                "channel_name": row[1],
                "message_text": row[2],
                "detection": row[3] if row[3] else None
            } for row in cur.fetchall()
        ]

async def get_items(db: Session):
    """Retrieve all items from the database."""
    return db.query(Item).all()

async def create_item(db: Session, item: ItemCreate):
    """Create a new item in the database."""
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item