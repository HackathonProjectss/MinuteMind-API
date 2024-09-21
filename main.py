from fastapi import FastAPI, Request, UploadFile, File, Form , HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from core.config import settings
from core.logger import logger
from pydantic import BaseModel
from typing import List
from services.watsonx import Watsonx, parse_audio, authenticate_watsonx
import json
from openai import OpenAI

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/openapi.json",
    docs_url=f"/docs",
    redoc_url=None,
)
allowed_origins = [
    "http://localhost:3000", 
    "http://localhost:5173",
    "https://minute-mind-ui.vercel.app"
]

# Define the Pydantic model for the user information
class User(BaseModel):
    name: str    
    email: str


# Define the Pydantic model for the request payload
class SummarizeRequest(BaseModel):
    title: str
    users: List[User]


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred"},
    )

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the MinuteMind API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to MinuteMind API"}


@app.post("/api/summarize")
async def summarize_content(
    meeting_info: str = Form(...),  # Accepting as a string
    audio: UploadFile = File(...)
):
    # Parse the JSON string into a dictionary
    try:
        team_info_dict = json.loads(meeting_info)
        team_info_model = SummarizeRequest(**team_info_dict)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail="Invalid JSON format") from e
    
    logger.info("Transcribing audio...")
    tanscribed_text = await parse_audio(audio)
    logger.info("Finished transcribing audio")
    
    logger.info("Authenticating with WatsonX...")
    try:
        token = await authenticate_watsonx(settings.WATSONX_API_KEY)
    except Exception as e:
        logger.error(f"Failed to authenticate with WatsonX: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to authenticate with WatsonX") from e
    logger.info("Authenticated with WatsonX")
    
    watsonx = Watsonx(token, settings.WATSONX_BASE_URL, settings.WATSONX_VERSION, settings.WATSONX_PROJECT_ID,)
    
    logger.info("Summarizing text...")
    summary = await watsonx.summarize_text(tanscribed_text, "meta-llama/llama-3-1-70b-instruct")
    logger.info("Finished summarizing text")
    
    logger.info("Generating action items...")
    action_items = await watsonx.generate_action_items(tanscribed_text, team_info_model.users, "meta-llama/llama-3-1-70b-instruct")
    logger.info("Finished generating action items")
    
    logger.debug({
        "summary": summary,
        "action_items": action_items
    })

    return {"summary": summary, "action_items": action_items}





# Add CORSMiddleware to the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies to be included in cross-origin requests
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)