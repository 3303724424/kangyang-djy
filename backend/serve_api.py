"""Run the local FastAPI service without remembering a long uvicorn command."""

import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host=os.getenv("TRAVEL_API_HOST", "127.0.0.1"),
        port=int(os.getenv("TRAVEL_API_PORT", "8000")),
        reload=False,
    )
