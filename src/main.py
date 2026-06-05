from data_loading import WhoopDB
from data_wrangling import DataWrangler
from feature_engineering import FeatureEngineer
import logging
from logging_config import setup_logging
import pandas as pd
import time
import config

#TODO: 

# - Add Error Handling and Docstrings to all functions

setup_logging()
logger = logging.getLogger(__name__)

class DataPipeline():
    def __init__(self):
        self.db = WhoopDB()
        logger.info("Database connection established successfully.")

    def pre_process_data(self) -> pd.DataFrame:
        df_initial_data = self.db.load_initial_whoop_data()
        logger.info("Data loaded successfully. Number of records: %d", len(df_initial_data))
        
        wrangler = DataWrangler(df_initial_data)
        
        df_processed = wrangler.convert_millis_to_hours()
        logger.info("milliseconds to hours conversion completed successfully.")
        
        df_processed = wrangler.create_total_sleep_time_hours()
        logger.info("Total sleep time hours created successfully.")

        df_processed = wrangler.handle_missing_values()
        logger.info("Missing values handled successfully.")

        df_processed = wrangler.convert_to_local_time(['sleep_start', 'sleep_end', 'date'])
        logger.info("Local Timestamps converted into new columns successfully.")
        return df_processed
    


    def feature_engineering(self, df_processed:pd.DataFrame) -> pd.DataFrame:
        engineer = FeatureEngineer(df_processed)
        df_engineered = engineer.create_rolling_averages(cols=['hrv_rmssd_milli', 'resting_heart_rate','cycle_strain'], window=7)
        logger.info("Rolling averages created successfully.")

        df_engineered = engineer.create_day_of_week(date_col='date_local')
        logger.info("Day of week feature created successfully.")
        
        df_engineered = engineer.create_anomalous_day_flag(recovery_score_col='recovery_score', recovery_threshold=config.RED_RECOVERY_SCORE_THRESHOLD, hrv_threshold=config.HRV_SURPRESSION_LEVEL)
        logger.info("Anomalous day flag created successfully.")

        df_engineered = engineer.create_sleep_decimal_score(col_sleep_start='sleep_start_local', col_sleep_end='sleep_end_local')
        logger.info("Sleep decimal score created successfully.")
        return df_engineered

        #TODO - Add sleep consistency score feature engineering step here and update the create_sleep_matrix and calculate_jaccard_similarity functions to take in the necessary data for the sleep consistency score calculation.


if __name__ == "__main__":
    pipeline = DataPipeline()
    df_processed = pipeline.pre_process_data()
    df_engineered = pipeline.feature_engineering(df_processed)
    print(df_engineered.tail())