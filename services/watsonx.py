import requests
from core.logger import logger


class Watsonx:
    def __init__(self, api_key, url, version):
        self.api_key = api_key
        self.url = url
        self.version = version

    def summarize_text(self, text):
        """
        Summarize text using IBM Watson Natural Language Understanding service.
        """
        url = f"{self.base_url}/v1/summarize"
        payload = {
            "text": text,
            "features": {
                "summarization": {}
            }
        }
        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
        #logger.info("Summarizing text")
        #return "This is a summarized text"
    
    def generate_action_items(self, text, users):
        logger.info("Generating action items")
        return "This is a list of action items"

    def generate_emails(self, text, users):
        logger.info("Generating emails")
        return "This is a list of emails"
    
    def parse_audio(self, audio_file):
        """
        Transcribe audio content to text using IBM Watson Speech to Text service.
        """
        url = f"{self.base_url}/v1/recognize"
        response = requests.post(
            url,
            headers=self.headers,
            files={"audio": ("audio.wav", audio_file, "audio/wav")},
            params={"model": "en-US_BroadbandModel"}
        )
        response.raise_for_status()
        return response.json()

        #logger.info("Parsing audio file")
        #return "This is a parsed audio file"