import struct
import pandas as pd
import pydeck as pdk
import geopandas as gpd
from sqlalchemy import null
import streamlit as st
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb
from model import  ModelManager
from data_processor import DataPreprocessor, Options_Manager, DataManager
import components as cp
from compare.compare_index import CompareManager;
import datetime
from datetime import datetime as dt
import time
from draw import draw_bar, draw_map
import joblib
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties as font

# 重要參數
use_unit_model = False # 使否使用Unit模型



# 設定字型的路徑
font1 = font(fname="fonts/Noto_Sans_TC/NotoSansTC-Regular.otf")


@st.cache(show_spinner = False)
def load_compare_data():
    return pd.read_csv( 'compare/compare_index.csv')

@st.cache(show_spinner = False)
def load_csv(file_path):
    return pd.read_csv( file_path)

@st.cache(show_spinner = False)
def loadModel( model_path):
    return joblib.load(model_path)

@st.cache(show_spinner = False)
def load_gdf():
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
    return gdf


###### sidebar info ######
cp.create_sidebar()

# had_compare 由於Streamlit 限制，需要進行處理的項目
# 過程有點複雜，我能力不足，就儘可能表達
# 0:第一次預測，要將compare_index 產出的相似資料存檔，並且重啟
# 1:重啟，讀取存檔，更新到欄位將第一次預測結果產出。
# 2:第二次預測，不用做任何事情
if 'had_compare' not in st.session_state:
    st.session_state['had_compare'] = 0

st.title("台灣房價預測網站")

# st.subheader("此網站可以幫助你了解台灣房價")

st.write("---")

st.subheader("請填寫你想預測的房屋資料"
)

place_df = load_csv('csv/Place.csv')
dp = DataPreprocessor(place_df)
All_City_Land_Usage_Manager = DataManager(load_csv('csv/All_City_Land_Usage.csv'))

Type_col, Building_Types_col, area_col1, area_col2 = st.columns([1, 1, 1, 1])


with Type_col:
    Type_list = ['房地(土地+建物)', '建物', '房地(土地+建物)+車位']
    Type = st.selectbox('交易標的',Type_list) 

with Building_Types_col:
    Building_Types_list = ['住宅大樓(11層含以上有電梯)', '透天厝', '華廈(10層含以下有電梯)', '公寓(5樓含以下無電梯)', '套房(1房1廳1衛)']
    Building_Types = st.selectbox('建物型態', Building_Types_list)

with area_col1:
    Transfer_Total_Ping = st.number_input('建坪', value = 10.0, min_value=0.01, max_value=500.0)
with area_col2:
    if(Building_Types == '透天厝'):
        min_floors_height = st.number_input('交易樓層', step=1, value=1, disabled = True)
    else:
        min_floors_height = st.number_input('交易樓層', step=1, min_value=1, max_value=100)

city_col, district_col,  age_col = st.columns(3)

with city_col:
    city_list = ['臺北市', '新北市', '基隆市', '桃園市', '新竹縣', '新竹市',
        '宜蘭縣', '苗栗縣', '臺中市', '彰化縣', '雲林縣', '嘉義縣', '嘉義市',
        '臺南市', '高雄市', '屏東縣', '臺東縣', '花蓮縣', '南投縣',    
        '澎湖縣', '連江縣', '金門縣' ]
    city_list_selected = [st.selectbox( '縣市', city_list)]
    # city_list_selected = st.multiselect( '縣市', city_list) 
    
    
with district_col:
    Place = st.selectbox('市區',
    dp.get_place_list_by_city_list(city_list_selected))

with age_col:
    house_age = st.number_input('屋齡(預售屋 = -1)', value = 10, min_value=-1, max_value=100,step=1)
    


