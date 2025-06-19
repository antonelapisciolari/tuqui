import streamlit as st
import pandas as pd
import modules.tables as db
import logging
from modules.data_base import get, add
from variables import page_icon

st.set_page_config(
    page_title="Formulario Pedido",
    page_icon=page_icon,
    layout="wide",
)

# Variables de sesión
if "pedido_guardado" not in st.session_state:
    st.session_state.pedido_guardado = False

if "productos_cliente" not in st.session_state:
    st.session_state.productos_cliente = []

st.title("🍕 Qué vas a comer hoy?")

# Cargar productos desde Supabase

productos_data = get(db.productoTable)
productos_df = pd.DataFrame(productos_data) if productos_data else pd.DataFrame()

# Categorías definidas
categorias = ["Empanadas", "Pizza", "HotDogs", "Pastas", "Bebidas"]

# Agrupar productos por categoría
productos_por_categoria = {
    cat: productos_df[productos_df["categoria"] == cat] for cat in categorias
}
def mostrar_tarjetas(categoria, productos):
    with st.expander(categoria):
        for i in range(0, len(productos), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(productos):
                    prod = productos.iloc[i + j]
                    nombre = prod["nombre"]
                    precio = prod["precio"]
                    prod_id = f"{categoria}_{prod['id']}"

                    with cols[j]:
                        with st.container():
                            imagen_url = prod.get("imagen")
                            if not imagen_url or not isinstance(imagen_url, str) or not imagen_url.startswith("http"):
                                imagen_url = "https://placekitten.com/300/200"
                            st.image(imagen_url, use_container_width=True)
                            st.markdown(f"**{nombre}**")
                            st.markdown(f"💰 ${precio:.2f}")

                            col1, col2, col3 = st.columns(3)

                            if col1.button("➖", key=f"menos_{prod_id}"):
                                actualizar_cantidad(nombre, precio, -1)

                            cantidad_actual = obtener_cantidad(nombre)
                            col2.markdown(f"<h4 style='text-align: center'>{cantidad_actual}</h4>", unsafe_allow_html=True)

                            if col3.button("➕", key=f"mas_{prod_id}"):
                                actualizar_cantidad(nombre, precio, 1)


def obtener_cantidad(nombre):
    for item in st.session_state.productos_cliente:
        if item["producto"] == nombre:
            return item["cantidad"]
    return 0

def actualizar_cantidad(nombre, precio, delta):
    for item in st.session_state.productos_cliente:
        if item["producto"] == nombre:
            item["cantidad"] += delta
            if item["cantidad"] <= 0:
                st.session_state.productos_cliente.remove(item)
            else:
                item["subtotal"] = item["cantidad"] * precio
            break
    else:
        if delta > 0:
            st.session_state.productos_cliente.append({
                "producto": nombre,
                "cantidad": delta,
                "subtotal": delta * precio
            })
    st.rerun()

# Función para agregar producto al pedido
def agregar_producto(nombre, precio):
    for item in st.session_state.productos_cliente:
        if item["producto"] == nombre:
            item["cantidad"] += 1
            item["subtotal"] += precio
            break
    else:
        st.session_state.productos_cliente.append({
            "producto": nombre,
            "cantidad": 1,
            "subtotal": precio
        })

# Mostrar tarjetas por categoría
if productos_df.empty:
    st.warning("⚠️ No hay productos disponibles.")
else:
    for cat in categorias:
        productos_cat = productos_por_categoria.get(cat)
        if productos_cat is not None and not productos_cat.empty:
            mostrar_tarjetas(cat, productos_cat)

    # Mostrar resumen del pedido
    if st.session_state.productos_cliente:
        st.markdown("---")
        st.markdown("### 🛒 Productos agregados:")
        total_general = 0
        for p in st.session_state.productos_cliente:
            total_general += p["subtotal"]
            st.markdown(f"- {p['producto']} x{p['cantidad']} → ${p['subtotal']:.2f}")
        st.markdown(f"### 💵 Total del pedido: ${total_general:.2f}")
    else:
        total_general = 0

    # ----------------------
    # FORMULARIO DEL PEDIDO
    # ----------------------
    st.markdown("---")
    with st.form("formulario_pedido"):
        st.subheader("🧾 Datos del cliente")
        nombre = st.text_input("Nombre")
        telefono = st.text_input("Teléfono")
        enviar = st.form_submit_button("Pedir")

    if enviar:
        if not nombre.strip():
            st.error("⚠️ Ingresá el nombre del cliente.")
        elif not st.session_state.productos_cliente:
            st.error("⚠️ Debés agregar al menos un producto.")
        else:
            try:
                pedido_data = {
                    "cliente": nombre.strip(),
                    "telefono": telefono.strip(),
                    "estado": "Abierto",
                    "total": total_general
                }
                pedido_response = add(db.pedidosTable, pedido_data)
                nro_pedido = pedido_response.data[0]["id"]

                for p in st.session_state.productos_cliente:
                    producto_info = productos_df[productos_df["nombre"] == p["producto"]].iloc[0]
                    detalle_data = {
                        "nroProducto": int(producto_info["id"]),
                        "nroPedido": int(nro_pedido),
                        "cantidad": int(p["cantidad"]),
                        "precio": float(p["subtotal"])
                    }
                    add(db.detallePedidoTable, detalle_data)

                st.success("✅ El pedido fue enviado correctamente.")
                st.session_state.pedido_guardado = True
                st.session_state.productos_cliente = []
                st.rerun()

            except Exception as e:
                logging.error(e, stack_info=True, exc_info=True)
                st.error(f"❌ Error al enviar el pedido: {e}")

# Mostrar mensaje si el pedido ya fue enviado
if st.session_state.pedido_guardado:
    st.success("✅ El pedido fue enviado correctamente.")
    st.button("Cargar otro pedido", on_click=lambda: st.session_state.update({
        "pedido_guardado": False,
        "productos_cliente": []
    }))
