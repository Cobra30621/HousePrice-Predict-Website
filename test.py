import pandas as pd
import numpy as np
from sklearn.utils import shuffle



# 研究欄位








# 研究檔案大小


import pandas as pd
import numpy as np
from sklearn.utils import shuffle


# 原本資料 289 MB 
compare_data = pd.read_csv('compare/compare_index.csv')

# 1. 去除用不到欄位 220 MB 
drop_columns = ['area_m2', 'manager', 'Total_price',
    'including_basement', 'including_arcade', 'Main_Usage_Walk',
   'Main_Usage_Living', 'Main_Usage_Selling', 'Main_Usage_Manufacturing',
   'Main_Usage_Parking', 'Main_Usage_SnE', 'Main_Usage_Farm',
   'Building_Material_stone',  'Non_City_Land_Usage',
   'Unit_Price_Ping']
compare_data = compare_data.drop(columns=drop_columns)


# 2. 將資料變45%，99.6MB
compare_data = shuffle(compare_data)
row_count = int(0.45 * len(compare_data))
compare_data_small = compare_data[:row_count]

compare_data_small.to_csv('compare/compare_index_small.csv',index=False)


check = compare_data['Parking_Area'].value_counts()


# 研究input問題

from model import  ModelManager

model = ModelManager()

input1 =  pd.read_csv('csv/input.csv')
input2 =  pd.read_csv('csv/input_2.csv')

input1 = input1.drop(columns = ["Unnamed: 0"])
input2 = input2.drop(columns = ["Unnamed: 0"])

input5 = input2[['Place_id', 'Type', 'area_ping', 'Month', 'house_age', 'room', 'hall',
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

input3 = input1.append(input2)
input4 = input2.append(input1)

model.test_predict(input1 )
model.test_predict(input2)
model.test_predict(input3)
model.test_predict(input4)
model.test_predict(input5)


output = input1
output = output.append(input2)

output2 = output[output["Place_id"] == 105]


input1.dtypes
input2.dtypes
