import pandas as pd
import numpy as np
from . import config
import time



class FeatureEngineer():
    def __init__(self, df):
        self.df = df

    def create_rolling_averages(self, cols:list, window:int):
        """Creates new columns in the DataFrame for rolling averages of specified columns over a given window size. The new columns are named with the format '{col}_rolling_avg_{window}'.
        Args:
            cols (list): List of column names for which to calculate rolling averages.
            window (int): The window size for calculating the rolling average.
        Returns:
            pd.DataFrame: DataFrame with the new rolling average columns."""
        try:
            self.df = self.df.sort_values(by='date_local')  # Ensure data is sorted by date before creating rolling averages
            for col in cols:
                if col in self.df.columns:
                    self.df[f"{col}_rolling_avg_{window}"] = self.df[col].rolling(window=window).mean()
        except Exception as e:
            print(f"Error creating rolling averages: {e}")
        
        return self.df

    def create_day_of_week(self, date_col:str) -> pd.DataFrame:
        """Creates a new column 'day_of_week' by extracting the day of the week from a specified date column.
        Args:
            date_col (str): The name of the date column from which to extract the day of the week.
        Returns:
            pd.DataFrame: DataFrame with the new 'day_of_week' as a numerical value column."""
        try:
            self.df["day_of_week"] = self.df[date_col].dt.dayofweek
        except Exception as e:
            print(f"Error creating day_of_week feature: {e}, now converting {date_col} to datetime and retrying.")
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.df["day_of_week"] = self.df[date_col].dt.dayofweek
        except Exception as e:
            raise ValueError(f"Failed to create day_of_week feature after retrying with datetime conversion: {e}")
        return self.df
    
    def create_recovery_shift_score(self) -> pd.DataFrame:
        self.df['recovery_score_shift'] = self.df['recovery_score'].shift(-1)
        return self.df

    
    def create_sleep_decimal_score(self, col_sleep_start:str, col_sleep_end:str) -> pd.DataFrame:
        """Creates new columns for sleep start and end times in decimal format, where times before noon are represented as their hour value and times after midnight are represented as their hour value plus 24.
        Args:
            col_sleep_start (str): The name of the column containing sleep start times.
            col_sleep_end (str): The name of the column containing sleep end times.
        Returns:
            pd.DataFrame: DataFrame with the new decimal sleep time columns."""
        try:
            self.df[f"{col_sleep_start}_decimal"] = pd.to_datetime(self.df[col_sleep_start]).dt.hour + (pd.to_datetime(self.df[col_sleep_start]).dt.minute / 60)
            self.df[f"{col_sleep_start}_decimal"] = np.where(self.df[f"{col_sleep_start}_decimal"] < 12,
                                                                self.df[f"{col_sleep_start}_decimal"] + 24,
                                                                self.df[f"{col_sleep_start}_decimal"]
                                                                )     
            
            self.df[f"{col_sleep_end}_decimal"] = pd.to_datetime(self.df[col_sleep_end]).dt.hour + (pd.to_datetime(self.df[col_sleep_end]).dt.minute / 60)
            self.df[f"{col_sleep_end}_decimal"] = np.add(self.df[f"{col_sleep_end}_decimal"],24)
        except Exception as e:
            print(f"Error creating sleep_decimal_score feature: {e}")
        return self.df

    # def drop_rows_with_na_recovery_shift_score(self) -> pd.DataFrame:
    #     self.df = self.df.dropna(subset=['recovery_score_shift'])
    #     return self.df

    def drop_features(self) -> pd.DataFrame:
        cols_to_drop = [
            'cycle_id', 'date', 'sleep_start', 'sleep_end',
            'timezone_offset', 'sleep_start_local', 'sleep_end_local',
             'total_light_sleep_time_hours',
            'total_awake_time_hours', 'total_slow_wave_sleep_time_hours',
            'spo2_percentage', 'cycle_max_heart_rate',
            
        ]
        self.df = self.df.drop(columns=cols_to_drop)
        return self.df
