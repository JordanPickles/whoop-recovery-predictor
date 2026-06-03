import config
import pandas as pd


class DataWrangler():
    def __init__(self, df):
        self.df = df

    def convert_millis_to_hours(self):
        for col in config.MILLI_TO_HOURS_COLUMNS:
            if col in self.df.columns:
                self.df[col.replace("_milli", "_hours")] = self.df[col] / (1000 * 60 * 60)
                self.df.drop(columns=[col], inplace=True)
        return self.df
    
    def create_total_sleep_time_hours(self):
        self.df["total_sleep_time_hours"] = self.df["total_light_sleep_time_hours"] + self.df["total_slow_wave_sleep_time_hours"] + self.df["total_rem_sleep_time_hours"]
        return self.df
    
    def handle_missing_values(self):
        """
        Handles missing values in the DataFrame by filling numeric columns with the median and categorical columns with the mode.
        """
        for col in self.df.columns:
            if self.df[col].isnull().sum() > 0:
                if self.df[col].dtype in ['float64', 'int64']:
                    self.df[col] = self.df[col].fillna(self.df[col].median())
                else:
                    self.df[col] = self.df[col].fillna(self.df[col].mode()[0])


    def convert_to_local_time(self):
        self.df["sleep_start_local"] = pd.to_datetime(self.df["sleep_start"], unit='ms') + pd.to_timedelta(self.df["timezone_offset"], unit='s')
        self.df["sleep_end_local"] = pd.to_datetime(self.df["sleep_end"], unit='ms') + pd.to_timedelta(self.df["timezone_offset"], unit='s')
        return self.df