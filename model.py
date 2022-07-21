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
        self.total_Price_model = self.loadModel(self.model_path  + '/model.pkl')

        self.use_unit_model = False


        if(self.use_unit_model):
            self.model_path = "model/" + "LGBM_0704"
            self.unit_Price_model = self.loadModel(self.model_path  + '/unit_model.pkl')
    
    def __init__(self, total_model, unit_model, use_unit_model):
        self.total_Price_model = total_model

        self.use_unit_model = use_unit_model
        self.unit_model = unit_model

    def __init__(self, total_model, use_unit_model):
        self.total_Price_model = total_model

        self.use_unit_model = use_unit_model



    @st.cache
    def loadModel(self, model_path):
        return joblib.load(model_path)

    # 調整欄位順序
    def correct_columns_order(self, raw_data):
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

        return data

    def predict(self, raw_data):
        data = self.correct_columns_order(raw_data)
        df = data
        
        
        Total_Price_predict = self.total_Price_model.predict(data, num_iteration=self.total_Price_model.best_iteration)
        if(self.use_unit_model):
            Unit_Price_predict = self.unit_Price_model.predict(data, num_iteration=self.unit_Price_model.best_iteration)
        
        # Total_Price
        df["price"] = Total_Price_predict.astype(int)
        df["price_wan"] = df.apply(lambda x : round(x["price"] / 10000) , axis=1 )

        if(self.use_unit_model):
            # Unit_Price
            df["unit_price"] = Unit_Price_predict.astype(int)
            df["unit_price_wan"] = df.apply(lambda x : round(x["unit_price"] / 10000) , axis=1 )
        else:
            Transfer_Total_Ping = data["Transfer_Total_Ping"].iloc[[0]]
            df["unit_price"] = df.apply(lambda x : round( (x["price"] / Transfer_Total_Ping )) , axis=1 )
            df["unit_price_wan"] = df.apply(lambda x : round( (x["price"] / Transfer_Total_Ping )/ 10000) , axis=1 )
        return df

    def predict_by_place(self, raw_data, place_df):
        data = self.correct_columns_order(raw_data)
        data = data[0:0]

        for place_id in place_df["Place_id"]:
            raw_data["Place_id"][0] = int(place_id)
            data = data.append(raw_data.iloc[[0]] , ignore_index=True)

        df = place_df
        # Total_Price
        Total_Price_predict = self.total_Price_model.predict(data, num_iteration=self.total_Price_model.best_iteration)
        df["price"] = Total_Price_predict.astype(int)
        df["price_wan"] = df.apply(lambda x : round(x["price"] / 10000) , axis=1 )

        # Unit_Price
        if(self.use_unit_model):
            Unit_Price_predict = self.unit_Price_model.predict(data, num_iteration=self.unit_Price_model.best_iteration)
            df["unit_price"] = Unit_Price_predict.astype(int)
            df["unit_price_wan"] = df.apply(lambda x : round(x["unit_price"] / 10000) , axis=1 )
        else:
            Transfer_Total_Ping = data["Transfer_Total_Ping"].iloc[[0]]
            df["unit_price"] = df.apply(lambda x : round( (x["price"] / Transfer_Total_Ping )) , axis=1 )
            df["unit_price_wan"] = df.apply(lambda x : round( (x["price"] / Transfer_Total_Ping )/ 10000) , axis=1 )
        return df



