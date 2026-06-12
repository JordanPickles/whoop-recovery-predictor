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

settings = Settings()

# Millisecond columns to convert to hours

MILLI_TO_HOURS_COLUMNS = [
    "total_in_bed_time_milli",
    "total_awake_time_milli",
    "total_light_sleep_time_milli",
    "total_slow_wave_sleep_time_milli",
    "total_rem_sleep_time_milli"
]

# Model location 
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'whoop_recovery_predictor.pkl')

# Shap Feature Grouping
FEATURE_GROUPS = {
    'Physiological': [
        'recovery_score',
        'hrv_rmssd_milli',
        'hrv_rmssd_milli_rolling_avg_7',
        'resting_heart_rate',
        'resting_heart_rate_rolling_avg_7',
        'skin_temp_celsius',
        'respiratory_rate'
    ],
    'Training Load': [
        'cycle_strain',
        'cycle_strain_rolling_avg_7',
        'cycle_avg_heart_rate',
        'cycle_kilojoule',
        'day_of_week'
    ],
    'Sleep': [
        'total_sleep_time_hours',
        'total_rem_sleep_time_hours',
        'total_in_bed_time_hours',
        'sleep_efficiency_percentage',
        'sleep_performance_percentage',
        'sleep_consistency_percentage',
        'sleep_start_local_decimal',
        'sleep_end_local_decimal',
        'disturbance_count',
        'sleep_needed_need_from_recent_strain_milli'
    ]
}