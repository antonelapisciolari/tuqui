import streamlit as st
from modules.data_base import getEqual,get

# Cargar datos del usuario desde Supabase y guardar en session_state
def load_user(email):
    response = getEqual("users", "email", email)
    if response:
        user = response[0]
        st.session_state.username = user["name"]
        st.session_state.logged_in = True
        return True
    return False

def is_authenticated():
    return (
        st.session_state.get("logged_in") or
        (hasattr(st, "user") and st.user and st.user.is_logged_in)
    )

def validate_get_user():
    if hasattr(st, "user") and st.user and st.user.is_logged_in:
        if "role" not in st.session_state:
            email = st.user.email
            if load_user(email):
                print('user loaded correctly')
                return True
            else:
                st.error("Tu cuenta de Google no está autorizada.")
                st.stop()

# Verificación inicial en cualquier página protegida
def is_logged():
    if not is_authenticated():
        st.warning("Redirigiendo al inicio de sesión...")
        st.session_state.logged_in = False
        st.session_state.redirected = True
        st.switch_page("app.py")
