import streamlit as st
import pyvista as pv
import geovista as gv
from stpyvista import stpyvista
import numpy as np
from stpyvista_utils import is_embed, is_xvfb
import colorcet as cc

# Initial configuration
if "IS_APP_EMBED" not in st.session_state:
    st.session_state.IS_APP_EMBED = is_embed()
IS_APP_EMBED = st.session_state.IS_APP_EMBED

st.set_page_config(
    page_title="stpyvista",
    page_icon="🧊", 
    layout="wide" if IS_APP_EMBED else "centered", 
    initial_sidebar_state="collapsed" if IS_APP_EMBED else "expanded")

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
    with st.sidebar:
        with open("assets/badges.md") as f:
            st.markdown(f"""{f.read()}""", unsafe_allow_html=True)

# *******************************************************************
@st.cache_resource
def stpv_planet(dummy:str = "earth"):
    x = np.arange(-180, 182, 2)
    y = np.arange(90, -92, -2)
    xx,yy = np.meshgrid(x, y)
    data = np.abs(yy)

    blob = gv.Transform.from_1d(
        x,y, data=data, name="Distance to Equator"
        # radius=gv.common.RADIUS * 1.05
        # zlevel=1, zscale=0.50
    )

    # if "natural_earth" not in st.session_state:
    #     # st.session_state.natural_earth = gv.natural_earth_1()
    #     st.session_state.natural_earth = gv.blue_marble()

    # if "plotter" not in st.session_state:

    plotter = gv.GeoPlotter()
    plotter.window_size = [600, 600]
    plotter.set_background("#0e1117")
    # # Force zlevel alignment of coastlines and base layer.
    # plotter.add_base_layer(texture=st.session_state.natural_earth, zlevel=0)
    plotter.add_graticule(mesh_args=dict(color="pink", opacity=0.4))
    plotter.add_coastlines(color="white", line_width=8)
    plotter.view_xz(negative=False)
    plotter.add_text(
        "Earth",
        position="upper_left",
        color="w",
        font_size=18,
        shadow=True,
    )
    
    plotter.add_mesh(
        blob, 
        show_edges=False, 
        line_width=4, 
        style='surface', 
        cmap="bmy",
        name="blob"
    )

    return plotter

earth = stpv_planet()
with st.sidebar:
    st.title("🧊 `stpyvista`")
    st.subheader("Show PyVista 3D visualizations in Streamlit")
    visible_layer = st.sidebar.checkbox("Visible layer?", True)

earth.actors['blob'].visibility = visible_layer

stpyvista(
    earth,
    panel_kwargs=dict(
        orientation_widget=True, 
        interactive_orientation_widget=True
    )
)
