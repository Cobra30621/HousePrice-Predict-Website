import streamlit as st


def create_sidebar():
    st.set_page_config(layout="wide")

    st.sidebar.title("關於網站")
    st.sidebar.info(
        """
        台灣房價預測專案。\n
        本網站只供作參考資料用途，目的是讓使用者對台灣房價有一定的了解，不對使用者之投資決策負任何責任。\n
        資料來源 : [內政部實價登錄資料](https://plvr.land.moi.gov.tw/DownloadOpenData)
        """
    )
    

    st.sidebar.title("團隊成員")
    st.sidebar.info(
        """
        [Eli Chen](), 
        [Sam Shen](),
        [Martin Lee](), 
        [Cobra Chen](), 
        [Allen Shiah](), \n
        指導: [Adms Chung](https://www.linkedin.com/in/admsc/)
        """
    )
    
    st.sidebar.title("聯絡我們")
    st.sidebar.success(
        """
        聯絡方式 : OAO\n
        [GitHub](https://github.com/Cobra30621/-TWDS2022-HousePrice-Predict) 
        """
    )

    st.sidebar.write("---")