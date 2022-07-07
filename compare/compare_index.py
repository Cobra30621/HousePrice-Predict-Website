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
    # def __init__(self):
    #     # self.compare_data = pd.read_csv( 'compare/compare_index.csv',dtype = 'str')
    #     self.compare_data_right_type = pd.read_csv( 'compare/compare_index.csv')
    #     # self.compare_data_right_type['combine'] = self.compare_data_right_type['combine'].astype(str)

    def __init__(self, compare_data):
        self.compare_data_right_type = compare_data
        

    def compare_value_2(self, Place_id,Transfer_Total_Ping,Building_Types):

        
        data_len = 0
        had_find = False

        # 第一次尋找: 條件 Place_id == @Place_id and Building_Types == @Building_Types
        print("第一次尋找: 條件 Place_id == @Place_id and Building_Types == @Building_Types")
        Transfer_Total_Ping_Range = 0.05
        Transfer_Total_Ping_Range_add = 0.05
        Transfer_Total_Ping_Range_max = 1
        while((data_len == 0) & (Transfer_Total_Ping_Range < Transfer_Total_Ping_Range_max)):

            # Place_id & Building_Types'
            filter_data = self.compare_data_right_type
            filter_data = filter_data.query("Place_id == @Place_id and Building_Types == @Building_Types")

            # Transfer_Total_Ping
            min_total_Ping = Transfer_Total_Ping * (1 - Transfer_Total_Ping_Range)
            max_total_Ping = Transfer_Total_Ping * (1 + Transfer_Total_Ping_Range)
            filter_data = filter_data.query("Transfer_Total_Ping > @min_total_Ping and Transfer_Total_Ping < @max_total_Ping")

            data_len = len(filter_data)
            if(data_len > 0):
                had_find = True
            
            print("坪數Range{}".format(Transfer_Total_Ping_Range - Transfer_Total_Ping_Range_add))
            Transfer_Total_Ping_Range += Transfer_Total_Ping_Range_add

        if(had_find):
            return filter_data.reset_index(drop = True)[0:1]

        # 第二次尋找: 條件 Place_id == @Place_id
        print("第二次尋找: 條件 Place_id == @Place_id")
        data_len = 0
        Transfer_Total_Ping_Range = 0.05
        Transfer_Total_Ping_Range_add = 0.05
        Transfer_Total_Ping_Range_max = 1
        while((data_len == 0) & (Transfer_Total_Ping_Range < Transfer_Total_Ping_Range_max)):

            # Place_id
            filter_data = self.compare_data_right_type
            filter_data = filter_data.query("Place_id == @Place_id")

            # Transfer_Total_Ping
            min_total_Ping = Transfer_Total_Ping * (1 - Transfer_Total_Ping_Range)
            max_total_Ping = Transfer_Total_Ping * (1 + Transfer_Total_Ping_Range)
            filter_data = filter_data.query("Transfer_Total_Ping > @min_total_Ping and Transfer_Total_Ping < @max_total_Ping")

            data_len = len(filter_data)
            if(data_len > 0):
                had_find = True
            
            print("坪數Range{}".format(Transfer_Total_Ping_Range - Transfer_Total_Ping_Range_add))
            Transfer_Total_Ping_Range += Transfer_Total_Ping_Range_add

        if(had_find):
            return filter_data.reset_index(drop = True)[0:1]

        # 第三次尋找 : 隨便給了
        print("第三次尋找 : 隨便給")
        return self.compare_data_right_type.reset_index(drop = True)[0:1]
        


      
    def get_compare_columns(self):
        return self.compare_data_right_type.columns

    # def compare_value(self, Place_id,Type,Transfer_Total_Ping,Building_Types,Month,house_age,min_floors_height):
        
    #     test = pd.DataFrame({
    #         'Place_id': Place_id,
    #         'Type': Type,
    #         'Transfer_Total_Ping':Transfer_Total_Ping,
    #         'Building_Types':Building_Types,
    #         'Month':Month,
    #         'house_age':house_age,
    #         'min_floors_height':min_floors_height
    #         },index = ['0'])
        
    #     test['combine'] =  test.apply(''.join,axis =1)
        
    #     print(test.apply(''.join,axis =1))
        
    #     filter_data = self.compare_data.query("Place_id == @Place_id and Type == @Type and Building_Types == @Building_Types ")

    #     compare_output_list = difflib.get_close_matches(test['combine'].iloc[0], filter_data['combine'])
    #     compare_output = compare_output_list[0]

    #     return compare_output, self.compare_data_right_type.query("combine == @compare_output")
    
    def test(self):
   
        test = self.compare_data.iloc[1]
        print("1")
        print(test)
        compare_output ,output = self.compare_value(test['Place_id'], test['Type'], test['Transfer_Total_Ping'], test['Building_Types'], test['Month'], test['house_age'], test['min_floors_height'])
        # print('compare_output')
        # print(compare_output)
        # print('output')
        # print(output)