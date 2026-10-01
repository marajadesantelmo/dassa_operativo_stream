import streamlit as st

NUEVA_URL = "https://apps.dassa.com.ar/orden/p/preingreso.html"

st.set_page_config(page_title="Preingreso Playón DASSA", page_icon="🚛", layout="centered")

st.image('logo.png')
st.warning("⚠️ Este formulario ya no está en uso. Fue reemplazado por una nueva versión.")
st.markdown(f"Por favor, continúe su preingreso en el siguiente enlace: [{NUEVA_URL}]({NUEVA_URL})")
st.link_button("Ir al nuevo formulario de Preingreso", NUEVA_URL, type="primary")

st.markdown(
    f'<meta http-equiv="refresh" content="5;url={NUEVA_URL}">',
    unsafe_allow_html=True,
)
st.caption("Será redirigido automáticamente en unos segundos...")
