import matplotlib as mpl
import matplotlib.pyplot as plt
import pydeck as pdk
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb

def draw_map(gdf):
    selected_col = "price"

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

    return r

def draw_bar(price, min, max):
    fig, ax = plt.subplots(figsize=(6, 1))
    fig.subplots_adjust(bottom=0.5)
    cmap = mpl.cm.YlOrRd
    print(cmap)
    norm = mpl.colors.Normalize(vmin=0, vmax=1)
    print(norm )
    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                    cax=ax, orientation='horizontal', 
                    ticks=[0,  1])
                    # ticks=[0, 0.2, 0.4, 0.6, 0.8, 1])
    # ax.set_title("XX 的 在 OO市的房價")

    price_rate = (price - min) / ( max - min)
    price_rate = 0.5 + (price_rate - 0.5) * 0.95
    cbar.ax.set_xticklabels([min, max])   
    cbar.ax.plot([price_rate, price_rate], [0, 1], 'black', linewidth=2)
    cbar.ax.plot([price_rate, price_rate], [0.9, 1], color='grey', marker='v', linewidth=0.10)
    cbar.ax.plot([price_rate, price_rate], [0, 0.1], color='grey', marker='^', linewidth=0.10)
    return fig