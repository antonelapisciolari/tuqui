import streamlit as st
from datetime import datetime
from streamlit_calendar import calendar
import pandas as pd
from datetime import timedelta
import importlib

def createCalendario(eventos):
    with st.container():
        st.subheader("Agenda")
        events = create_events(eventos)
        today = datetime.today().strftime('%Y-%m-%d')
        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridDay,dayGridWeek,dayGridMonth",
            },
            "initialDate": today,
            "initialView": "dayGridMonth",
            "locale":"ES"
        }
        custom_css = """
            .fc-toolbar-title {
                font-size: 1.5rem;  /* Adjust the title size */
            }
            .fc {
                width: 70%;  /* Set calendar width to 70% of the container for desktop */
                margin: 0 auto;
            }
            .fc-view {
                min-height: 250px;  /* Set a minimum height */
            }
            
            /* Responsive adjustments for smaller screens */
            @media only screen and (max-width: 768px) {
                .fc {
                    width: 100%;  /* Full width for mobile */
                }
                .fc-toolbar-title {
                    font-size: 1.2rem;  /* Adjust the title size for mobile */
                }
            }
        """
        details_placeholder = st.empty()
        selected_date = calendar(
            events, 
            options=calendar_options,
            custom_css=custom_css,
            callbacks = ["eventClick"]
        )

        if selected_date:
            details_placeholder.markdown(f"**Evento:** {selected_date['eventClick']['event']['title']}\n**Dia:** {selected_date['eventClick']['event']['start']}")


def create_events(df, title_template=None, duration_minutes=60):
    events = []
    for _, row in df.iterrows():
        # Combinar fecha + hora
        start_datetime = pd.to_datetime(f"{row['fecha']} {row['hora']}")
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)

        if title_template:
            title = title_template.format(**row)
        else:
            title = f"{row['titulo']} - {row['email_candidato']}"

        # Evento
        event = {
            "start":  start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "end":  end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "title": title,
            "psicologo":f"{row['email_psicologo']}"
        }
        events.append(event)
    return events

def getLanguage(userLang):
    lang_module = importlib.import_module(f"location.{userLang}")
    t = lang_module.texts
    return t