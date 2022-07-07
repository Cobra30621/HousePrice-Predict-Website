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
        print(self.default_data.to_json(orient='index')) 
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


# 將使用者輸入資料，轉成模型所需資料
class DataPreprocessor():
    def __init__(self):
        self.place_df = pd.read_csv('csv/place_id.csv')
        self.building_type_df = pd.read_csv('csv/building_type.csv')
        self.type_df = pd.read_csv('csv/type.csv')
        self.gdf = gpd.read_file('taiwan_map/TOWN_MOI_1100415.shp', encoding='utf-8')
        self.gdf['place'] = self.gdf['COUNTYNAME'] + self.gdf['TOWNNAME']
        print('self.gdf')
        print(self.gdf)
        print(self.gdf['place'])
        print('self.place_df')
        print(self.place_df)

        self.gdf = pd.merge(self.gdf, self.place_df, on ="place")
        self.city_list = ['臺北市', '新北市', '基隆市', '桃園市', '新竹縣', 
            '宜蘭縣', '苗栗縣', '臺中市', '彰化縣', '雲林縣', '嘉義縣', 
            '臺南市', '高雄市', '屏東縣', '臺東縣', '花蓮縣', '南投縣',    
            '澎湖縣', '連江縣', '金門縣' ]


    def get_place_id(self, city, district):
        return self.place_df[self.place_df['place'] == city + district]\
            .reset_index()['Place_id'][0]

    def get_place_id(self, palce):
        return self.place_df[self.place_df['place'] == palce].reset_index()['Place_id'][0]

    def get_city_list(self):
        return self.city_list

    def get_district_list(self, city_list):
        return self.gdf['TOWNNAME'][self.gdf['COUNTYNAME'].isin(city_list)].unique()

    def get_place_list_by_city_list(self, city_list):
        return self.gdf['place'][self.gdf['COUNTYNAME'].isin(city_list)].unique()

    def get_place_list(self):
        return self.place_df['place']

    def get_building_type_list(self):
        return self.building_type_df['type']

    def get_building_type_id(self, type):
        return self.building_type_df[self.building_type_df['type'] == type].reset_index()['type_id'][0]

    def get_type_list(self):
        return self.type_df['type']

    def get_type_id(self, type):
        return self.type_df[self.type_df['type'] == type].reset_index()['type_id'][0]

    def get_month_list(self):
        datetime.date.today()

    def get_gdf(self):
        return self.gdf

    def get_gdf_by_city(self, city_list):
        return self.gdf [self.gdf["COUNTYNAME"].isin(city_list)]
    
    def get_economy_indicators(self, date):
        print(date)





