import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Dashboard Lavado de Estibas", layout="wide")

st.title("📊 Dashboard Operativo - Lavado de Estibas Plásticas")
st.caption("Conectado en tiempo real con Google Sheets.")

# 2. URL de tu Google Sheet (formato CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1SpCbxB_Ih5wtIWFNZZO8JVEqfIK-i7fT1jGcuNknGzE/export?format=csv&gid=550787410"

@st.cache_data(ttl=10)
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(SHEET_URL)
    
    # Limpieza de columnas numéricas reales de tu Excel
    cols = [
        'Cantidad de estibas plásticas revisadas',
        'Cantidad de estibas plásticas no aptas',
        'Cantidad de estibas plásticas no aptas por residuos de huevo',
        'Cantidad de estibas plásticas no aptas por lodo',
        'Cantidad de estibas plásticas no aptas por polvo critico',
        'Cantidad de estibas plásticas limpias a despachar'
    ]
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    # --- KPIs PRINCIPALES ---
    st.subheader("📌 Resumen General")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_rev = int(df['Cantidad de estibas plásticas revisadas'].sum())
    total_no = int(df['Cantidad de estibas plásticas no aptas'].sum())
    total_ok = int(df['Cantidad de estibas plásticas limpias a despachar'].sum())
    pct = (total_no / total_rev * 100) if total_rev > 0 else 0
    
    kpi1.metric("Estibas Revisadas", f"{total_rev:,}")
    kpi2.metric("No Aptas (Total)", f"{total_no:,}", delta=f"{total_no} unidades", delta_color="inverse")
    
    # ESTA ES LA CORRECCIÓN (línea 57 y 58):
    kpi3.metric(label="Limpias Despachadas", value=f"{total_ok:,}")
    kpi4.metric(label="Porcentaje de Rechazo", value=f"{pct:.1f}%")

    st.markdown("---")

    # --- GRÁFICOS ---
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔄 Actividad Actual")
        fig1 = px.pie(df, names='Seleccione la actividad que se está realizando', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        st.subheader("⏱️ Reportes por Turno")
        fig2 = px.histogram(df, x='Turno en que se reciben las estibas plásticas', color='Turno en que se reciben las estibas plásticas')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 Últimos Registros")
    st.dataframe(df.tail(10), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")