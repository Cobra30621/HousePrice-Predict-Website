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


def app():
    cp.create_sidebar()

    st.title("【首頁】台灣房價地圖")
    st.markdown(
        """**模型與網站介紹:**
    """
    )

app()