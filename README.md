# TWDS-HousePrice-Predict

## 一、專案介紹

台灣房價預測網站。

[Demo](https://cobra30621--twds2022-houseprice-predict-app-ouieh6.streamlitapp.com/house_predit)



## 二、使用專案

### 1. 完整版

1. 下載本專案

```
git clone https://github.com/Cobra30621/HousePrice-Predict-Website
```

2. 下載requirements套件

```
pip install -r requirements.txt
```

3. 下載地圖繪製套件 geopandas
- 下載較為複雜，Window 版可以參考以下文章
    - [geopandas安装心得（win10）](https://zhuanlan.zhihu.com/p/137628480)
    - [Geopandas Installation— the easy way for Windows!](https://towardsdatascience.com/geopandas-installation-the-easy-way-for-windows-31a666b3610f)

4. 啟動網頁

```
streamlit run app.py       
```


### 2. 簡易版
沒有地圖的版本

1. 下載本專案

```
git clone https://github.com/Cobra30621/HousePrice-Predict-Website
```

2. 下載requirements套件

```
pip install -r requirements.txt
```

3. 啟動網頁

```
streamlit run app_no_map.py       
```

## 三、更新專案

### 1.換模型
- 將新模型放入model資料夾中
- 將app.py 的 model_path，改成新模型的路徑
- 如果使用別的模型(非LGBM)，將app.py中的loadModel()改成新模型的讀取方式


## 四、相關資料

### 1.網站

- 使用套件: Streamlit
    - [Streamlit是什麼?-Streamlit入門(1)](https://medium.com/@yt.chen/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92-%E8%B3%87%E6%96%99%E7%A7%91%E5%AD%B8%E6%A1%86%E6%9E%B6%E6%87%89%E7%94%A8-streamlit%E5%85%A5%E9%96%80-1-d07478cd4d8)
    - [Streamlit官網教學](https://docs.streamlit.io/library/get-started) 



