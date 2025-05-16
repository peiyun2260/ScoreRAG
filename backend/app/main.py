from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import news_router
import logging

app = FastAPI()

# CORS settings
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Mount routers
app.include_router(news_router.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "ScoreRAG API ready."}
