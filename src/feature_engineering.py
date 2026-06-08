import pandas as pd
import numpy as np
import config
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

    def create_anomalous_day_flag(self, recovery_score_col:str, recovery_threshold:int, hrv_threshold:float) -> pd.DataFrame:
        """Creates a new binary column 'anomalous_day_flag' that indicates whether the recovery score for a given day is below a specified threshold.
        Args:
            recovery_score_col (str): The name of the column containing recovery scores.
            recovery_threshold (int): The threshold value below which a day is considered anomalous.
            hrv_threshold (float): The threshold value for HRV suppression.
        Returns:
            pd.DataFrame: DataFrame with the new 'anomalous_day_flag' column."""
        
        try:
            hrv_median = self.df['hrv_rmssd_milli'].median() # median is more robust to the outliers we know are present
            low_hrv_threshold = hrv_median * hrv_threshold # more conservative requiring the larger decrease based on the study of 33% decrease 
            self.df['alcohol_consumed_flag'] = ((self.df['recovery_score'] < recovery_threshold) & (self.df['hrv_rmssd_milli'] < low_hrv_threshold)).astype(int)
        except Exception as e:
            print(f"Error creating anomalous_day_flag feature: {e}")
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

    def return_n_day_rolling_window_rows(self, date_col:str, day_window:int, date:pd.Timestamp) -> pd.DataFrame:
        """Returns the rows for the specified number of days rolling window.
        Args:
            date_col (str): The name of the column containing dates.
            day_window (int): The number of days to include in the rolling window.
            start_date (pd.Timestamp): The starting date for the rolling window.
        Returns:
            pd.DataFrame: DataFrame with the rows for the rolling window."""
        
        start_date = date.date() - pd.Timedelta(days=day_window)
        return self.df[(self.df[date_col].dt.date > start_date) & (self.df[date_col].dt.date <= date.date())]

    def recreate_sleep_consistency_score(self, col_sleep_start:str, col_sleep_end:str, day_minutes:int, day_window:int) -> pd.DataFrame:
        """Recreates the sleep consistency score by using Jacard similarity to compare the sleep periods of each day to a rolling window of previous days. The sleep periods are represented as binary vectors indicating whether the user was asleep during each minute of the day.
        Args:
            col_sleep_start (str): The name of the column containing sleep start times in decimal
            col_sleep_end (str): The name of the column containing sleep end times in decimal
            day_minutes (int): The number of minutes in a day.
            day_window (int): The window size for calculating the standard deviation.
        Returns:
            pd.DataFrame: DataFrame with the new 'sleep_consistency_score' column."""

        try:
            for date in self.df['date_local'].unique():
                df_sleep_consistency_window = self.return_n_day_rolling_window_rows('date_local', day_window, date)
                n_days = len(df_sleep_consistency_window)
                try:
                    if n_days != day_window: # Not enough previous days to calculate consistency score so loop exit
                        consistency = np.nan
                    else:
                        sleep_matrix = self.create_sleep_matrix(day_minutes, n_days, df_sleep_consistency_window, col_sleep_start, col_sleep_end)
                        consistency = self.calculate_jaccard_similarity(sleep_matrix, n_days)

                    self.df.loc[self.df['date_local'] == date, 'sleep_consistency_percentage_recalculated'] = consistency
                except Exception as e:
                    print(f"Error recreating sleep on {self.df['date_local']}: {e}")

        except Exception as e:
            print(F"Error Recreating Sleep Score: {e}")
        return self.df

    def create_sleep_matrix(self, day_minutes: int, n_days: int, df_sleep_consistency_window: pd.DataFrame, col_sleep_start:str, col_sleep_end:str) -> np.ndarray:
        minutes = np.arange(day_minutes)/ 60 # decmimal hours in a day

        sleep_matrix = np.zeros((n_days, len(minutes)), dtype=bool)
        for i, (start, end) in enumerate(zip(
            df_sleep_consistency_window[f"{col_sleep_start}_decimal"], 
            df_sleep_consistency_window[f"{col_sleep_end}_decimal"]
            )):
            start_normalised = start % 24 # Normalise to 0-24 range
            end_normalised = end % 24
        
            if end_normalised < start_normalised: # Sleep window crosses midnight (typical)
                sleep_matrix[i, (minutes >= start_normalised) | (minutes < end_normalised)] = 1  
            else:
                sleep_matrix[i, (minutes >= start_normalised) & (minutes < end_normalised)] = 1 
        return sleep_matrix
    
    def calculate_jaccard_similarity(self, sleep_matrix: np.ndarray, n_days: int) -> float:
        scores = []
        for i in range(n_days):
            for j in range(i + 1, n_days):
                intersection = (sleep_matrix[i] & sleep_matrix[j]).sum()
                union = (sleep_matrix[i] | sleep_matrix[j]).sum()
                if union > 0:
                    scores.append(intersection / union)

        consistency = round(np.mean(scores) * 100, 1) if scores else 0.0
        return consistency