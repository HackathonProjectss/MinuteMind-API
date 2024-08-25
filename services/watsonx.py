import requests
from core.logger import logger
from openai import OpenAI
from core.config import settings
from fastapi import UploadFile
import io
from requests.exceptions import ConnectionError, Timeout, RequestException
class Watsonx:
    def __init__(self,token, url, version, project_id):
        self.token = token
        self.project_id = project_id
        self.url = url + '?version=' + version

    def text_generation(
        self,
        input_text: str,
        model_id: str,
        decoding_method: str = "greedy",
        max_new_tokens: int = 200,
        repetition_penalty: float = 1.0,
        hap_enabled: bool = True,
        hap_threshold: float = 0.5
    ):
        """
        Make a request to the IBM WatsonX Text Generation API.

        :param url: The API endpoint URL.
        :param api_key: The authorization API key.
        :param input_text: The input text for generation.
        :param model_id: The model ID to use.
        :param project_id: The project ID to use.
        :param decoding_method: The decoding method to use.
        :param max_new_tokens: The maximum number of tokens to generate.
        :param repetition_penalty: The penalty for repetition.
        :param hap_enabled: Whether HAP moderation is enabled.
        :param hap_threshold: The HAP moderation threshold.
        :return: The generated text from the API response.
        """
        try:
            body = {
                "input": input_text,
                "parameters": {
                    "decoding_method": decoding_method,
                    "max_new_tokens": max_new_tokens,
                    "repetition_penalty": repetition_penalty
                },
                "model_id": model_id,
                "project_id": self.project_id,
                "moderations": {
                    "hap": {
                        "input": {
                            "enabled": hap_enabled,
                            "threshold": hap_threshold,
                            "mask": {
                                "remove_entity_value": True
                            }
                        },
                        "output": {
                            "enabled": hap_enabled,
                            "threshold": hap_threshold,
                            "mask": {
                                "remove_entity_value": True
                            }
                        }
                    }
                }
            }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }

            response = requests.post(self.url, headers=headers, json=body)

            if response.status_code != 200:
                raise Exception(f"Non-200 response: {response.text}")

            data = response.json()
            return data['results'][0]['generated_text']
        except ConnectionError as ce:
            logger.error(f"Connection failed: {ce}")
            raise Exception("Could not connect to the WatsonX API. Please check your network connection and try again.") from ce
        
        except Timeout as te:
            logger.error(f"Request timed out: {te}")
            raise Exception("The request to WatsonX API timed out. Please try again later.") from te
        
        except RequestException as re:
            logger.error(f"Request failed: {re}")
            raise Exception(f"An error occurred while communicating with the WatsonX API: {re}") from re

    async def summarize_text(self, text, model):
        content = f"Summarize Meeting\n\nInput: {text}\n\nOutput:"
        return self.text_generation(input_text=content, model_id=model)
    
    async def generate_action_items(self, text, users, model):
        results = []
        for user in users:
            try:
                prompt = f"Generate a list of action items for the person mentioned below. Each action item should be a specific task and presented in markdown format as a checklist. Ensure that the tasks are clear, actionable, and relevant to the person's role or responsibilities. Person: {user.name}\n\n{text}"
                # this should be an async function
                action_items = self.text_generation(input_text=prompt, model_id=model)
                results.append({"user": user.model_dump(), "action_items": action_items})
            except Exception as e:
                logger.debug(f"Failed to generate action items for {user.name}: {e}")
                results.append({"user": user.model_dump(), "action_items": "None", "error": str(e)})   
        return results
    

    def generate_emails(self, text, users):
        logger.info("Generating emails")
        return "This is a list of emails"

async def authenticate_watsonx(api_key):
    """
    Authenticate with IBM Watson using an API key.
    """
    
    auth_url = 'https://iam.cloud.ibm.com/identity/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey': api_key
    }
    response = requests.post(auth_url, headers=headers, data=data)
    if response.status_code != 200:
        logger.error(response.json())
        response.raise_for_status()
        return None
    token = response.json().get('access_token')
    return token

async def parse_audio(audio: UploadFile):
    try:
        openai = OpenAI()
        openai.api_key = settings.OPENAI_API_KEY
        content = await audio.read()
        file = io.BytesIO(content)
        file.name = audio.filename

        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=file,
            response_format="text"
        )
        return transcription
    except Exception as e:
        logger.error(e)
        raise e