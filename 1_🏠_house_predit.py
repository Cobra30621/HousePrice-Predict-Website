import pandas as pd
import pydeck as pdk
import geopandas as gpd
import streamlit as st
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb
from model import DataPreprocessor, ModelManager
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

    with st.form("basic_form"):
        area_col1, area_col2, Type_col, Building_Types_col = st.columns([1, 1, 1, 1])
        
        with area_col1:
            Transfer_Total_Ping = st.number_input('轉移坪數', value=20.0 )
        with area_col2:
            min_floors_height = st.number_input('交易樓層', step=1, value=1 )
        with Type_col:
            Type = st.selectbox(
                '交易標的',
                dp.get_Type_list()) # on_change

        with Building_Types_col:
            Building_Types = st.selectbox(
                '建物型態',
                dp.get_Building_Types_list()) # on_change


        city_col, district_col, Note_Presold_col,  age_col = st.columns([1, 1, 1, 1])

        with city_col:
            city_list = st.multiselect(
            '縣市',
            dp.get_city_list(), ['臺北市']) # on_change
            
        with district_col:
            place = st.selectbox(
            '市區',
            dp.get_place_list_by_city_list(city_list))
        with Note_Presold_col:
            Note_Presold = st.checkbox('預售屋')
        with age_col:
            house_age = st.number_input('屋齡', value=10)

        

    
        basic_submited = st.form_submit_button("基礎篩選")

    

    # 填寫進階房價
    if(basic_submited ):
        # 資料轉換
        Place_id = dp.get_place_id(place)
        Building_Types_id = dp.get_Building_Types_id(Building_Types)
        Type_id = dp.get_Type_id(Type)
        if(Note_Presold):
            house_age = -1

        # 取得compate_data 作為input_data
        input_data = cpm.get_input_data(Place_id, Type_id, Transfer_Total_Ping,\
             Building_Types_id, house_age, min_floors_height)
        
        # 設定預設值
        kwargs = { 
            "trading_floors_count" : 1, "Note_Relationships" : 0} 
        for key, value in kwargs.items():
            input_data[key][0] = value

        # 儲存資料
        for key in input_data.columns:
            st.session_state[key] = input_data[key][0]
        st.session_state['had_input_data_state'] = True

        st.write("Debug: 輸入模型的資料")
        st.dataframe(input_data) 




    with st.form("進階搜尋表單"):
        
        today = st.date_input(
            "購買時間",
            datetime.date.today())
        Month = today.month

        main_area_col, area_ping_col, City_Land_Usage_col = st.columns([1, 1, 1])
        with main_area_col:
            main_area = st.number_input('主建物面積', key = "main_area")
        with area_ping_col:
            area_ping = st.number_input('地坪',  key = "area_ping")
        with City_Land_Usage_col:
            City_Land_Usage = st.number_input('都市土地使用分區',  key = "City_Land_Usage", step=1)

        Transaction_col1, Transaction_col2, Transaction_col3 = st.columns([1, 1, 1])
        with Transaction_col1:
            Transaction_Land = st.number_input('交易土地的數量', key = "Transaction_Land", step=1)
        with Transaction_col2:
            Transaction_Building = st.number_input('交易建築的數量', key = "Transaction_Building" , step=1)
        with Transaction_col3:
            Transaction_Parking = st.number_input('交易車位的數量',  key = "Transaction_Parking", step=1)

        building_total_floors = st.number_input('房子總高度',  key = "building_total_floors", step=1)

        room_col, hall_col, bathroom_col = st.columns([1, 1, 1])
        with room_col:
            room = st.number_input('房',  key = "room", step=1 ) 
        with hall_col:
            hall = st.number_input('廳',  key = "hall", step=1)
        with bathroom_col:
            bathroom = st.number_input('衛',  key = "bathroom", step=1) 
        
        adv_submited = st.form_submit_button("進階搜尋", on_click=on_advanced_summit)

    # st.session_state


    # 預測房價
    if(adv_submited):
        # 資料轉換
        Place_id = dp.get_place_id(place)
        Building_Types_id = dp.get_Building_Types_id(Building_Types)
        Type_id = dp.get_Type_id(type)


        # 使用者輸入欄位
        kwargs = {
            "Place_id": Place_id, "Building_Types" : Building_Types_id,"Type" : Type_id,
            "Month" : int(Month),
            "Transfer_Total_Ping" : Transfer_Total_Ping,"min_floors_height": min_floors_height, 
            "house_age": house_age, 
            "main_area" : main_area,
            "area_ping" : area_ping,
            "building_total_floors" : building_total_floors,
            "Transaction_Land" : Transaction_Land,
            "Transaction_Building" : Transaction_Building,
            "Transaction_Parking" : Transaction_Parking,
            "City_Land_Usage" : City_Land_Usage,
            "trading_floors_count" : 1,
            "room" : room,
            "hall" : hall,
            "bathroom" : bathroom
        } 

        for key, value in kwargs.items():
            input_data[key][0] = value

        st.write("Debug: 輸入模型的資料")
        st.dataframe(input_data) 

    if(adv_submited ):

        # 繪圖
        geo_col, label_col, price_col, = st.columns([6,1,3])

        if(len(city_list) != 0):
            with geo_col:
                # 地圖繪製
                selected_col = "price"
                gdf = dp.get_gdf_by_city(city_list)
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
                palette = palettes.index("Blues")

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
                house_price = gdf[gdf['place'] == place].reset_index()['price_wan'][0]

                unit_price = 0
                if(Transfer_Total_Ping != 0):
                    unit_price = round(house_price / Transfer_Total_Ping)

                st.subheader("{}".format(place))
                
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