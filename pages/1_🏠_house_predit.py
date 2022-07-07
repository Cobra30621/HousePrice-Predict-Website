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
    # compare_data = pd.read_csv( 'compare/compare_index.csv')
    compare_data = pd.read_csv( 'compare/compare_index_small.csv')
    drop_columns = ['area_m2', 'TDATE', 'manager', 'Total_price', 'parking_price', '編號',
       'address', 'including_basement', 'including_arcade', 'Main_Usage_Walk',
       'Main_Usage_Living', 'Main_Usage_Selling', 'Main_Usage_Manufacturing',
       'Main_Usage_Parking', 'Main_Usage_SnE', 'Main_Usage_Farm',
       'Building_Material_stone',  'Non_City_Land_Usage',
       'Unit_Price_Ping', 'Month_raw', 'combine']

    return compare_data.drop(columns=drop_columns)


def on_advanced_summit(**kwargs):
    for key, value in kwargs.items():
        st.session_state[key] = value



def app():
    cp.create_sidebar()

    st.title("台灣房價地圖")
    st.markdown(
        """**介紹:** OWO
    """
    )

    dp = DataPreprocessor()
    model = ModelManager()
    compare_data = load_compare_data()
    cpm = CompareManager(compare_data)

    with st.form("basic_form"):
        area_col1, area_col2, type_col, building_type_col = st.columns([1, 1, 1, 1])
        
        with area_col1:
            Transfer_Total_Ping = st.number_input('轉移坪數', value=20.0 )
        with area_col2:
            min_floors_height = st.number_input('交易樓層', step=1, value=1 )
        with type_col:
            type = st.selectbox(
                '交易標的',
                dp.get_type_list()) # on_change

        with building_type_col:
            building_type = st.selectbox(
                '建物型態',
                dp.get_building_type_list()) # on_change

        year_col, month_col , age_col = st.columns([1, 1, 1])

        with year_col:
            now_year = datetime.date.today().year
            year_list = [str(x) for x in range(now_year, now_year -5 , -1)]
            year = st.selectbox('購買年', year_list)
        with month_col:
            now_month =  datetime.date.today().month
            month_list = [str(x).zfill(2) for x in range(1, 13)]
            month = st.selectbox('購買月', month_list, now_month - 1)
        with age_col:
            house_age = st.number_input('屋齡', value=10)

        city_col, district_col, color_col = st.columns([1, 1, 1])

        with city_col:
            city_list = st.multiselect(
            '縣市',
            dp.get_city_list(), ['臺北市']) # on_change
            
        with district_col:
            place = st.selectbox(
            '市區',
            dp.get_place_list_by_city_list(city_list))

        with color_col:
            palettes = cm.list_colormaps()
            palette = st.selectbox("圖表顏色", palettes, index=palettes.index("Blues"))

    
        basic_submited = st.form_submit_button("預測房價")

    

    # 基礎預測房價
    if(basic_submited ):
        # 資料轉換
        place_id = dp.get_place_id(place)
        building_type_id = dp.get_building_type_id(building_type)
        type_id = dp.get_type_id(type)
        year_month = year + month

        # 取得compate_data 作為input_data
        input_data = cpm.compare_value_2(place_id, Transfer_Total_Ping, building_type_id)
        kwargs = {  "Place_id": place_id, "Building_Types" : building_type_id,"Type" : type_id,
            "Month" : int(year_month),
            "Transfer_Total_Ping" : Transfer_Total_Ping,"min_floors_height": min_floors_height, 
            "house_age": house_age, 
            "trading_floors_count" : 1, "Note_Relationships" : 0} # 預設值
        for key, value in kwargs.items():
            input_data[key][0] = value

        # 儲存資料
        for key in input_data.columns:
            st.session_state[key] = input_data[key][0]
        st.session_state['had_input_data_state'] = True

        st.write("Debug: 輸入模型的資料")
        st.dataframe(input_data) 



    adv_expand = False 
    if(basic_submited):
        adv_expand = False
    # if(st.session_state['FormSubmitter:進階搜尋表單-進階搜尋']):
    #     adv_expand = True


    with st.expander("進階搜尋", expanded= adv_expand ):
        with st.form("進階搜尋表單"):
            st.session_state['expander'] = True

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

            # building_total_floors_col = st.columns([1])
            # with building_total_floors_col:
            building_total_floors = st.number_input('房子總高度',  key = "building_total_floors", step=1)

            
            room_col, hall_col, bathroom_col = st.columns([1, 1, 1])
            with room_col:
                room = st.number_input('房',  key = "room", step=1 ) 
            with hall_col:
                hall = st.number_input('廳',  key = "hall", step=1)
            with bathroom_col:
                bathroom = st.number_input('衛',  key = "bathroom", step=1) 

            advanve_kwargs = {
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
            
            #　adv_submited = st.form_submit_button("進階搜尋", on_click=on_advanced_summit, kwargs=advanve_kwargs)
            adv_submited = st.form_submit_button("進階搜尋", on_click=on_advanced_summit)

    # st.session_state


    # 預測房價
    if(adv_submited):
        # 資料轉換
        place_id = dp.get_place_id(place)
        building_type_id = dp.get_building_type_id(building_type)
        type_id = dp.get_type_id(type)
        year_month = year + month

        # 是否有基礎搜尋過
        if 'had_input_data_state' not in st.session_state:
            st.session_state['had_input_data_state'] = False

        # 是否要compate_data 作為input_data
        if(not st.session_state['had_input_data_state'] ):
            # 取得compate_data 作為input_data
            input_data = cpm.compare_value_2(place_id, Transfer_Total_Ping, building_type_id)
            kwargs = {  "Place_id": place_id, "Building_Types" : building_type_id,"Type" : type_id,
                "Month" : int(year_month),
                "Transfer_Total_Ping" : Transfer_Total_Ping,"min_floors_height": min_floors_height, 
                "house_age": house_age, 
                "trading_floors_count" : 1, "Note_Relationships" : 0} # 預設值
            for key, value in kwargs.items():
                input_data[key][0] = value

            st.session_state['had_input_data_state'] = True
        # 讀取存檔
        else:
            row = {}
            for key in compare_data.columns:
                row[key] = st.session_state[key] 
            input_data = pd.DataFrame(row, index=[0])

        for key, value in advanve_kwargs.items():
            input_data[key][0] = value
        
        
        # 儲存資料
        # for key in input_data.columns:
        #     st.session_state[key] = input_data[key][0]
        #　st.session_state['had_input_data_state'] = True
        st.write("Debug: 輸入模型的資料")
        st.dataframe(input_data) 

    if(adv_submited | basic_submited):

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