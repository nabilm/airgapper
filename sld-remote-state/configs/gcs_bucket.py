from typing import List
import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    BUCKET: str = os.getenv('GCS_BUCKET_NAME', "sld-remote-state")
    SERVICE_ACCOUNT_JSON: str = os.getenv('SERVICE_ACCOUNT_JSON', None)


settings = Settings()
