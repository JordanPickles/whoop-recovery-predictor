import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from sqlalchemy.orm import sessionmaker

from config import settings 



class WhoopDB():
    def __init__(self):
        self.db_url = f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}?sslmode=require"
        self.engine = create_engine(self.db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.SessionLocal()
        self.connection = self.engine.connect()

    def load_raw_data(self, query: str) -> pd.DataFrame:
        """Executes a SQL query and returns the results as a pandas DataFrame.
        Args:
            query (str): The SQL query to be executed.
        Returns:
            pd.DataFrame: DataFrame containing the results of the SQL query.
        """       
        
        try:
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def load_initial_whoop_data(self) -> pd.DataFrame:
        """Loads Whoop data using the predefined SQL query.
        Returns:
            pd.DataFrame: DataFrame containing the initial Whoop data loaded from the database.
        """
        query_text ="""SELECT 
            -- identifiers
            R.cycle_id
            , R.created_at  AS date

            -- recovery score
            , R.recovery_score

            -- physiological signals
            , R.resting_heart_rate
            , R.hrv_rmssd_milli
            , R.spo2_percentage
            , R.skin_temp_celsius

            -- sleep timing
            , S.start AS sleep_start
            , S.end AS sleep_end
            , S.timezone_offset

            -- raw sleep stage millis (convert to hours in Python)
            , S.total_in_bed_time_milli
            , S.total_awake_time_milli
            , S.total_light_sleep_time_milli
            , S.total_slow_wave_sleep_time_milli
            , S.total_rem_sleep_time_milli

            -- sleep quality metrics
            , S.sleep_efficiency_percentage
            , S.sleep_consistency_percentage
            , S.sleep_performance_percentage
            , S.respiratory_rate
            , S.sleep_cycle_count
            , S.disturbance_count

            -- sleep debt
            , S.sleep_needed_baseline_milli
            , S.sleep_needed_need_from_recent_strain_milli

            -- daily strain
            , C.strain AS cycle_strain
            , C.average_heart_rate AS cycle_avg_heart_rate
            , C.max_heart_rate AS cycle_max_heart_rate
            , C.kilojoule AS cycle_kilojoule

        FROM 
            fact_recovery R
        LEFT JOIN 
            fact_activity_sleep S 
            ON R.sleep_id = S.sleep_id
        LEFT JOIN 
            fact_cycle C 
            ON R.cycle_id = C.cycle_id

        WHERE 
            1=1
            AND S.nap = FALSE
            AND S.total_no_data_time_milli < 0.1

        ORDER BY R.created_at ASC
            """
        return self.load_raw_data(query_text)
        

if __name__ == "__main__":
    data = WhoopDB().load_raw_data(query_text)
    print(data.head())