import joblib
import pandas as pd
import numpy as np
# from sqlalchemy import false
import streamlit as st
import geopandas as gpd
import json
import datetime

class ModelManager():
    def __init__(self):
        self.model_path = "model/" + "LGBM_0704"
        self.gbm_Flag_weight = self.loadModel(self.model_path  + '/model.pkl')
    
    def create_json_file(self):

        self.default_data = pd.read_csv(self.model_path + '/test.csv') 
        # http://json.parser.online.fr/
        
    # @st.cache # 建立快取
    def loadModel(self, model_path):
        print("ModelManager load model:" + model_path)
        return joblib.load(model_path)

    def predict(self, data, **kwargs):
        for key, value in kwargs.items():
            data.loc[0, key] = value
        
        y_pred_test = self.gbm_Flag_weight.predict(data, num_iteration=self.gbm_Flag_weight.best_iteration)
        
        return y_pred_test[0]


    def predict(self, **kwargs):
        for key, value in kwargs.items():
            self.default_data.loc[0, key] = value

        y_pred_test = self.gbm_Flag_weight.predict(self.default_data, num_iteration=self.gbm_Flag_weight.best_iteration)
        
        return y_pred_test[0]

    def predict_by_place(self, raw_data, place_df):
    
        data = raw_data[0:0]

        for place_id in place_df["Place_id"]:
            raw_data["Place_id"][0] = int(place_id)
            data = data.append(raw_data.iloc[[0]] , ignore_index=True)


        y_pred_test = self.gbm_Flag_weight.predict(data, num_iteration=self.gbm_Flag_weight.best_iteration)
        # print(y_pred_test)
        df = place_df
        df["price"] = y_pred_test.astype(int)
        df["price_"] = df.apply(lambda x : format(x["price"], ','), axis=1 )
        df["price_wan"] = df.apply(lambda x : round(x["price"] / 10000) , axis=1 )
        return df


    def number_2_wan(self, number):
        return round(number / 10000)




