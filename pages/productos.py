import streamlit as st
from navigation import make_sidebar
import pandas as pd
from page_utils import apply_page_config
from modules.data_base import get, add
import modules.tables as db 

# Configuración inicial
apply_page_config()

# Control de acceso
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Sesión expirada. Redirigiendo a login...")
    st.session_state.logged_in = False 
    st.session_state.redirected = True 
    st.switch_page("app.py")
else:
    make_sidebar()


st.title("📦 Productos Y Clientes")

# 🆕 Cargar productos
if "productos" not in st.session_state:
    st.session_state.productos = get(db.productoTable)

if "clientes" not in st.session_state:
    st.session_state.clientes = get(db.clientesTable)
# Botón refrescar
if st.button("🔄 Refrescar"):
    st.session_state.productos = get(db.productoTable)
    st.session_state.clientes = get(db.clientesTable)

productos = st.session_state.productos
prods = pd.DataFrame(productos)

clientes = st.session_state.clientes
clients = pd.DataFrame(clientes)
# Solo si hay productos
if not prods.empty:
    with st.expander("Lista Productos"):
        columnas_visibles = {
            "nombre": "Producto",
            "precio": "Precio"
        }
        prods = prods[list(columnas_visibles.keys())]  # Filtramos las columnas deseadas
        prods.rename(columns=columnas_visibles, inplace=True)
        st.dataframe(prods, use_container_width=True, hide_index=True)
else:
    st.info("Todavía no hay productos cargados.")

# 🆕 Formulario para agregar nuevo producto
with st.expander("Agregar nuevo producto", expanded=False):
    with st.form("form_nuevo_producto"):
        nombre = st.text_input("Nombre del producto").strip()
        precio = st.text_input("Precio")
        agregar_producto = st.form_submit_button("Agregar producto")

    if agregar_producto:
        if nombre and precio:
            data = {
                "nombre": nombre,
                "precio": precio
            }
            try:
                add(db.productoTable, data)
                st.success(f"Producto '{nombre}' creado correctamente.")
                st.session_state.productos = get(db.productoTable) 
                st.rerun()
            except Exception as e:
                st.error(f"Ocurrió un error al guardar el producto: {e}")
        else:
            st.warning("Por favor completá todos los campos.")
st.divider()

if not clients.empty:
    with st.expander("Lista Clientes"):
        columnas_visibles = {
            "nombre": "Nombre",
            "direccion": "Direccion",
            "telefono": "Telefono"
        }
        clients = clients[list(columnas_visibles.keys())]  # Filtramos las columnas deseadas
        clients.rename(columns=columnas_visibles, inplace=True)
        st.dataframe(clients, use_container_width=True, hide_index=True)
else:
    st.info("Todavía no hay clientes cargados.")

# 🆕 Formulario para agregar nuevo cliente
with st.expander("Agregar nuevo cliente", expanded=False):
    with st.form("form_nuevo_cliente"):
        nombre = st.text_input("Nombre").strip()
        direccion = st.text_input("Direccion").strip()
        telefono = st.text_input("Telefono").strip()
        agregar_cliente = st.form_submit_button("Agregar cliente")

    if agregar_cliente:
        if nombre:
            data = {
                "nombre": nombre,
                "direccion": direccion,
                "telefono": telefono
            }
            try:
                add(db.clientesTable, data)
                st.success(f"Cliente '{nombre}' creado correctamente.")
                st.session_state.clientes = get(db.clientesTable) 
                st.rerun()
            except Exception as e:
                st.error(f"Ocurrió un error al guardar el cliente: {e}")
        else:
            st.warning("Por favor completá todos los campos.")