import streamlit as st
import pandas as pd
from datetime import datetime
from modules.data_base import get
import plotly.express as px
from navigation import make_sidebar
from page_utils import apply_page_config
# Configuración inicial
st.session_state["current_page"] = "metricas"
apply_page_config()

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Sesión expirada. Redirigiendo a login...")
    st.session_state.logged_in = False 
    st.session_state.redirected = True 
    st.switch_page("app.py")
else:
    make_sidebar()

st.title("📈 Métricas de Ventas")

# Datos
ventas = pd.DataFrame(get("ventas"))
detalles = pd.DataFrame(get("detalleVenta"))
productos = pd.DataFrame(get("producto"))
formas_pago = pd.DataFrame(get("formaPago"))

# Convertir fechas
ventas['created_at'] = pd.to_datetime(ventas['created_at'])

# 📌 Filtro: solo ventas del mes actual
hoy = datetime.now()
ventas_mes = ventas[ventas['created_at'].dt.month == hoy.month]
ventaCol, producto = st.columns(2)

total_mes = ventas_mes["total"].sum()
with ventaCol: 
    st.metric("💰 Total ventas del mes", f"${total_mes:.2f}")

with producto:
    detalles_prod = detalles.merge(productos, left_on="producto", right_on="id")
    mas_vendido = detalles_prod.groupby("nombre")["cantidad"].sum().sort_values(ascending=False)
    producto_top = mas_vendido.idxmax()
    st.metric("🥇 Producto más vendido", f"{producto_top} ({mas_vendido.max()} unidades)") 
# 📈 Histórico de ventas por mes

ventas['Mes'] = ventas['created_at'].dt.to_period('M').astype(str)
ventas_mensuales = ventas.groupby('Mes')['total'].sum().reset_index()
fig_hist = px.line(ventas_mensuales, x="Mes", y="total", title="Histórico de Ventas")
st.plotly_chart(fig_hist, use_container_width=True)




# 📊 Porcentaje de productos vendidos (gráfico de torta)
prod_pct = mas_vendido / mas_vendido.sum() * 100
prod_pct = prod_pct.reset_index()
prod_pct.columns = ["Producto", "Porcentaje"]

fig_prod = px.pie(
    prod_pct,
    names="Producto",
    values="Porcentaje",
    title="% de productos vendidos"
)

st.plotly_chart(fig_prod, use_container_width=True)


# ⏰ Horas de venta
ventas['Hora'] = ventas['created_at'].dt.hour
ventas_horas = ventas.groupby("Hora").size().reset_index(name="Cantidad de ventas")
fig_horas = px.bar(
    ventas_horas,
    x="Hora",
    y="Cantidad de ventas",
    title="Cantidad de ventas por hora",
    labels={"Hora": "Hora del día", "Cantidad de ventas": "Cantidad"}
)
st.plotly_chart(fig_horas, use_container_width=True)

# 📊 Porcentaje por forma de pago
ventas_fp = ventas.merge(formas_pago, left_on="formaPago", right_on="id")
fp_pie = ventas_fp["formaPago_y"].value_counts(normalize=True).reset_index()
fp_pie.columns = ["Forma de Pago", "Proporción"]

# Crear gráfico de torta
fig_fp = px.pie(fp_pie, names="Forma de Pago", values="Proporción", title="% por forma de pago")
st.plotly_chart(fig_fp, use_container_width=True)