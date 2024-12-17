import streamlit as st
from time import sleep

import geovista as gv
import numpy as np
import colorcet as cc  # noqa
import rasterio

from stpyvista.utils import is_the_app_embedded, start_xvfb
from stpyvista import stpyvista

TIFF = {
    "Min": "assets/tiff/us.tmin_nohads_ll_20231224_float.tif",
    "Max": "assets/tiff/us.tmax_nohads_ll_20231224_float.tif",
}

###############################################################################
# Processing and caching
###############################################################################


@st.cache_resource(show_spinner=False)
def get_grid(filename: str):
    with rasterio.open(filename) as src:
        band = src.read(1)
        left, bottom, right, top = src.bounds
        res = src.res
        nodata = 0.0

        x = np.arange(left, right + res[0], res[0])
        y = np.arange(top, bottom - res[1], -res[1])

    return gv.Transform.from_1d(
        x, y, data=np.ma.masked_values(band, nodata), name="Temperature [C]"
    )


@st.cache_resource(show_spinner=False)
def stpv_build_geoplotter(dummy: str = "planet"):
    plotter = gv.GeoPlotter(shape=[1, 2], off_screen=True)
    plotter.window_size = [800, 500]
    plotter.set_background("#0e1117")

    blobs = [get_grid(tiff) for tiff in TIFF.values()]
    labels = ["🌎 Minimum", "🌎 Maximum"]

    for i, (label, blob) in enumerate(zip(labels, blobs)):
        plotter.subplot(0, i)
        plotter.add_base_layer(texture=gv.blue_marble())
        plotter.add_graticule(mesh_args=dict(color="pink", opacity=0.4))
        plotter.add_coastlines(color="white", line_width=8, resolution="50m")
        plotter.view_xz(negative=False)

        plotter.add_mesh(
            blob,
            show_edges=False,
            line_width=4,
            style="surface",
            cmap="coolwarm",
            name="Temperature",
            nan_color="w",
            nan_opacity=0,
            clim=[-20, 20],
        )

        plotter.add_text(
            label,
            position="upper_left",
            color="w",
            font_size=16,
            shadow=True,
        )

    plotter.link_views()
    return plotter


###############################################################################
# Streamlit App
###############################################################################


def add_info():
    with st.expander("▛", expanded=True):
        st.title("🧊 + 🌎", anchor=False)
        st.header("`stpyvista` + `geovista`", anchor=False)
        st.markdown("**Show PyVista 3D visualizations in Streamlit**")

        st.divider()

        st.header("🧑‍🎄", anchor=False)
        st.markdown("**CONUS Temperature** \n **on Christmas Eve**")

        st.caption(
            "Data from <br /> [NOAA National Weather Service](https://www.cpc.ncep.noaa.gov/products/GIS/GIS_DATA/)",
            unsafe_allow_html=True,
        )

        st.divider()

        # Add badges
        st.html("assets/badges.html")

        st.html("""<p style="text-align:right;">▟</>""")


def embedded():
    st.session_state.IS_APP_EMBEDDED = True

    st.html(
        """<p class="embed_message" style="text-align:right;">Launch <b>fullscreen</b> to explore &emsp; <b>⇲</b></>""",
    )

    add_info()


def main():
    if "started_xvfb" not in st.session_state:
        start_xvfb()
        st.session_state.started_xvfb = True

    if "rendered" not in st.session_state:
        st.session_state.rendered = False

    cols = st.columns([0.5, 2])

    with cols[0]:
        add_info()

    with cols[1]:
        btn_container = st.empty()

        if not st.session_state.rendered:
            btn = btn_container.button(
                "Click here to load",
                use_container_width=True,
                help="This might take a while depending on your device",
                type="primary",
            )

        else:
            btn = True

        if btn and not st.session_state.rendered:
            btn_container.empty()

            with st.status("Building `GeoPlotter`...", expanded=True) as status:
                with (placeholder := st.empty()):
                    st.html('<p style="text-align: center; font-size:4rem">🌎</p>')
                    sleep(1)

                earths = stpv_build_geoplotter()
                status.update(label="Sending to `stpyvista`...", expanded=True)

                with placeholder:
                    stpyvista(
                        earths,
                        panel_kwargs=dict(
                            orientation_widget=True,
                            interactive_orientation_widget=True,
                        ),
                    )

                st.session_state.rendered = True
                status.update(label="Ready!", state="complete", expanded=True)


###############################################################################
# Initialize
###############################################################################

if __name__ == "__main__":
    st.set_page_config(
        page_title="stpyvista + geovista",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    if is_the_app_embedded():
        embedded()

    else:
        main()

    # Add some styling with CSS selectors
    with open("assets/style.css") as f:
        st.html(f"<style>{f.read()}</style>")
