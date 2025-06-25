from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
import logging

app = FastAPI(
    title="Schedule AI Manager",
    description="AI assistant for managing Google Calendar via LangGraph",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logging.info("✅ Schedule AI Manager started.")
    for route in app.routes:
        logging.info(f"📡 Route: {route.path} → {route.name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
