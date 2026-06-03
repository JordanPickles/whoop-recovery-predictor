from pydantic_settings import BaseSettings
from pathlib import Path
import os
import json
from typing import Optional

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
TOKENS_JSON_PATH = Path(__file__).resolve().parents[2] / ".secrets/tokens.json"

class Settings(BaseSettings):
    db_user:str
    db_password:str
    db_host:str
    db_port:str
    db_name:str


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    # ── Millisecond columns to convert to hours ──────────────────────────


settings = Settings()

MILLI_TO_HOURS_COLUMNS = [
    "total_in_bed_time_milli",
    "total_awake_time_milli",
    "total_light_sleep_time_milli",
    "total_slow_wave_sleep_time_milli",
    "total_rem_sleep_time_milli"
]