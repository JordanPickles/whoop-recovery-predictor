
import pandas as pd
import numpy as np
import joblib
import config
import shap

class OutputPrediction():
    def __init__(self, df):
        self.df=df
        self.model_path_predict=config.MODEL_PATH_PREDICT
        self.shap_groupings=config.FEATURE_GROUPS

    def predict_recovery_score(self) -> dict:
        """
        Finds Todays row of data points from the df (final row where recovery_score_shift is NaN) and runs inference.
        Returns: -> dict
            recovery_prediction
            shap_group_scores
            prediction_date"""
        
        input_values = self.find_input_values()
        
        prediction_date = pd.Timestamp(input_values['date_local'].values[0]).strftime('%d.%m.%Y')

        input_values_column_list = [col for col in input_values if col not in ['date_local', 'recovery_score_shift']]
        inference_input_values = input_values[input_values_column_list]
        
        model = self.load_model(self.model_path)  

        recovery_prediction = self.run_inference(inference_input_values, model)
        shap_scores = self.calculate_shap_scores(model, inference_input_values)
        shap_group_scores = self.group_shap_values(inference_input_values ,self.shap_groupings, shap_scores)

        dictionary={'recovery_prediction':recovery_prediction, 'shap_group_scores':shap_group_scores, 'prediction_date':prediction_date}
        
        
        return dictionary
    
    def load_model(self, model_path):
        try:
            model = joblib.load(model_path)
        except Exception as e:
            print(f"Model could not be loaded at this time due to {e}")
        return model


    def find_input_values(self) -> pd.DataFrame:
        try:
            input_values=self.df[self.df['recovery_score_shift'].isna()].tail(1)
            if input_values is pd.NA:
                print('No Null Values Found')

        except Exception as e:
            print(f"The input values could not be found at this time due to {e}")
        return input_values

    def run_inference(self, inference_input_values, model) -> int:

        recovery_score_prediction = float(model.predict(inference_input_values)[0])

        return recovery_score_prediction
    
    def calculate_shap_scores(self, model, inference_input_values):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(inference_input_values)
        return shap_values
    
    def group_shap_values(self, inference_input_values, feature_groups, shap_values) -> pd.DataFrame:
        
        shap_df = pd.DataFrame(shap_values, columns=inference_input_values.columns)

        group_shap = {}
        for group, features in feature_groups.items():
            cols = [f for f in features if f in shap_df.columns]
            group_shap[group] = shap_df[cols].sum(axis=1)

        grouped_shap_df = pd.DataFrame(group_shap)


        return grouped_shap_df
