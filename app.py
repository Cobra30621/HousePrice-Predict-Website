import struct
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import streamlit as st
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb
from model import  ModelManager
from data_processor import DataPreprocessor, Options_Manager, DataManager
import components as cp
from compare.compare_index import CompareManager;
import datetime
from datetime import datetime as dt

@st.cache
def load_compare_data():
    return pd.read_csv( 'compare/compare_index.csv')


def on_advanced_summit(**kwargs):
    for key, value in kwargs.items():
        st.session_state[key] = value


def app():
    cp.create_sidebar()

    st.title("台灣房價地圖")
    with st.expander("使用說明"):
        st.markdown(
            """**介紹:** OWO
        """
        )

    dp = DataPreprocessor()
    model = ModelManager()
    compare_data = load_compare_data()
    cpm = CompareManager(compare_data)

    Building_Material_manager = Options_Manager('csv/Building_Material.csv')
    Note_manager = Options_Manager('csv/Note.csv')

    # _manager = DataManager('csv/.csv')
    Type_manager = DataManager('csv/Type.csv')
    Building_Types_manager = DataManager('csv/Building_Types.csv')
    Parking_manager = DataManager('csv/Parking_Space_Types.csv')
    City_Land_Usage_manager = DataManager('csv/City_Land_Usage.csv')
    Non_City_Land_Usage_manager = DataManager('csv/Non_City_Land_Usage.csv')


    basic_key_defaults = {
        "Transfer_Total_Ping" : 20,
        "min_floors_height" : 1,
        "Type" : "房地(土地+建物)",
        "Building_Types" : "住宅大樓(11層含以上有電梯)",
        "city_list" :  ['臺北市'],
        "Place" : "臺北市大安區",
        "Note_Presold" : False,
        "house_age" : 10
    }

    for key , value in basic_key_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    
    with st.form("basic_form"):

        st.subheader('1. 填寫房屋基礎資料')
        area_col1, area_col2, Type_col, Building_Types_col = st.columns([1, 1, 1, 1])
        
        with area_col1:
            Transfer_Total_Ping = st.number_input('建坪' , key="Transfer_Total_Ping")
        with area_col2:
            min_floors_height = st.number_input('交易樓層', step=1, key = "min_floors_height" )
        with Type_col:
            Type = Type_manager.get_id(
            st.selectbox('交易標的',
                Type_manager.get_name_list(), key = "Type")) 

        with Building_Types_col:
            Building_Types = Building_Types_manager.get_id(
            st.selectbox('建物型態',
                Building_Types_manager.get_name_list(), key = "Building_Types")) 
        

        city_col, district_col, Note_Presold_col, age_col = st.columns(4)
        
        with city_col:
            city_list = st.multiselect(
            '縣市',
            dp.get_city_list(),  key = "city_list") # on_change
            
        with district_col:
            Place = st.selectbox('市區',
            dp.get_place_list_by_city_list(city_list), key="Place")


        with Note_Presold_col:
            Note_Presold = st.checkbox('預售屋', key="Note_Presold")
        with age_col:
            if(not Note_Presold):
                house_age = st.number_input('屋齡', key = "house_age")
            
        # basic_submited = st.button("基礎篩選")
        basic_submited = st.form_submit_button("產生相似進階資料")
    
    # # 儲存
    # if(st.session_state["FormSubmitter:進階搜尋表單-預測房價"]):

    

    # 填寫進階房價
    if(basic_submited ):
        # 1. 資料轉換

        Place_id = dp.get_place_id(Place)
        if(Note_Presold):
            house_age = -1

        # 2. 取得compate_data 作為input_data
        input_data = cpm.get_input_data(Place_id, Type, Transfer_Total_Ping,\
             Building_Types, house_age, min_floors_height)
        
        # 3. 設定預設值
        kwargs = { 
            "trading_floors_count" : 1} 
        ## 所有Note都先關閉
        Note_manager.set_options([])
        kwargs = Note_manager.get_variable_dic(kwargs)

        for key, value in kwargs.items():
            input_data[key][0] = value


        # 4. 儲存資料
        ## 一般資料
        avoid_save_columns = ["Type", "Building_Types", "house_age", "Transfer_Total_Ping", \
            "min_floors_height",  "Note_Presold"]
        save_data = input_data.drop(columns=avoid_save_columns)

        for key in save_data.columns:
            st.session_state[key] = save_data[key][0]

        st.write("Debug: 篩選資料產出資料")
        st.dataframe(input_data) 
        
        ## 儲存多選欄位
        ### 儲存建築材料
        Building_Material_state = Building_Material_manager.get_save_state(input_data)
        st.session_state["Building_Material"] = Building_Material_state

        ### 特殊標記
        Note_state = Note_manager.get_save_state(input_data)
        st.session_state["Note"] = Note_state

        ## 儲存清單資料 : id to name
        ### Parking_Space
        Parking_Space_Types = input_data["Parking_Space_Types"][0]
        st.session_state["Parking_Space_Types"] = Parking_manager.get_name(Parking_Space_Types)
        ### City_Land_Usage
        City_Land_Usage = input_data["City_Land_Usage"][0]
        st.session_state["City_Land_Usage"] = City_Land_Usage_manager.get_name(City_Land_Usage)
        ### Non_City_Land_Usage
        Non_City_Land_Usage = input_data["Non_City_Land_Code"][0]
        st.session_state["Non_City_Land_Usage"] = Non_City_Land_Usage_manager.get_name(Non_City_Land_Usage)
        
        # 日期預設值
        st.session_state["today"] = datetime.date.today()

        
    # st.session_state


    with st.form("進階搜尋表單"):
        st.subheader('2. 填寫房屋進階資料')

        # 面積與樓高
        main_area_col, area_ping_col, building_total_floors  = st.columns([1, 1, 1])
        with main_area_col:
            main_area = st.number_input('主建物面積', key = "main_area")
        with area_ping_col:
            area_ping = st.number_input('地坪',  key = "area_ping")
        with building_total_floors:
            building_total_floors = st.number_input('建築總樓層數',  key = "building_total_floors", step=1)

        room_col, hall_col, bathroom_col = st.columns([1, 1, 1])
        with room_col:
            room = st.number_input('房',  key = "room", step=1 ) 
        with hall_col:
            hall = st.number_input('廳',  key = "hall", step=1)
        with bathroom_col:
            bathroom = st.number_input('衛',  key = "bathroom", step=1) 

        # 多選清單
        options_col1, options_col2, city_col, non_city_col = st.columns(4)
        with options_col1:
            Building_Material_options = st.multiselect(
                '主要建材', Building_Material_manager.get_list(),  key = "Building_Material")
        with options_col2:
            Note_options = st.multiselect(
                '特殊標記', Note_manager.get_list(),  key = "Note")

        # 使用分區
        with city_col:
            City_Land_Usage = City_Land_Usage_manager.get_id(
                st.selectbox('都市土地使用分區',
                City_Land_Usage_manager.get_name_list(), key="City_Land_Usage"))

        with non_city_col:
            Non_City_Land_Usage = Non_City_Land_Usage_manager.get_id(
                st.selectbox('非都市土地使用分區',
                Non_City_Land_Usage_manager.get_name_list(), key="Non_City_Land_Usage"))



        # 停車位與購買時間
        month_col ,parking_col1, parking_col2, parking_col3 = st.columns([2, 1, 2, 2])
        with month_col:
            today = st.date_input(
                "購買時間",
                key = "today")
            Month = today.strftime("%Y%m") 
            print(Month)
        with parking_col1:
            Note_Parking = st.checkbox('含車位', key="Note_Parking")
        with parking_col2:
            Parking_Space_Types = Parking_manager.get_id(
            st.selectbox('車位類別',
                Parking_manager.get_name_list(), key="Parking_Space_Types"))
        with parking_col3:
            Parking_Area = st.number_input('停車位面積', key = "Parking_Area")

        
        # 交易數量
        Transaction_col1, Transaction_col2, Transaction_col3 = st.columns([1, 1, 1])
        with Transaction_col1:
            Transaction_Land = st.number_input('交易土地的數量', key = "Transaction_Land", step=1)
        with Transaction_col2:
            Transaction_Building = st.number_input('交易建築的數量', key = "Transaction_Building" , step=1)
        with Transaction_col3:
            Transaction_Parking = st.number_input('交易車位的數量',  key = "Transaction_Parking", step=1)

        
        adv_submited = st.form_submit_button("預測房價", on_click=on_advanced_summit)

    # 預測房價
    if(adv_submited):
        # 1.資料轉換
        Place_id = dp.get_place_id(Place)
        if(len(Note_options) == 0):
            Note_Null = 1
        else:
            Note_Null = 0

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
            "trading_floors_count" : 1,
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

        st.write("Debug: 輸入模型的資料")
        st.json(kwargs) 

        # 2. 繪圖與預測
        geo_col, label_col, price_col, = st.columns([6,1,3])

        if(len(city_list) != 0):
            with geo_col:
                # 地圖繪製
                selected_col = "price"
                gdf = dp.get_gdf_by_city(city_list)
                input_data =pd.DataFrame([kwargs]) 
                print(input_data)
                gdf = model.predict_by_place(input_data, gdf)
                
                st.dataframe(gdf[["Place_id", "price"]])

                gdf[selected_col] =  gdf[selected_col]
                gdf = gdf.sort_values(by=[selected_col], ascending=True)

                min_price = gdf['price_wan'].min()
                max_price = gdf['price_wan'].max()

                initial_view_state = pdk.ViewState(
                    latitude=23.5,
                    longitude=121,
                    zoom=7,
                    max_zoom=20,
                    pitch=0,
                    bearing=0,
                    height=700,
                    width=None,
                )

                
                # 顏色參數
                n_colors = 10
                color_exp = f"[R, G, B]"

                palettes = cm.list_colormaps()
                palette = palettes[2]
                print(palettes)
                print(palette)

                colors = cm.get_palette(palette, n_colors)
                colors = [hex_to_rgb(c) for c in colors]

                for i, ind in enumerate( gdf.index):
                    price = gdf['price_wan'][ind]
                    index = int(((price - min_price) / (max_price - min_price) ) * len(colors))
                    if index >= len(colors):
                        index = len(colors) - 1
                    gdf.loc[ind, "R"] = colors[index][0]
                    gdf.loc[ind, "G"] = colors[index][1]
                    gdf.loc[ind, "B"] = colors[index][2]

                geojson = pdk.Layer(
                    "GeoJsonLayer",
                    gdf,
                    pickable=True,
                    opacity=0.5,
                    stroked=True,
                    filled=True,
                    extruded=False,
                    wireframe=True,
                    get_elevation=selected_col,
                    elevation_scale=1,
                    get_fill_color=color_exp,
                    get_line_color=[0, 0, 0],
                    get_line_width=2,
                    line_width_min_pixels=1,
                )

                tooltip = {
                    "html": "<b>地區:</b> {"+ 'place' + "}<br><b>價格:</b> {"
                    +  'price_wan'
                    + "}萬",
                    "style": {"backgroundColor": "steelblue", "color": "white"},
                }

                layers = [geojson]

                r = pdk.Deck(
                    layers=layers,
                    initial_view_state=initial_view_state,
                    map_style="light",
                    tooltip=tooltip,
                )

                st.pydeck_chart(r)

            with label_col:
                st.write(
                    cm.create_colormap(
                        palette,
                        # label=selected_col.title(),
                        # label="萬",
                        width=0.2,
                        height=3,
                        orientation="vertical",
                        vmin=min_price,
                        vmax=max_price,
                        font_size=10,
                    )
                )
            
            with price_col:
                house_price = gdf[gdf['place'] == Place].reset_index()['price_wan'][0]

                unit_price = 0
                if(Transfer_Total_Ping != 0):
                    unit_price = round(house_price / Transfer_Total_Ping)

                st.subheader("{}".format(Place))
                
                st.write("- 總房價　 : {}萬".format(house_price))
                st.write("- 單位房價 : {}萬".format(unit_price))

                # st.subheader("房價比較")

                # citys = city_list[0]
                # for i in range(1, len(city_list)):
                #     citys +=  ", {}".format(city_list[i])

                # st.write("{}".format(citys))
                
                # st.write("- 最高房價 :{}萬".format(max_price))
                # st.write("- 最低房價 :{}萬".format(min_price))


app()