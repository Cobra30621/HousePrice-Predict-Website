# -*- coding: utf-8 -*-
"""
Created on Sun Jul  3 13:04:16 2022

@author: User
"""

import pandas as pd
import sys
import difflib
import streamlit as st

# from eval import simple_evaluatcompare_data_right_typee,evaluate_partitions,default_partitions


class CompareManager:
    def __init__(self, compare_data):
        self.compare_data = compare_data

    # 回傳屋齡的資料區間
    # ex: 19 > 10 ~ 20, 35 > 35 ~ 50, 
    # ex: 0  > -6 ~ 1, 
    # 超過區間，回傳最近的區間
    # ex:-999 > -6 ~ 1, 999 > 60 ~ 100
    def get_house_age_range(self, age):
        house_age_range = [-6, 1, 10, 20, 35, 50, 100]
        length = len(house_age_range)
        for i in range(length - 1):
            if(age < house_age_range[i+1]):
                return house_age_range[i], house_age_range[i+1]
            
         # 超過上限，回傳最後一個區間 ex: 999 > 50 ~ 100
        return house_age_range[length - 2], house_age_range[length - 1]


    # 回傳總坪數的區間
    # ex: 19 > 1 ~ 20 
    # ex: 30 > 30 ~ 40
    # 超過區間，回傳最近的區間
    # ex:-999 > 0 ~ 10, 999 > 50 ~ 100
    def get_Transfer_Total_Ping_range(self, Transfer_Total_Ping):
        Transfer_Total_Ping_range =  [0 , 10.0 , 20.0,  30.0 , 40.0, 50.0 , 100]
        length = len(Transfer_Total_Ping_range)
        
        for i in range(length - 1):
            if(Transfer_Total_Ping < Transfer_Total_Ping_range[i+1]):
                return Transfer_Total_Ping_range[i], Transfer_Total_Ping_range[i+1]
            
        # 超過上限，回傳最後一個區間 ex: 999 > 60 ~ 100
        return Transfer_Total_Ping_range[length - 2], Transfer_Total_Ping_range[length - 1]


    # 比較像似度
    def compare_value(self, filter_data, user_input):
        compare_output =  difflib.get_close_matches(user_input, filter_data['combine'])[0]

        return filter_data.query("combine == @compare_output").drop(columns=['combine']).reset_index(drop=True)


    # 取得最相似的資料
    def get_input_data(self, Place_id, Type, Transfer_Total_Ping, Building_Types, house_age, min_floors_height):

        user_input = str(Place_id) + str(Type) + str(float(Transfer_Total_Ping)) + \
            str(Building_Types) +   str(float(house_age)) + str(float(min_floors_height))   
        filter_data = self.compare_data
        
        # 1. 篩選 Building_Types
        previous_data = filter_data # 紀錄上一個篩選條件資料
        filter_data = filter_data.query("Building_Types == @Building_Types")
        # 如果篩選資料量為0，選上一個篩選條件的資料進行比對
        if(len(filter_data) == 0): 
            return self.compare_value(previous_data, user_input)
            
        
        # 2. 篩選 Transfer_Total_Ping 總坪數
        previous_data = filter_data # 紀錄上一個篩選條件資料
        Total_Ping_start , Total_Ping_end = self.get_Transfer_Total_Ping_range(Transfer_Total_Ping)
        filter_data = filter_data.query("Transfer_Total_Ping >= @Total_Ping_start and \
                                        Transfer_Total_Ping < @Total_Ping_end")
        # 如果篩選資料量為0，選上一個篩選條件的資料進行比對
        if(len(filter_data) == 0): 
            return self.compare_value(previous_data, user_input)
        
        
        # 3. 篩選 Place_id 地區
        previous_data = filter_data # 紀錄上一個篩選條件資料
        filter_data = filter_data.query("Place_id == @Place_id")
        # 如果篩選資料量為0，選上一個篩選條件的資料進行比對
        if(len(filter_data) == 0): 
            return self.compare_value(previous_data, user_input)
        
        
        # 4. 篩選 house_age 屋齡
        previous_data = filter_data # 紀錄上一個篩選條件資料
        house_age_start , house_age_end = self.get_house_age_range(house_age)
        filter_data = filter_data.query("house_age >= @house_age_start and house_age < @house_age_end")
        # 如果篩選資料量為0，選上一個篩選條件的資料進行比對
        if(len(filter_data) == 0): 
            return self.compare_value(previous_data, user_input)

        return self.compare_value(previous_data, user_input)

        
