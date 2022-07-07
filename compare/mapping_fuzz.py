# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 16:32:51 2022

@author: User
"""

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
import sys

import difflib

adress = 'C:/Users/User/OneDrive - 銘傳大學 - Ming Chuan University/實價登陸/House_Project/'
sys.path.append(adress)
from eval import simple_evaluate,evaluate_partitions,default_partitions

TRAIN_DATA_PATH = adress + 'output_feature/clean_data_all_add_variable_train.csv'
TEST_DATA_PATH = adress + 'output_feature/clean_data_all_add_variable_test.csv'

raw_data = pd.read_csv(TRAIN_DATA_PATH ,dtype = 'str')
raw_data_test = pd.read_csv(TEST_DATA_PATH ,dtype = 'str')

use_column = ['Place_id','Type','Transfer_Total_Ping','Building_Types','Month','house_age','min_floors_height']

#raw_data = raw_data[use_column]
#raw_data_test =raw_data_test[use_column]

raw_data['combine'] = raw_data[use_column].apply(''.join,axis =1)
raw_data_test['combine'] = raw_data_test[use_column].apply(''.join,axis =1)

pd.concat([raw_data,raw_data_test]).to_csv(adress + '/code/compare_index.csv',index = False)

def compare_value('Place_id','Type','Transfer_Total_Ping','Building_Types','Month','house_age','min_floors_height')






# 1:14
import datetime as dt
d1 = dt.datetime.now()
difflib.get_close_matches(raw_data_test.query("Place_id=='613'")['combine'].iloc[0], raw_data.query("Place_id=='613'")['combine'])[0]
print(dt.datetime.now()-d1)

# 4:14
d1 = dt.datetime.now()
process.extract(raw_data_test['combine'][0], raw_data['combine'].tolist(),limit=2)
print(dt.datetime.now()-d1)


# 4:30
def minDistance(word1: str, word2: str):
    '編輯距離的計算函數'
    n = len(word1)
    m = len(word2)
    # 有一個字串為空串
    if n * m == 0:
        return n + m
    # DP 陣列
    D = [[0] * (m + 1) for _ in range(n + 1)]
    # 邊界狀態初始化
    for i in range(n + 1):
        D[i][0] = i
    for j in range(m + 1):
        D[0][j] = j
    # 計算所有 DP 值
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            left = D[i - 1][j] + 1
            down = D[i][j - 1] + 1
            left_down = D[i - 1][j - 1]
            if word1[i - 1] != word2[j - 1]:
                left_down += 1
            D[i][j] = min(left, down, left_down)
    return D[n][m]

import datetime as dt
d1 = dt.datetime.now()
raw_data['combine'].apply(lambda user: minDistance(user, raw_data_test['combine'][0]))
print(dt.datetime.now()-d1)

# 找不到資料
import re
def fuzzyfinder(user_input, collection):
	suggestions = []
	pattern = '.*?'.join(user_input)	# Converts ‘djm‘ to ‘d.*?j.*?m‘
	regex = re.compile(pattern)		 # Compiles a regex.
	for item in collection:
		match = regex.search(item)	  # Checks if the current item matches the regex.
		if match:
			suggestions.append((len(match.group()), match.start(), item))
	return [x for _, _, x in sorted(suggestions)]

fuzzyfinder(raw_data_test['combine'][0], raw_data['combine'])

# 4:53
d1 = dt.datetime.now()
process.extractOne(raw_data_test['combine'][0], raw_data['combine'])
print(dt.datetime.now()-d1)