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
        # 調整欄位順序
        data = raw_data[['Place_id', 'Type', 'area_ping', 'Month', 'house_age', 'room', 'hall',
            'bathroom', 'compartment', 'main_area', 'trading_floors_count',
            'building_total_floors', 'min_floors_height', 'City_Land_Usage',
            'Parking_Area', 'Main_Usage_Business', 'Building_Material_S',
            'Building_Material_R', 'Building_Material_C', 'Building_Material_steel',
            'Building_Material_B', 'Building_Material_W', 'Building_Material_iron',
            'Building_Material_tile', 'Building_Material_clay',
            'Building_Material_RC_reinforce', 'Non_City_Land_Code',
            'Transaction_Land', 'Transaction_Building', 'Transaction_Parking',
            'Note_Null', 'Note_Additions', 'Note_Presold', 'Note_Relationships',
            'Note_Balcony', 'Note_PublicUtilities', 'Note_PartRegister',
            'Note_Negotiate', 'Note_Parking', 'Note_OnlyParking', 'Note_Gov',
            'Note_Overbuild', 'Note_Decoration', 'Note_Furniture', 'Note_Layer',
            'Note_BuildWithLandholder', 'Note_BlankHouse', 'Note_Defect',
            'Note_Debt', 'Note_Elevator', 'Note_Renewal', 'Note_DistressSale_',
            'Note_OverdueInherit', 'Note_DeformedLand', 'Parking_Space_Types',
            'Building_Types', 'Transfer_Total_Ping']]

        data = data[0:0]

        for place_id in place_df["Place_id"]:
            raw_data["Place_id"][0] = int(place_id)
            data = data.append(raw_data.iloc[[0]] , ignore_index=True)
        data.to_csv("csv/input_2.csv")

        y_pred_test = self.gbm_Flag_weight.predict(data, num_iteration=self.gbm_Flag_weight.best_iteration)
        # print(y_pred_test)
        df = place_df
        df["price"] = y_pred_test.astype(int)
        df["price_"] = df.apply(lambda x : format(x["price"], ','), axis=1 )
        df["price_wan"] = df.apply(lambda x : round(x["price"] / 10000) , axis=1 )
        return df

    def test_predict(self, data):
        y_pred_test = self.gbm_Flag_weight.predict(data, num_iteration=self.gbm_Flag_weight.best_iteration)
        # print(y_pred_test)
        df = data
        df["price"] = y_pred_test.astype(int)
        df["price_"] = df.apply(lambda x : format(x["price"], ','), axis=1 )
        df["price_wan"] = df.apply(lambda x : round(x["price"] / 10000) , axis=1 )

        return df


    def number_2_wan(self, number):
        return round(number / 10000)




