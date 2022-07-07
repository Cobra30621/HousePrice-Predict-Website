import streamlit as st


def create_sidebar():
    st.set_page_config(layout="wide")

    st.sidebar.title("About")
    st.sidebar.info(
        """
        台灣房價預測專案。\n
        資料來源 : 台灣時價登陸
        """
    )

    st.sidebar.title("Contact")
    st.sidebar.info(
        """
        Qiusheng Wu: <https://wetlands.io>
        [GitHub](https://github.com/giswqs) | [Twitter](https://twitter.com/giswqs) | [YouTube](https://www.youtube.com/c/QiushengWu) | [LinkedIn](https://www.linkedin.com/in/qiushengwu)
        """
    )