from data_loading import WhoopDB
from data_wrangling import DataWrangler
import logging
from logging_config import setup_logging
import pandas as pd

#TODO: 
# - Ensure conversion to local time is correct
# - Add Error Handling and Docstrings to all functions



setup_logging()
logger = logging.getLogger(__name__)


def pre_process_data():
    db = WhoopDB()
    logger.info("Database connection established successfully.")

    df_initial_data = db.load_initial_whoop_data()
    logger.info("Data loaded successfully. Number of records: %d", len(df_initial_data))
    
    wrangler = DataWrangler(df_initial_data)
    
    df_processed = wrangler.convert_millis_to_hours()
    logger.info("milliseconds to hours conversion completed successfully.")
    
    df_processed = wrangler.create_total_sleep_time_hours()
    logger.info("Total sleep time hours created successfully.")

    df_processed = wrangler.handle_missing_values()
    logger.info("Missing values handled successfully.")

    df_processed = wrangler.convert_to_local_time()
    logger.info("Timestamps converted to local time successfully.")
    print(df_processed[['sleep_start_local', 'sleep_end_local']].tail())

if __name__ == "__main__":
    pre_process_data()