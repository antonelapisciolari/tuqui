import streamlit as st
from navigation import make_sidebar
import pandas as pd
from page_utils import apply_page_config
import modules.tables as db
from modules.data_base import get, updateEstadoPedido
from datetime import datetime

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

st.title("📋 Pedidos")

filtros, refresh = st.columns([3, 1])

# Cargar pedidos y detalles
if "df_pedidos" not in st.session_state:
    st.session_state["df_pedidos"] = pd.DataFrame(get(db.pedidosTable) or [])

if "df_detalle" not in st.session_state:
    st.session_state["df_detalle"] = pd.DataFrame(get(db.detallePedidoTable) or [])

with refresh:
    if st.button("🔄 Refrescar Pedidos"):
        st.session_state.pop("df_pedidos", None)
        st.session_state.pop("df_detalle", None)
        st.rerun()

df = st.session_state["df_pedidos"]
detalle = st.session_state["df_detalle"]

if not df.empty:
    df = df.dropna(how='all')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['Fecha'] = df['created_at'].dt.strftime('%d/%m/%Y')

    if not detalle.empty:
        productos = pd.DataFrame(get(db.productoTable))
        detalle = detalle.merge(productos[['id', 'nombre']], left_on='nroProducto', right_on='id', how='left')
    
    with filtros:
        filtro = st.radio("📌 Filtrar pedidos por:", ("Solo de hoy", "Listos de hoy"), horizontal=True)

    hoy_str = datetime.now().strftime("%d/%m/%Y")

    if filtro == "Solo de hoy":
        df = df[(df["Fecha"] == hoy_str) & (df["estado"] == "Abierto")]
    elif filtro == "Listos de hoy":
        df = df[(df["Fecha"] == hoy_str) & (df["estado"] == "Listo")]

    if df.empty:
        st.warning("⚠️ No hay pedidos que coincidan con los filtros seleccionados.")
    else:
        st.subheader("📦 Pedidos")
        for index, row in df.iterrows():

            detalle_pedido = detalle[detalle["nroPedido"] == row["id"]][["nombre", "cantidad"]]
            detalle_pedido = detalle_pedido.rename(columns={"nombre": "Producto", "cantidad": "Cantidad"})

            estado = row["estado"]
            icono_estado = {
                "Abierto": "🟠",
                "Listo": "🔵",
                "Entregado": "🟢"
            }.get(estado, "❔")

            with st.expander(f"{icono_estado} Pedido #{row['id']} - {row['cliente']}"):
                st.write(f"📅 Fecha: {row['Fecha']}")
                st.write(f"🧞 Nombre: {(row['cliente'])}")
                st.write(f"📞 Teléfono: {(row['telefono'])}")
                st.write(f"📝 Total $: {row['total']}")
                st.write(f"Productos:")
                col1, col2 = st.columns([2,3])
                with col1:
                    st.dataframe(detalle_pedido, hide_index=True)
                st.markdown(f"**📌 Estado:** `{estado}`")

                if estado == "Abierto":
                    if st.button(f"✅ Marcar como Listo (Pedido #{row['id']})", key=f"boton_listo_{index}"):
                        updateEstadoPedido(row['id'], "Listo")
                        st.session_state.pop("df_pedidos", None)
                        st.session_state.pop("df_detalle", None)
                        st.success(f"Pedido #{row['id']} marcado como Listo ✅")
                        st.rerun()
                elif estado == "Listo":
                    if st.button(f"🚚 Marcar como Entregado (Pedido #{row['id']})", key=f"boton_entregado_{index}"):
                        updateEstadoPedido(row['id'], "Entregado")
                        st.session_state.pop("df_pedidos", None)
                        st.session_state.pop("df_detalle", None)
                        st.success(f"Pedido #{row['id']} marcado como Entregado ✅")
                        st.rerun()

else:
    st.info("Aquí encontrarás tus pedidos. Todavía no tienes pedidos cargados.")
