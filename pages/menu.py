import streamlit as st
from modules.data_base import get
import modules.tables as db

st.set_page_config(page_title="Menú Tuqui")
st.title("📋 Menú - Tuqui")

menu_items = get(db.productoTable)


# Separar por categoría
comida = [item for item in menu_items if item["tipo"] == "Comida"]
bebida = [item for item in menu_items if item["tipo"] == "Bebida"]

tab1, tab2 = st.tabs(["🍽️ Comida", "🥤 Bebidas"])
with tab1:
    for subcat in sorted(set(item["categoria"] for item in comida)):
        st.subheader(f"🔸 {subcat}")
        for item in [x for x in comida if x["categoria"] == subcat]:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(item["imagen"], width=100)
            with col2:
                st.markdown(f"**{item['nombre']}** - ${item['precio']}")

with tab2:
    for item in bebida:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(item["imagen"], width=100)
            with col2:
                st.markdown(f"**{item['nombre']}** - ${item['precio']}")
st.divider()
col1, col2  =st.columns(2)
with col1:
    st.write("Sueca 78 - Ruzafa - Valencia")
with col2:
    st.write("@tuqui.food")