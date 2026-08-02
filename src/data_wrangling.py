from . import config
import pandas as pd


class DataWrangler():
    def __init__(self, df):
        self.df = df

    def convert_millis_to_hours(self):
        """Converts specified columns from milliseconds to hours and drops the original millisecond columns.
        Returns:
            pd.DataFrame: DataFrame with specified columns converted to hours and original millisecond columns dropped.
            """
        for col in config.MILLI_TO_HOURS_COLUMNS:
            if col in self.df.columns:
                self.df[col.replace("_milli", "_hours")] = self.df[col] / (1000 * 60 * 60)
                self.df.drop(columns=[col], inplace=True)
        return self.df
    
    
    def create_total_sleep_time_hours(self):
        """Creates a new column 'total_sleep_time_hours' by summing the individual sleep stage duration columns in hours.
        Returns:
            pd.DataFrame: DataFrame with the new 'total_sleep_time_hours' column."""
        self.df["total_sleep_time_hours"] = self.df["total_light_sleep_time_hours"] + self.df["total_slow_wave_sleep_time_hours"] + self.df["total_rem_sleep_time_hours"]
        return self.df

    
    # def handle_missing_values(self):
    #     """
    #     Handles missing values in the DataFrame by filling numeric columns with the median and categorical columns with the mode.
    #     """
    #     for col in self.df.columns:
    #         if self.df[col].isnull().sum() > 0:
    #             if self.df[col].dtype in ['float64', 'int64']:
    #                 self.df[col] = self.df[col].fillna(self.df[col].median())
    #             else:
    #                 self.df[col] = self.df[col].fillna(self.df[col].mode()[0])


    def convert_to_local_time(self, cols:list, timezone_col:str = "timezone_offset"):
        """Converts specified UTC timestamp columns to local time using the provided timezone offset column. The converted local time is stored in new columns with a '_local' suffix.
        Args:
            cols (list): List of column names containing UTC timestamps to be converted.
            timezone_col (str): Name of the column containing timezone offsets in minutes. Default is 'timezone_offset'.
        Returns:
            pd.DataFrame: DataFrame with new columns for local time.
        """
        for col in cols:
            if col in self.df.columns:
                self.df[f"{col}_local"] = pd.to_datetime(self.df[col]) + pd.to_timedelta(self.df[timezone_col], unit='m')
        return self.df
