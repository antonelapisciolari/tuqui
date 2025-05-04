import streamlit as st
from time import sleep
def get_current_page_name():
    return st.session_state.get("current_page", "")


def make_sidebar():
    with st.sidebar:
        st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            width: 200px;  /* Adjust the width to your preference */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
        st.title("Menu")
        st.write(f"Hola {st.session_state.username}!")
        st.write("")
        st.write("")

        if st.session_state.get("logged_in", False):
            st.page_link("pages/ventas.py", label="Venta")
            st.page_link("pages/productos.py", label="Productos")
            st.page_link("pages/historicoVentas.py", label="Historico")
            st.page_link("pages/metricas.py", label="Metricas")
            st.write("")
            st.write("")

            if st.button("Desloguearse"):
                st.logout()

        elif get_current_page_name() != "app":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("app.py")


