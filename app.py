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

@st.cache
def load_csv(file_path):
    return pd.read_csv( file_path)

@st.cache
def load_gdf():
    place_df = pd.read_csv('csv/Place_id.csv')
    gdf = gpd.read_file('taiwan_map/TOWN_MOI_1100415.shp', encoding='utf-8')
    gdf['place'] = gdf['COUNTYNAME'] + gdf['TOWNNAME']

    gdf = pd.merge(gdf, place_df, on ="place")
    return place_df, gdf


###### sidebar info ######
cp.create_sidebar()



st.title("台灣房價預測地圖")

# 
place_df, gdf = load_gdf()
dp = DataPreprocessor(place_df, gdf)
All_City_Land_Usage_Manager = DataManager(load_csv('csv/All_City_Land_Usage.csv'))

with st.container():
    st.subheader('請填寫房屋資料')
    area_col1, area_col2, Type_col, Building_Types_col = st.columns([1, 1, 1, 1])

    with area_col1:
        Transfer_Total_Ping = st.number_input('建坪', value = 10.0, min_value=0.01, max_value=500.0)
    with area_col2:
        min_floors_height = st.number_input('交易樓層', step=1, min_value=0, max_value=100)
    with Type_col:
        Type_list = ['房地(土地+建物)', '建物', '房地(土地+建物)+車位']
        Type = st.selectbox('交易標的',Type_list) 

    with Building_Types_col:
        Building_Types_list = ['住宅大樓(11層含以上有電梯)', '透天厝', '華廈(10層含以下有電梯)', '公寓(5樓含以下無電梯)', '套房(1房1廳1衛)']
        Building_Types = st.selectbox('建物型態', Building_Types_list)


    city_col, district_col,  age_col = st.columns(3)

    with city_col:
        city_list = ['臺北市', '新北市', '基隆市', '桃園市', '新竹縣', 
            '宜蘭縣', '苗栗縣', '臺中市', '彰化縣', '雲林縣', '嘉義縣', 
            '臺南市', '高雄市', '屏東縣', '臺東縣', '花蓮縣', '南投縣',    
            '澎湖縣', '連江縣', '金門縣' ]
        city_list_selected = [st.selectbox( '縣市', city_list)]
        # city_list_selected = st.multiselect( '縣市', city_list) 
        
        
    with district_col:
        Place = st.selectbox('市區',
        dp.get_place_list_by_city_list(city_list_selected))

    with age_col:
        house_age = st.slider('屋齡(預售屋 = -1)', value = 10, min_value=-1, max_value=100,step=1 )
        


