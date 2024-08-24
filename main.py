import base64
import io
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

class ActionItem(BaseModel):
    user: User
    task: str

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

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the MinuteMind API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to MinuteMind API"}

@app.post("/api/summarize")
async def summarize_content(
    team_name: str = Form(...),
    users: str = Form(...),
    action_items: List[ActionItem] = Form(...),
    audio: UploadFile = File(...)
):
    
    # # Parse the JSON string into a list of User objects
    # users_list = json.loads(users)
    # parsed_users = [User(**user) for user in users_list]

    # #TODO: Implement the audio processing logic
    # #TODO: Send transcribed text to WatsonX API for summarization
    # #TODO: Return the summarized text to the client
    # watsonx = Watsonx(settings.WATSONX_API_KEY, settings.BASE_URL, "2021-08-01")
    # watsonx.summarize_text("This is a test text")
    # watsonx.generate_action_items("This is a test text", parsed_users)
    # watsonx.generate_emails("This is a test text", parsed_users)
    # watsonx.parse_audio(audio)
    # Process the team name, users, and audio file as needed

    watsonx = Watsonx(settings.WATSONX_API_KEY, settings.BASE_URL)

    audio_content = await audio.read()
    transcript_results = watsonx.parse_audio(audio_content)
    transcript_text = " ".join([result['alternatives'][0]['transcript'] for result in transcript_results])

    # Summarize the transcript
    summary = watsonx.summarize_text(transcript_text)

    # Encode audio content as base64
    encoded_audio = base64.b64encode(audio_content).decode('utf-8')

    # return {
    # "team_name": "Team Alpha",
    # "summary": "The meeting discussed project deadlines and assigned tasks for the upcoming sprint. Key points included finalizing the design, improving code quality, and ensuring timely delivery.",
    # "action_items": [
    #     {
    #     "user": {
    #         "name": "John Doe",
    #         "email": "johndoe@example.com"
    #     },
    #     "tasks": "- [ ] **Finalize the design of the homepage** by *August 31, 2024*\n- [ ] **Review code quality and provide feedback** by *August 28, 2024*"
    #     },
    #     {
    #     "user": {
    #         "name": "Jane Smith",
    #         "email": "janesmith@example.com"
    #     },
    #     "tasks": "- [ ] **Prepare the presentation** for the next client meeting by *September 2, 2024*\n- [ ] **Coordinate with the marketing team** by *August 30, 2024*"
    #     }
    # ]
    # }
    response_data = {
        "team_name": team_name,
        "summary":summary.get('summary', 'No summary available'),
        "audio_base64": f"data:audio/wav;base64,{encoded_audio}"  # Base64-encoded audio file
    }
    return JSONResponse(content=response_data)


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