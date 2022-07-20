import pandas as pd
import numpy as np
from sklearn.utils import shuffle
import geopandas as gpd

# 縣市處理
place_df = pd.read_csv('csv/Place_id.csv')
gdf = gpd.read_file('taiwan_map/TOWN_MOI_1100415.shp', encoding='utf-8')
gdf['place'] = gdf['COUNTYNAME'] + gdf['TOWNNAME']
    
    
gdf2 = pd.merge(gdf, place_df, on ="place")

gdf3 =  pd.merge(gdf, place_df, how="outer")


place_list = gdf2['place']

gdf4 = gdf3[~gdf3["place"].isin(place_list)]

gdf4.to_csv("csv/test.csv", index=False)

jojo = pd.read_csv('csv/test.csv')

geo = gdf4['geometry'].reset_index()

gdf_except = gdf4[['COUNTYNAME','geometry', 'place', 'Place_id']]
gdf_except = gdf_except[gdf_except['place'].isin(['新竹市','嘉義市'])]
gdf_except = gdf_except.reset_index(drop=True)



place = '嘉義市'
gdf5 = gdf4[gdf4['COUNTYNAME'] == place]
geo = gdf5.geometry.unary_union
gdf_except.loc[1,'geometry'] =  geo
gdf_except.loc[1,'COUNTYNAME'] =  place 


gdf_all = gdf2[['COUNTYNAME', 'place', 'Place_id','geometry']]

gdf_all = gdf_all.append(gdf_except).reset_index(drop=True)
gdf_all = gdf_all[['COUNTYNAME', 'place', 'Place_id','geometry']]

place_id = gdf_all[['COUNTYNAME', 'place', 'Place_id']]
place_id.to_csv("csv/Place.csv", index=False)


gdf_all.to_csv("csv/Place_gdf.csv", index=False)


[gdf_except['place'] == '新竹市']

place_gdf = pd.read_csv('csv/Place_gdf.csv')


import pandas as pd
import numpy as np
from sklearn.utils import shuffle
import geopandas as gpd


place_df = pd.read_csv('csv/Place.csv').drop(columns=['COUNTYNAME'] )
gdf_raw = gpd.read_file('taiwan_map/TOWN_MOI_1100415.shp', encoding='utf-8')
gdf_raw ['place'] = gdf_raw ['COUNTYNAME'] + gdf_raw ['TOWNNAME']
gdf = pd.merge(gdf_raw , place_df, on ="place")
gdf = gdf[['COUNTYNAME', 'place', 'Place_id','geometry']]


# 嘉義市,嘉義市,600.0
place = '嘉義市'
geometry = gdf_raw [gdf_raw ['COUNTYNAME'] == place].geometry.unary_union
gdf = gdf.append({'COUNTYNAME' : place, 'place' : place, 'Place_id' : 600.0 , 'geometry' :geometry},
           ignore_index=True)

# 新竹市,新竹市,300.0
place = '新竹市'
geometry = gdf_raw [gdf_raw ['COUNTYNAME'] == place].geometry.unary_union
gdf = gdf.append({'COUNTYNAME' : place, 'place' : place, 'Place_id' : 300.0 , 'geometry' :geometry},
           ignore_index=True)

[ '新竹市','新竹市',300.0 ,geometry]

gdf_except.loc[1,'geometry'] =  geometry
gdf_except.loc[1,'COUNTYNAME'] =  place 




# 研究欄位

compare_data = pd.read_csv('compare/compare_index.csv')

compare_data.columns
count = compare_data['Non_City_Land_Code'].value_counts()

count = compare_data['City_Land_Usage'].value_counts()


compare_data_100 = compare_data[:100]

count = compare_data['Type'].value_counts()

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
