import streamlit as st
import geovista as gv
from stpyvista import stpyvista
import numpy as np
from stpyvista_utils import is_embed, is_xvfb
import colorcet as cc
# from multiprocessing import Pool
import asyncio
import rasterio

@st.cache_resource
def get_grid(filename:str):
    with rasterio.open(filename) as src:
        band = src.read(1)
        left, bottom, right, top = src.bounds
        res = src.res
        x = np.arange(left, right, res[0])
        y = np.arange(top, bottom, -res[1])

    return gv.Transform.from_1d(x,y, data=np.ma.masked_equal(band, 0), name="Temperature [C]")

@st.cache_resource
def stpv_add_raster(filename):
    plotter = gv.GeoPlotter()
    plotter.window_size = [600, 600]
    plotter.set_background("#0e1117")
    plotter.add_base_layer(texture=gv.blue_marble())
    plotter.add_graticule(mesh_args=dict(color="pink", opacity=0.4))
    plotter.add_coastlines(color="white", line_width=8, resolution="50m")
    plotter.view_xz(negative=False)

    plotter.add_text(
        "NOOA National Weather Service \n\n"
        "https://www.cpc.ncep.noaa.gov/products/GIS/GIS_DATA/",
        position="lower_edge",
        color="pink",
        font_size=9,
        shadow=True,
    )

    blob = get_grid(filename)
    plotter.add_mesh(
        blob, 
        show_edges=False, 
        line_width=4, 
        style='surface', 
        cmap="coolwarm",
        name="Temperature",
        nan_color="w",
        nan_opacity=0,
        clim=[-20,20]
    )
    return plotter

async def build_column(column, tiff):
    TIFF = {
        "Min": "assets/tiff/us.tmin_nohads_ll_20231224_float.tif",
        "Max": "assets/tiff/us.tmax_nohads_ll_20231224_float.tif"
    }

    with column:
        with st.spinner("🌎🌍🌏..."):
            # await asyncio.sleep(10)
            earth = stpv_add_raster(TIFF.get(tiff))
            # earth.actors['Temperature'].visibility = visible_layer_min
            
            message = "Minimum" if tiff == "Min" else "Maximum"

            earth.add_text(
                f"🌎 {message}",
                position="upper_left",
                color="w",
                font_size=16,
                shadow=True,
            )

            stpyvista(
                earth,
                panel_kwargs=dict(
                    orientation_widget=True, 
                    interactive_orientation_widget=True
                )
            )

    return True

async def main():

    # Initial configuration
    if "IS_APP_EMBED" not in st.session_state:
        st.session_state.IS_APP_EMBED = is_embed()
    IS_APP_EMBED = st.session_state.IS_APP_EMBED

    st.set_page_config(
        page_title="stpyvista + geovista",
        page_icon="🧊", 
        layout="wide", 
        initial_sidebar_state="collapsed")

    if "IS_XVFB_RUNNING" not in st.session_state:
        IS_XVFB_RUNNING = is_xvfb()
        st.session_state.IS_XVFB_RUNNING = IS_XVFB_RUNNING
        
        # Inform xvfb status with a toast
        if not IS_APP_EMBED: st.toast(IS_XVFB_RUNNING.message, icon=IS_XVFB_RUNNING.icon)

    IS_XVFB_RUNNING = st.session_state.IS_XVFB_RUNNING

    # Add some styling with CSS selectors
    with open("assets/style.css") as f:
        st.markdown(f"""<style>{f.read()}</style>""", unsafe_allow_html=True)

    # Add badges to sidebar
    if not IS_APP_EMBED:
        with open("assets/badges.md") as f:
            st.markdown(f"""{f.read()}""", unsafe_allow_html=True)

    if "rendered" not in st.session_state:
        st.session_state.rendered = [False, False]

    cols = st.columns([0.5,2]) if not IS_APP_EMBED else st.columns([1,0.01])

    with cols[0]:
        if IS_APP_EMBED:
            st.markdown(
                """<p class="embed_message" style="text-align:right;">Launch <b>fullscreen</b> to explore &emsp; <b>⇲</b></>""",
                unsafe_allow_html=True
            )
            
        with st.expander("▛", expanded=True):
            st.title("🧊 + 🌎")
            st.header("`stpyvista` + `geovista`")
            "##### Show PyVista 3D visualizations in Streamlit"
            "***"
            "## 🧑‍🎄"
            st.markdown(
                "**CONUS Temperature** <br /> **on Christmas Eve**",
                unsafe_allow_html=True
            )

            st.caption(
                "Data from <br /> [NOOA National Weather Service](https://www.cpc.ncep.noaa.gov/products/GIS/GIS_DATA/)",
                unsafe_allow_html=True
            )        
            
            st.markdown("""
                <p style="text-align:right;">▟</>
                        """,unsafe_allow_html=True)

    if not IS_APP_EMBED:
        with cols[1]:

            btn_container = st.empty()

            if not all(st.session_state.rendered):
                btn = btn_container.button(
                    "Click here to load", 
                    use_container_width=True,
                    help="This might take a while depending on your device"
                )
            else:
                btn = True

            if btn:
                subcols = btn_container.columns(2)
                
                # async with asyncio.TaskGroup() as tg:
                #     e1 = tg.create_task(build_column(subcols[0], "Min"))
                #     e2 = tg.create_task(build_column(subcols[1], "Max"))
                
                # print(e1, e2)
                
                st.session_state.rendered = await asyncio.gather(
                    build_column(subcols[0], "Min"),
                    build_column(subcols[1], "Max")
                )


if __name__ == "__main__":
    asyncio.run(main())