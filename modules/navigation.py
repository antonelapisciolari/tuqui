import streamlit as st
from modules.utils import getLanguage

lang = getLanguage(st.session_state.get("language", "es"))

def get_current_page_name():
    return st.session_state.get("current_page", "")

def render_menu(role):
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
        st.write(f"{lang['greetings']} {st.session_state.username}!")
        st.write("")
        
        if st.session_state.logged_in:
            if(role=="admin"):
                st.page_link("pages/dashboard_psicologos.py", label="Dashboard Psicólogos")
                st.page_link("pages/dashboard_admin.py", label="Dashboard Admin")
                
                st.write("")
                st.write("")

                if st.button(lang['logoutButton']):
                    st.logout()
            if(role=="pm"):
                st.page_link("pages/pm_datos_preliminares.py", label=lang['titlePreliminarData'])
                st.page_link("pages/pm_usuarios.py", label=lang['titleUsers'])
                st.page_link("pages/pm_clientes.py", label=lang['titleClients'])
                st.write("")
                st.write("")

                if st.button(lang['logoutButton']):
                    st.logout()
            if(role=="consultora"):
                st.page_link("pages/consultora_calendar.py", label=lang['titleCalendar'])
                st.page_link("pages/consultora_entrevista.py", label=lang['titleInterview'])
                st.write("")
                st.write("")

                if st.button(lang['logoutButton']):
                    st.logout()
        elif get_current_page_name() != "app":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("app.py")

