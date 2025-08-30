import os
import requests
from dotenv import load_dotenv

load_dotenv()

class BHIVClient:
    def __init__(self):
        self.bucket_path = os.getenv('BHIV_BUCKET_PATH')
        self.lm_url = os.getenv('BHIV_LM_URL')
        self.api_key = os.getenv('BHIV_LM_API_KEY')
    
    def upload_to_bucket(self, file_path, bucket_key):
        if not self.bucket_path:
            return None
        return f"{self.bucket_path}/{bucket_key}"
    
    def call_language_model(self, prompt):
        if not self.lm_url or not self.api_key:
            return None
        try:
            response = requests.post(
                self.lm_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"prompt": prompt}
            )
            return response.json()
        except:
            return None
