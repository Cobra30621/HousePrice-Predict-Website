import pandas as pd
import numpy as np
import geopandas as gpd
import json
import datetime

class DataManager():
    def __init__(self, path):
        self.df = pd.read_csv(path)
        self.df['id'] = self.df['id'].astype(int)

    def get_name_list(self):
        return self.df['name']

    def get_id(self, name):
        return self.df[self.df['name'] == name].reset_index()['id'][0]

    def get_name(self, id):        
        return self.df[self.df['id'] == id].reset_index()['name'][0]

# 將使用者輸入資料，轉成模型所需資料
class DataPreprocessor():
    def __init__(self):
        self.place_df = pd.read_csv('csv/place_id.csv')

        self.gdf = gpd.read_file('taiwan_map/TOWN_MOI_1100415.shp', encoding='utf-8')
        self.gdf['place'] = self.gdf['COUNTYNAME'] + self.gdf['TOWNNAME']

        self.gdf = pd.merge(self.gdf, self.place_df, on ="place")
        self.city_list = ['臺北市', '新北市', '基隆市', '桃園市', '新竹縣', 
            '宜蘭縣', '苗栗縣', '臺中市', '彰化縣', '雲林縣', '嘉義縣', 
            '臺南市', '高雄市', '屏東縣', '臺東縣', '花蓮縣', '南投縣',    
            '澎湖縣', '連江縣', '金門縣' ]

    # Place_id 
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


    # gdf
    def get_gdf(self):
        return self.gdf

    def get_gdf_by_city(self, city_list):
        return self.gdf [self.gdf["COUNTYNAME"].isin(city_list)]
    


# 2. Building_Material : 建築材料, Note : 特殊標記
class Option:
    # 建構式
    def __init__(self, variable, name):
        self.variable = variable
        self.name = name
        self.select = 0
        
    def select_option(self, select):
        self.select = select

class Options_Manager:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)
        self.dictionary = {}
        for ind in self.df.index:
            variable = self.df["variable"][ind]
            name = self.df["name"][ind]
            
            option = Option(variable,name)
            self.dictionary[name] = option
            
    def get_list(self):
        return self.df['name']
    
    # 設定選項
    def set_options(self, options):
        # 先全部重製
        for option in self.dictionary.values():
            option.select_option(0)

        # 選擇有在清單中的選項
        for option in options:
            self.dictionary[option].select_option(1)
    
    # 取得選項kwargs
    def get_variable_dic(self, kwargs):
        for key, value in self.dictionary.items():
            kwargs[value.variable] = value.select
        
        return kwargs
    
    # 使用中文名子找到變數名稱
    def get_name_by_variable(self, variable):
        return self.df[self.df["variable"] == variable]["name"].reset_index(drop=True)[0]

    # 取得存檔資料
    def get_save_state(self, input_data):
        options = []
        input_data = input_data[self.df["variable"]]
        for variable in input_data.columns:
            if(input_data[variable][0] == 1):
                name = self.get_name_by_variable(variable)
                options.append(name)
        return options



