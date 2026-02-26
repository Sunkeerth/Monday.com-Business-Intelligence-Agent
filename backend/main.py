from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from query_processor import interpret_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChartData(BaseModel):
    labels: list[str]
    values: list[float]

class ChatResponse(BaseModel):
    answer: str
    trace: list[str]
    chart: Optional[ChartData] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    trace = []
    answer, trace, chart_data = interpret_query(request.message, trace)
    return ChatResponse(answer=answer, trace=trace, chart=chart_data)

@app.get("/")
def root():
    return {"message": "Monday BI Agent API is running."}