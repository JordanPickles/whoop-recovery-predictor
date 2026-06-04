import pandas as pd
import numpy as np
import config




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
        
        self.df = self.df.sort_values(by='date_local')  # Ensure data is sorted by date before creating rolling averages
        for col in cols:
            if col in self.df.columns:
                self.df[f"{col}_rolling_avg_{window}"] = self.df[col].rolling(window=window).mean()
        
        return self.df

    def create_sleep_efficiency(self):
        """Creates a new column 'sleep_efficiency' by calculating the ratio of total sleep time to time in bed.
        Returns:
            pd.DataFrame: DataFrame with the new 'sleep_efficiency' column."""
        self.df["sleep_efficiency"] = self.df["total_sleep_time_hours"] / (self.df["time_in_bed_hours"])
        return self.df
    
