from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import logging

from aiService.services.llm_client import ask_llm

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="CalcVoyager Chat Service",
    description="Backend API service for the CalcVoyager AI chatbot",
    version="1.0.0"
)


class ChatRequest(BaseModel):
    message: str
    topic: str = ""
    history: list = Field(default_factory=list)

class ChatResponse(BaseModel):
    answer: str


@app.get("/")
async def home():
    return {
        "status": "running",
        "service": "CalcVoyager Chat Service"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    try:

        logging.info(
            f"Received question: {request.message}"
        )

        answer = await ask_llm(
            message=request.message,
            topic=request.topic,
            history=request.history
        )

        return ChatResponse(
            answer=answer
        )

    except Exception as e:

        logging.error(
            f"Chat error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail="AI service unavailable"
        )