with st.expander("更多欄位"):
    st.info("註:第一次預測時，會自動將空欄位填入系統預測值")
    # 事前計算
    Parking_Space_Types_Default = 1 if Type == '房地(土地+建物)+車位' else 0
    Note_Parking =  (Type != '房地(土地+建物)+車位')

    # 讀取存檔
    if(st.session_state["had_compare"] == 1):
        st.session_state["main_area"] = st.session_state["main_area_save"] if ("main_area_save" in st.session_state) else 0
        st.session_state["area_ping"] = st.session_state["area_ping_save"] if ("area_ping_save" in st.session_state) else 0
        st.session_state["building_total_floors"] = st.session_state["building_total_floors_save"] if ("building_total_floors_save" in st.session_state) else 0
        st.session_state["room"] = st.session_state["room_save"] if ("room_save" in st.session_state) else 0
        st.session_state["hall"] = st.session_state["hall_save"] if ("hall_save" in st.session_state) else 0
        st.session_state["bathroom"] = st.session_state["bathroom_save"] if ("bathroom_save" in st.session_state) else 0
        st.session_state["Transaction_Land"] = st.session_state["Transaction_Land_save"] if ("Transaction_Land_save" in st.session_state) else 0
        st.session_state["Transaction_Building"] = st.session_state["Transaction_Building_save"] if ("Transaction_Building_save" in st.session_state) else 0
        st.session_state["Transaction_Parking"] = st.session_state["Transaction_Parking_save"] if ("Transaction_Parking_save" in st.session_state) else 0
        st.session_state["All_City_Land_Usage"] = st.session_state["All_City_Land_Usage_save"] if ("All_City_Land_Usage_save" in st.session_state) else "請選擇"
        

    # 面積與樓高  
    main_area_col, area_ping_col, building_total_floors  = st.columns([1, 1, 1])
    with main_area_col:
        main_area = st.number_input('主建物坪數', min_value = 0.0, max_value=500.0, key = "main_area")
    with area_ping_col:
        area_ping = st.number_input('地坪', min_value = 0.0, max_value=500.0, key = "area_ping")
    with building_total_floors:
        building_total_floors = st.number_input('建築總樓層數', min_value=0, max_value=100, step=1, key = "building_total_floors")

    room_col, hall_col, bathroom_col = st.columns([1, 1, 1])
    with room_col:
        room = st.number_input('幾房', min_value=0, max_value=100, step=1 , key = "room") 
    with hall_col:
        hall = st.number_input('幾廳', min_value=0, max_value=100, step=1, key = "hall")
    with bathroom_col:
        bathroom = st.number_input('幾衛', min_value=0, max_value=100, step=1, key = "bathroom") 

    # 交易數量
    Transaction_col1, Transaction_col2, Transaction_col3 = st.columns([1, 1, 1])
    with Transaction_col1:
        Transaction_Land = st.number_input('交易土地的數量', min_value=0, max_value=100,
        step=1 , key = "Transaction_Land")
    with Transaction_col2:
        Transaction_Building = st.number_input('交易建築的數量', min_value=0, max_value=100 ,
        step=1 , key = "Transaction_Building")
    with Transaction_col3:
        Transaction_Parking = st.number_input('交易車位的數量', min_value=0, max_value=100, step=1, 
        disabled = Note_Parking , key = "Transaction_Parking")

    # 多選清單
    options_col1, options_col2, city_col = st.columns(3)
    with options_col1:
        Building_Material_options_list = ['使用鋼骨', '使用鋼筋', '使用混凝土', '使用其他鋼材', '使用磚頭', '使用木材，土塊，竹子', '使用鐵材', '使用瓦片', '使用泥土', '有用到鋼筋混凝土補強']
        Building_Material_options = st.multiselect(
            '主要建材(多選)', Building_Material_options_list, ['使用鋼筋', '使用混凝土'])
    with options_col2:
        Note_options_list = ['是否有隔間', '有電梯', '增建或未登記建物', '頂樓加蓋', '陽台外推', '夾層', '特殊關係交易', '商業用途', '政府機關承購', '傢俱', '建商與地主合建案', '毛胚屋', '瑕疵or凶宅', '畸零地', '裝潢', '公共設施保留地', '分次登記案件', '協議價購', '債權債務', '都更效益', '逾期未辦繼承', '急售']
        Note_options = st.multiselect(
            '特殊標記(多選)', Note_options_list)

    # 使用分區
    with city_col:
        All_City_Land_Usage_list = ['請選擇', '住', '農', '工', '商業', '其他住商', '其他住', '不知道', '農牧用地', '甲種建築用地', '乙種建築用地', '丙種建築用地', '丁種建築用地']
        All_City_Land_Usage = st.selectbox('土地使用分區', All_City_Land_Usage_list, key="All_City_Land_Usage")


    # 停車位與購買時間
    month_col ,parking_col2, parking_col3 = st.columns([2,  2, 2])
    with month_col:
        today = st.date_input(
            "購買時間")
        Month = today.strftime("%Y%m") 
    with parking_col2:
        
        Parking_Space_Types_list = ['無車位', '坡道平面', '坡道機械', '一樓平面', '升降機械', '其他', '升降平面', '塔式車位']
        Parking_Space_Types = st.selectbox('車位類別', Parking_Space_Types_list,
                disabled = Note_Parking, index = Parking_Space_Types_Default)
    with parking_col3:
        Parking_Area = st.number_input('停車位坪數', min_value=0.0, max_value=100.0, 
                disabled = Note_Parking)


