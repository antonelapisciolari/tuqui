from variables import page_icon
import streamlit as st
from modules.utils import getLanguage
from streamlit_calendar import calendar
lang = getLanguage(st.session_state.get("language", "es"))
def apply_page_config():
    st.set_page_config(
        page_title=lang['title'],
        page_icon=page_icon,  # You can use an emoji or a URL to an icon image
        layout="wide", # Optional: You can set the layout as "centered" or "wide"
        initial_sidebar_state="collapsed"
    )
    
    st.logo(page_icon,size="large")

def createCalendar(events):
      calendar_events = [
            {
                "title": e.get("summary", "Sin título"),
                "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date")),
                "end": e.get("end", {}).get("dateTime", e.get("end", {}).get("date"))
            }
            for e in events
        ]

      calendar_options = {
            "initialView": "dayGridMonth",
            "editable": False,
            "selectable": False,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay"
            }
        }
      custom_css = """
        .fc-toolbar-title {
            font-size: 1rem;  /* Adjust the title size */
        }
        .fc {
            width: 60%;  /* Set calendar width to 70% of the container for desktop */
            margin: 0 auto;
        }
        .fc-view {
            min-height: 200px;  /* Set a minimum height */
        }
        
        /* Responsive adjustments for smaller screens */
        @media only screen andter (max-width: 768px) {
            .fc {
                width: 100%;  /* Full width for mobile */
            }
            .fc-toolbar-title {
                font-size: 1.2rem;  /* Adjust the title size for mobile */
            }
        }
    """

      calendar(events=calendar_events, options=calendar_options,custom_css=custom_css)