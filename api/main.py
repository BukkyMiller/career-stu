"""
FastAPI application for Career STU
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routes import chat, learner

load_dotenv()

app = FastAPI(
    title="Career STU API",
    description="AI-powered career support assistant API",
    version="0.2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(learner.router, prefix="/learner", tags=["learner"])


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Career STU API",
        "version": "0.2.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