adv_submited = st.button("預測房價")

show_result = False
# 預測房價
if(adv_submited | (st.session_state['had_compare'] == 1)):
    with st.spinner(text='房價預測中'):
        # 讀取模型
        model_path = "model/LGBM_0704"
        total_model = loadModel(model_path + '/model.pkl')
        if(use_unit_model):
            unit_model = loadModel(model_path + '/model_unit.pkl')
            model = ModelManager(total_model, unit_model, use_unit_model)
        else:
            model = ModelManager(total_model, null, use_unit_model)
        

        Type_manager = DataManager(load_csv('csv/Type.csv'))
        Building_Types_manager = DataManager(load_csv('csv/Building_Types.csv'))
        Parking_manager = DataManager(load_csv('csv/Parking_Space_Types.csv'))
        All_City_Land_Usage_manager = DataManager(load_csv('csv/All_City_Land_Usage.csv'))
        Building_Material_manager = Options_Manager(load_csv('csv/Building_Material.csv'))
        Note_manager = Options_Manager(load_csv('csv/Note.csv'))

        gdf = load_gdf()
        dp.set_gdf(gdf)

        # 1.資料轉換
        Place_id = dp.get_place_id(Place)
        Building_Types = Building_Types_manager.get_id(Building_Types)
        Type = Type_manager.get_id(Type)
        Parking_Space_Types = Parking_manager.get_id(Parking_Space_Types)

        ## 土地使用分區
        All_City_Land_Usage = All_City_Land_Usage_manager.get_id(All_City_Land_Usage)
        is_City_Land_Usage = All_City_Land_Usage_manager.get_column_value_by_id("City_Land_Usage", All_City_Land_Usage)

        if(is_City_Land_Usage):
            City_Land_Usage = All_City_Land_Usage
            Non_City_Land_Usage = 0
        else:
            City_Land_Usage = 0
            Non_City_Land_Usage = All_City_Land_Usage


        Note_Null = 0 if len(Note_options) == 0 else 1
        Note_Presold = 1 if house_age == -1 else 0
        trading_floors_count = min_floors_height if(Building_Types == '透天厝') else 1

        # 存檔與比較相似度
        if(st.session_state['had_compare'] == 0):
            # 2. 計算相似欄位
            compare_data = load_compare_data()
            cpm = CompareManager(compare_data)
            input_data = cpm.get_input_data(Place_id, Type, Transfer_Total_Ping,\
                    Building_Types, house_age, min_floors_height)

            st.session_state['had_compare'] = 1
            if(main_area == 0):
                main_area = input_data["main_area"].iloc[0]
            st.session_state["main_area_save"] = main_area

            if(area_ping == 0):
                area_ping = input_data["area_ping"].iloc[0]
            st.session_state["area_ping_save"] = area_ping 

            if(building_total_floors == 0):
                building_total_floors = input_data["building_total_floors"].iloc[0]
            st.session_state["building_total_floors_save"] = building_total_floors

            if(room == 0):
                room = input_data["room"].iloc[0]
            st.session_state["room_save"] = room

            if(hall == 0):
                hall = input_data["hall"].iloc[0]
            st.session_state["hall_save"] = hall
            
            if(bathroom == 0):
                bathroom = input_data["bathroom"].iloc[0]
            st.session_state["bathroom_save"] = bathroom

            if((Transaction_Land == 0) & (Transaction_Building == 0) & (Transaction_Parking == 0)):
                Transaction_Land = Type_manager.get_column_value_by_id('Transaction_Land' ,Type)
                Transaction_Building = Type_manager.get_column_value_by_id('Transaction_Building' ,Type) 
                Transaction_Parking = Type_manager.get_column_value_by_id('Transaction_Parking' ,Type)
            st.session_state["Transaction_Land_save"] = Transaction_Land
            st.session_state["Transaction_Building_save"] = Transaction_Building
            st.session_state["Transaction_Parking_save"] = Transaction_Parking

            if(All_City_Land_Usage == 0):
                All_City_Land_Usage = input_data['City_Land_Usage'].iloc[0]
            st.session_state["All_City_Land_Usage_save"] = All_City_Land_Usage_manager.get_name(All_City_Land_Usage)
    
            # 重run一次
            st.experimental_rerun()
        else:
            st.session_state['had_compare'] = 2
            

        ## 使用者輸入欄位
        kwargs = {
            "Place_id": Place_id, 
            "Building_Types" : Building_Types,
            "Type" : Type,
            "Month" : int(Month),
            "Note_Presold" : Note_Presold,
            "house_age": house_age, 
            "min_floors_height": min_floors_height, 
            "building_total_floors" : building_total_floors,
            "trading_floors_count" : trading_floors_count,
            "Transfer_Total_Ping" : Transfer_Total_Ping,
            "main_area" : main_area,
            "area_ping" : area_ping,
            "Transaction_Land" : Transaction_Land,
            "Transaction_Building" : Transaction_Building,
            "Transaction_Parking" : Transaction_Parking,
            "City_Land_Usage" : City_Land_Usage,
            "Non_City_Land_Code" : Non_City_Land_Usage,
            "Note_Parking" : Note_Parking,
            "Parking_Space_Types" : Parking_Space_Types,
            "Parking_Area" : Parking_Area,
            "room" : room,
            "hall" : hall,
            "bathroom" : bathroom,
            "Note_OnlyParking" : 0,
            "Note_Null" : Note_Null
        } 

        # 建材
        Building_Material_manager.set_options(Building_Material_options)
        kwargs = Building_Material_manager.get_variable_dic(kwargs)

        # 特殊標記
        Note_manager.set_options(Note_options)
        kwargs = Note_manager.get_variable_dic(kwargs)

        # 2. 地圖繪製
        
        gdf = dp.get_gdf_by_city(city_list_selected)
        input_data =pd.DataFrame([kwargs]) 
        gdf = model.predict_by_place(input_data, gdf)

        min_price = gdf['price_wan'].min()
        max_price = gdf['price_wan'].max()

        map = draw_map(gdf, city_list_selected[0])

        # 進度條
        st.write('---')

    
        

    # my_bar = st.progress(0)
    # for percent_complete in range(100):
    #         time.sleep(0.01)
    #         my_bar.progress(percent_complete + 1)
    # time.sleep(0.05)
    st.success('房價預測成功')
    st.write('---')
    show_result = True


# 顯示成果
if(show_result):
    
    geo_col,  price_col, = st.columns([5,5])
    with geo_col:
        st.subheader("1. 房價預測地圖")
        
        st.pydeck_chart(map)
        house_price = gdf[gdf['place'] == Place].reset_index()['price_wan'][0]

    with price_col:

        house_price = gdf[gdf['place'] == Place].reset_index()['price_wan'][0]

        unit_price = gdf[gdf['place'] == Place].reset_index()['unit_price_wan'][0]
        
        st.subheader("2. 房價預測結果")
        

        st.write("#### 總房價　 :　{}萬".format(house_price))
        st.write("#### 單坪房價　:　{}萬".format(int(unit_price)))
        st.pyplot(draw_bar(house_price, min_price, max_price, city_list_selected[0]))
        st.info("此地圖為以相同條件，對【{}】其他市區進行房價預測".format(city_list_selected[0]))
    


