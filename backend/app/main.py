import sys
import os
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')))
from backend.app.orchestrator import ProctorOrchestrator

# 1. Initialize the FastAPI web server instance
app = FastAPI(title="AzureAI-Proctor API Gateway",
    description="Production-ready Reasoning Agent Gateway for the AI-901 Gamified Proctor.",
    version="1.0.0")

# 2. Instantiate our RAG + Judge master orchestrator
# This loads our FAISS index and Groq client into memory ONCE when the server boots up.
orchestrator = ProctorOrchestrator()

# 3. Define the strict Data Schema for incoming requests using Pydantic
class EvaluationRequest(BaseModel):
    question: str
    user_answer: str

# 4. Create a health-check endpoint to verify the server is alive
@app.get("/")
def read_root():
    return {"status": "online", "message": "AzureAI-Proctor Core Reasoning Agent is running smoothly!"}

# 5. Create the primary endpoint to handle evaluation submissions
@app.post("/api/evaluate")
def evaluate_submission(payload: EvaluationRequest):
    """
    Receives an exam question and response, fetches Foundry IQ context via RAG,
    runs the LLM agent reasoning pass, and returns the breakdown plus structured point awards.
    """
    try:
        q = payload.question.strip()
        ans = payload.user_answer.strip()

        if not q or not ans:
            raise HTTPException(status_code=400, detail="Question and user_answer cannot be empty fields.")

        # Fire off the end-to-end processing pipeline!
        report = orchestrator.run_proctor(question=q, user_answer=ans)

        # Game Engine Logic: Programmatically extract score tags from the judge's first line
        # This shields the frontend from having to guess or string-search complex markdown blocks
        score_status = "Fail"
        if "SCORE: Pass" in report:
            score_status = "Pass"
        elif "SCORE: Partial" in report:
            score_status = "Partial"

        # Return a structured JSON response to whoever called our API
        return {
            "success": True,
            "score": score_status,
            "evaluation_report": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
