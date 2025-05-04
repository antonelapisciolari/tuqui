import streamlit as st
from navigation import make_sidebar
import pandas as pd
from page_utils import apply_page_config
from modules.data_base import get, add

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

# Variables de sesión
if "pedido_guardado" not in st.session_state:
    st.session_state.pedido_guardado = False
if "productos_cliente" not in st.session_state:
    st.session_state.productos_cliente = []

st.title("📦 Ventas")
tabla_ventas = "ventas"
tabla_detalle = "detalleVenta"
productoTable = "producto"
formaPagoTabla = "formaPago"

productos_data = get(productoTable)
forma_pago = get(formaPagoTabla)

if productos_data:
    productos_df = pd.DataFrame(productos_data)
    if not productos_df.empty and "nombre" in productos_df.columns:
        productos_df = productos_df.dropna(subset=["nombre"])
        productos_disponibles = productos_df["nombre"].tolist()
        precios_dict = dict(zip(productos_df["nombre"], productos_df["precio"]))

if not productos_disponibles:
    st.warning("⚠️ No hay productos cargados aún.")
else:
    if not st.session_state.pedido_guardado:
        botonAgregar, botonNuevo = st.columns([3, 1])
        with botonAgregar:
            st.subheader("Agregar producto")
        with botonNuevo:
            if st.button("🔄 Nueva Venta"):
                st.rerun()

        col1, col2, col3 = st.columns([3, 1, 1])
        producto_seleccionado = col1.selectbox("Producto", productos_disponibles, key="producto_actual")
        cantidad = col2.number_input("Cantidad", min_value=1, step=1, key="cantidad_actual")

        with col3:
            precio_unitario = precios_dict.get(producto_seleccionado, 0)
            st.write('')
            st.subheader(f"Precio: ${precio_unitario:.2f}")

        subtotal = precio_unitario * cantidad
        st.write(f"Subtotal: ${subtotal:.2f}")

        if st.button("➕ Agregar producto"):
            producto_id = productos_df[productos_df["nombre"] == producto_seleccionado]["id"].values[0]
            st.session_state.productos_cliente.append({
                "producto_id": int(producto_id),
                "producto": producto_seleccionado,
                "cantidad": cantidad,
                "subtotal": subtotal,
            })
            st.rerun()

        if st.session_state.productos_cliente:
            st.subheader("📝 Productos agregados:")
            total_general = 0

            for idx, p in enumerate(st.session_state.productos_cliente):
                total_general += p["subtotal"]
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"- {p['producto']} x{p['cantidad']} → ${p['subtotal']:.2f}")
                with col2:
                    if st.button("❌", key=f"delete_{idx}"):
                        st.session_state.productos_cliente.pop(idx)
                        st.rerun()

            st.markdown(f"### 💵 Total del pedido: ${total_general:.2f}")

            forma_pago_opciones = [fp["formaPago"] for fp in forma_pago]
            forma_pago_seleccionada = st.selectbox("Forma de pago", forma_pago_opciones, key="forma_pago_actual", index=1)
            forma_pago_id = [fp["id"] for fp in forma_pago if fp["formaPago"] == forma_pago_seleccionada][0]

            if st.button("💾 Guardar pedido"):
                # 1. Guardar en tabla VENTAS
                venta_data = {
                    "formaPago": forma_pago_id,
                    "total": total_general
                }
                venta_id = add(tabla_ventas, venta_data)
                if venta_id:
                    for p in st.session_state.productos_cliente:
                        detalle_data = {
                            "ventaId": venta_id.data[0]["id"],
                            "producto": p["producto_id"],
                            "cantidad": p["cantidad"],
                            "subtotal": p["subtotal"]
                        }
                        add(tabla_detalle, detalle_data)

                    st.toast("✅ Pedido guardado con éxito", icon="💾")
                    st.session_state.productos_cliente = []
        else:
            total_general = 0
