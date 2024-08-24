from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from core.config import settings
from core.logger import logger
from pydantic import BaseModel
from typing import List
from services.watsonx import Watsonx
import json

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/openapi.json",
    docs_url=f"/docs",
    redoc_url=None,
)
allowed_origins = [
    "http://localhost:3000", 
]

# Define the Pydantic model for the user information
class User(BaseModel):
    name: str    
    email: str

# Define the Pydantic model for the request payload
class SummarizeRequest(BaseModel):
    team_name: str
    users: List[User]


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred"},
    )



@app.get("/")
async def read_root():
    return {"message": "Welcome to MinuteMind API"}

@app.post("/api/summarize")
async def summarize_content(
    team_name: str = Form(...),
    users: str = Form(...),
    audio: UploadFile = File(...)
):
    # Parse the JSON string into a list of User objects
    users_list = json.loads(users)
    parsed_users = [User(**user) for user in users_list]

    #TODO: Implement the audio processing logic
    #TODO: Send transcribed text to WatsonX API for summarization
    #TODO: Return the summarized text to the client
    watsonx = Watsonx(settings.WATSONX_API_KEY, settings.BASE_URL, "2021-08-01")
    watsonx.summarize_text("This is a test text")
    watsonx.generate_action_items("This is a test text", parsed_users)
    watsonx.generate_emails("This is a test text", parsed_users)
    watsonx.parse_audio(audio)
    # Process the team name, users, and audio file as needed
    return {"message": "Processing complete", "team_name": team_name, "users": parsed_users}


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