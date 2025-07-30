from fastapi import FastAPI, HTTPException
from crud import get_top_products, get_channel_activity, search_messages
from schemas import ReportResponse, ChannelActivityResponse, SearchResponse
from routers import reports
import uvicorn

app = FastAPI(title="Telegram Analytical API")

@app.get("/api/reports/top-products", response_model=ReportResponse)
async def top_products(limit: int = 10):
    if limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be positive")
    products = get_top_products(limit)
    return {"top_products": products}

@app.get("/api/channels/{channel_name}/activity", response_model=ChannelActivityResponse)
async def channel_activity(channel_name: str):
    if not channel_name:
        raise HTTPException(status_code=400, detail="Channel name is required")
    activity = get_channel_activity(channel_name)
    return {"channel_name": channel_name, "activity": activity}

@app.get("/api/search/messages", response_model=SearchResponse)
async def search_messages_endpoint(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    results = search_messages(query)
    return {"messages": results}

# Include the reports router
app.include_router(reports.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)