with st.expander("更多欄位"):

    st.info("欄位為-1時，將代入模型預設值")

    # 面積與樓高
    main_area_col, area_ping_col, building_total_floors  = st.columns([1, 1, 1])
    with main_area_col:
        main_area = st.number_input('主建物坪數', min_value = 0.01, max_value=500.0)
    with area_ping_col:
        area_ping = st.number_input('地坪', min_value = 0.01, max_value=500.0)
    with building_total_floors:
        building_total_floors = st.number_input('建築總樓層數', min_value=0, max_value=100, step=1)

    room_col, hall_col, bathroom_col = st.columns([1, 1, 1])
    with room_col:
        room = st.number_input('幾房', min_value=0, max_value=100, step=1 ) 
    with hall_col:
        hall = st.number_input('幾廳', min_value=0, max_value=100, step=1)
    with bathroom_col:
        bathroom = st.number_input('幾衛', min_value=0, max_value=100, step=1) 

    # 交易數量
    Transaction_col1, Transaction_col2, Transaction_col3 = st.columns([1, 1, 1])
    with Transaction_col1:
        Transaction_Land = st.number_input('交易土地的數量', min_value=0, max_value=100, step=1)
    with Transaction_col2:
        Transaction_Building = st.number_input('交易建築的數量', min_value=0, max_value=100 , step=1)
    with Transaction_col3:
        Transaction_Parking = st.number_input('交易車位的數量', min_value=0, max_value=100, step=1)

    st.write('---')

    # 多選清單
    options_col1, options_col2, city_col = st.columns(3)
    with options_col1:
        Building_Material_options_list = ['使用鋼骨', '使用鋼筋', '使用混凝土', '使用其他鋼材', '使用磚頭', '使用木材，土塊，竹子', '使用鐵材', '使用瓦片', '使用泥土', '有用到鋼筋混凝土補強']
        Building_Material_options = st.multiselect(
            '主要建材(多選)', Building_Material_options_list)
    with options_col2:
        Note_options_list = ['是否有隔間', '有電梯', '增建或未登記建物', '頂樓加蓋', '陽台外推', '夾層', '特殊關係交易', '商業用途', '政府機關承購', '傢俱', '建商與地主合建案', '毛胚屋', '瑕疵or凶宅', '畸零地', '裝潢', '公共設施保留地', '分次登記案件', '協議價購', '債權債務', '都更效益', '逾期未辦繼承', '急售']
        Note_options = st.multiselect(
            '特殊標記(多選)', Note_options_list)

    # # 使用分區
    with city_col:
        All_City_Land_Usage_list = ['住', '農', '工', '商業', '其他住商', '其他住', '不知道', '農牧用地', '甲種建築用地', '乙種建築用地', '丙種建築用地', '丁種建築用地']
        All_City_Land_Usage = st.selectbox('都市土地使用分區', All_City_Land_Usage_list)


    # 停車位與購買時間
    month_col ,parking_col2, parking_col3 = st.columns([2,  2, 2])
    with month_col:
        today = st.date_input(
            "購買時間")
        Month = today.strftime("%Y%m") 
    with parking_col2:
        
        Parking_Space_Types_list = ['無車位', '坡道平面', '坡道機械', '一樓平面', '升降機械', '其他', '升降平面', '塔式車位']

        Parking_Space_Types_Default = 1 if Type == '房地(土地+建物)+車位' else 0
        Note_Parking =  (Type != '房地(土地+建物)+車位')
            
        Parking_Space_Types = st.selectbox('車位類別', Parking_Space_Types_list,
                disabled = Note_Parking, index = Parking_Space_Types_Default)
    with parking_col3:
        Parking_Area = st.number_input('停車位坪數', min_value=0.0, max_value=100.0, 
                disabled = Note_Parking)



adv_submited = st.button("預測房價")

# 預測房價
if(adv_submited):
    model = ModelManager()
    # compare_data = load_compare_data()
    # cpm = CompareManager(compare_data)


    City_Land_Usage_manager = DataManager(load_csv('csv/City_Land_Usage.csv'))
    Non_City_Land_Usage_manager = DataManager(load_csv('csv/Non_City_Land_Usage.csv'))
    Type_manager = DataManager(load_csv('csv/Type.csv'))
    Building_Types_manager = DataManager(load_csv('csv/Building_Types.csv'))
    Parking_manager = DataManager(load_csv('csv/Parking_Space_Types.csv'))
    All_City_Land_Usage_manager = DataManager(load_csv('csv/All_City_Land_Usage.csv'))

    Building_Material_manager = Options_Manager(load_csv('csv/Building_Material.csv'))
    Note_manager = Options_Manager(load_csv('csv/Note.csv'))

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

    # 2. 繪圖與預測
    geo_col, label_col, price_col, = st.columns([6,1,3])

    if(len(city_list_selected) != 0):
        with geo_col:
            st.write("說明 : 待撰寫")
            # 地圖繪製
            selected_col = "price"
            gdf = dp.get_gdf_by_city(city_list_selected)
            input_data =pd.DataFrame([kwargs]) 
            gdf = model.predict_by_place(input_data, gdf)
            

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
                "html": "【預測房價】<br><b>地區:</b> {"+ 'place' + "}<br>" +
                "<b>總房價:</b> {" +  'price_wan' + "}萬<br>" +
                "<b>單坪房價:</b> {" +  'unit_price_wan' + "}萬" ,
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

            unit_price = gdf[gdf['place'] == Place].reset_index()['unit_price_wan'][0]
            
            # st.subheader("{}".format(Place))
            st.subheader("房價預測")
            
            st.write("##### 總房價　 :　{}萬".format(house_price))
            st.write("##### 單坪房價　:　{}萬".format(int(unit_price)))

