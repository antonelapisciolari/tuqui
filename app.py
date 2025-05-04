import streamlit as st
from modules.data_base import getEqual
from modules.session_manager import load_user, validate_get_user

st.set_page_config(page_title="Inicio", page_icon="🧠", layout="centered")
st.session_state["current_page"] = "streamlit_app"

# ✅ Si ya está logueado por cualquier medio, redirige
if st.session_state.get("logged_in"):
    st.switch_page("pages/ventas.py")
    st.stop()

# ✅ Si viene del login con Google y no hay sesión cargada aún
islogged = validate_get_user()
if islogged:
    st.switch_page("pages/ventas.py")

logo, login = st.columns(2)
with logo:
    st.image("images/tuqui-gif.gif")
with login:
    st.header("")
    st.markdown("<p style='font-size: 20px;'>Ingresá con tu cuenta de Google</p>", unsafe_allow_html=True)

    st.write("")

    # Botón de login con Google
    if st.button("Iniciar sesión con Google"):
        st.login("google")



