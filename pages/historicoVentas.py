import streamlit as st
from navigation import make_sidebar
from page_utils import apply_page_config
import pandas as pd
from modules.data_base import get
import modules.tables as db
# Configuración inicial
st.session_state["current_page"] = "historico"
apply_page_config()

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Sesión expirada. Redirigiendo a login...")
    st.session_state.logged_in = False 
    st.session_state.redirected = True 
    st.switch_page("app.py")
else:
    make_sidebar()

st.title("📋 Histórico Ventas")

# Carga de datos
df_ventas = pd.DataFrame(get(db.ventasTable))
df_detalle = pd.DataFrame(get(db.detalleVentaTable))
productos_data = get(db.productoTable)
productos = pd.DataFrame(productos_data)
formas_pago_data = get(db.formaPagoTabla)
formas_pago = pd.DataFrame(formas_pago_data)
cliente_data = get(db.clientesTable)
clientes = pd.DataFrame(cliente_data)
filtros, refresh = st.columns([3, 1])
with refresh:
    st.text('')
    if st.button("🔄 Refrescar Ventas"):
        st.rerun()

# Si hay ventas
if not df_ventas.empty:
    df = df_ventas.dropna(how='all')
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['Fecha'] = df['created_at'].dt.strftime('%d/%m/%Y')

    # Agregamos nombre de forma de pago
    if not formas_pago.empty and 'id' in formas_pago and 'formaPago' in formas_pago:
        df = df.merge(
            formas_pago[['id', 'formaPago']],
            left_on='formaPago',
            right_on='id',
            how='left',
            suffixes=('', '_forma_pago')
        )
        df.rename(columns={'formaPago_forma_pago': 'Forma de Pago'}, inplace=True)
    
    
    if not clientes.empty and 'id' in clientes and 'nombre' in clientes and 'cliente' in df:
        df = df.merge(
            clientes[['id', 'nombre']],
            left_on='cliente',       # Esta columna tiene el ID del cliente
            right_on='id',           # Esta columna en `clientes` también es el ID
            how='left',
            suffixes=('', '_cliente')
        )
        # Renombrar la columna 'nombre' agregada del merge para claridad
        df.rename(columns={'nombre': 'Cliente'}, inplace=True)

    # Procesar detalle
    if not df_detalle.empty and not productos.empty:
        detalle = df_detalle.merge(productos[['id', 'nombre']], left_on='producto', right_on='id', how='left')

        # Agrupar por venta
        detalle_grouped = (
            detalle.groupby("ventaId")[["nombre", "cantidad"]]
            .apply(lambda x: ", ".join(f"{row['nombre']} x{row['cantidad']}" for _, row in x.iterrows()))
            .reset_index(name="Detalle Venta")
        )

        df = df.merge(detalle_grouped, left_on="id", right_on="ventaId", how="left")

        # 🔍 Filtros por producto y forma de pago
        with filtros:
            producto, pago= st.columns(2)
            with producto:
                producto_opciones = sorted(productos["nombre"].unique().tolist())
                filtro_producto = st.selectbox("Filtrar por producto", ["Todos"] + producto_opciones)
            with pago:
                forma_pago_opciones = sorted(formas_pago["formaPago"].unique().tolist())
                filtro_forma_pago = st.selectbox("Filtrar por forma de pago", ["Todos"] + forma_pago_opciones)

        # Aplicar filtros
        if filtro_producto != "Todos":
            df = df[df["Detalle Venta"].str.contains(filtro_producto, na=False)]

        if filtro_forma_pago != "Todos":
            df = df[df["Forma de Pago"] == filtro_forma_pago]

        # Columnas a mostrar
        columnas_a_mostrar = [
            "Fecha",
            "Detalle Venta",
            "Forma de Pago",
            "total",
            "Cliente" 
        ]
        columnas_presentes = [col for col in columnas_a_mostrar if col in df.columns]
        tabla_mostrar = df[columnas_presentes]

        st.subheader("📝 Ventas")
        st.dataframe(tabla_mostrar, use_container_width=True, hide_index=True)
    else:
        st.info("No hay productos o detalles de venta para mostrar.")
else:
    st.info("No hay ventas registradas aún.")
