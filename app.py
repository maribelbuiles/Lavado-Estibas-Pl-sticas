import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página del Dashboard
st.set_page_config(
    page_title="Dashboard Lavado de Estibas Plásticas", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard Operativo - Lavado de Estibas Plásticas")
st.caption("Conectado en tiempo real con Google Sheets. Se actualiza automáticamente.")

# 2. URL de exportación directa a CSV de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1SpCbxB_Ih5wtIWFNZZO8JVEqfIK-i7fT1jGcuNknGzE/export?format=csv&gid=550787410"

# 3. Función para cargar datos con Auto-Refresh (TTL de 10 segundos)
@st.cache_data(ttl=10)
def load_data(url):
    data = pd.read_csv(url)
    return data

try:
    df = load_data(SHEET_URL)
    
    # 4. Limpieza y conversión de tipos de datos de las columnas reales
    columnas_numericas = [
        'Cantidad de estibas plásticas revisadas',
        'Cantidad de estibas plásticas no aptas',
        'Cantidad de estibas plásticas no aptas por residuos de huevo',
        'Cantidad de estibas plásticas no aptas por lodo',
        'Cantidad de estibas plásticas no aptas por polvo critico',
        'Cantidad de estibas plásticas limpias a despachar'
    ]
    
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 5. Sección de Métricas / KPIs Principales (CORREGIDO)
    st.subheader("📌 Resumen General de Operaciones")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_revisadas = int(df['Cantidad de estibas plásticas revisadas'].sum())
    total_no_aptas = int(df['Cantidad de estibas plásticas no aptas'].sum())
    total_despachadas = int(df['Cantidad de estibas plásticas limpias a despachar'].sum())
    
    # Cálculo del porcentaje de rechazo de forma segura
    col_pct = (total_no_aptas / total_revisadas * 100) if total_revisadas > 0 else 0
    
    kpi1.metric(label="Estibas Revisadas", value=f"{total_revisadas:,}")
    kpi2.metric(label="Estibas No Aptas (Total)", value=f"{total_no_aptas:,}", delta=f"{total_no_aptas} unidades", delta_color="inverse")
    # AQUÍ ESTÁ LA CORRECCIÓN: Se agregó 'value=' explícitamente para evitar el SyntaxError
    kpi3.metric(label="Limpias Despachadas", value=f"{total_despachadas:,}")
    kpi4.metric(label="Porcentaje de Rechazo", value=f"{col_pct:.1f}%")

    st.markdown("---")

    # 6. Gráficos Distribución y Análisis
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.subheader("🔄 Distribución por Actividad")
        col_act = 'Seleccione la actividad que se está realizando'
        if col_act in df.columns:
            act_counts = df[col_act].value_counts().reset_index()
            act_counts.columns = ['Actividad', 'Total']
            fig_pie = px.pie(act_counts, values='Total', names='Actividad', hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
            
    with col_der:
        st.subheader("⏱️ Registro Operativo por Turnos")
        col_turno = 'Turno en que se reciben las estibas plásticas'
        if col_turno in df.columns:
            turno_counts = df[col_turno].value_counts().reset_index()
            turno_counts.columns = ['Turno', 'Cantidad de Reportes']
            fig_bar = px.bar(turno_counts, x='Turno', y='Cantidad de Reportes', color='Turno',
                             color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # 7. Desglose de Defectos (Huevo, Lodo, Polvo)
    st.subheader("❌ Análisis de Causas de No Aptitud")
    
    causas_dict = {
        'Residuos de Huevo': df['Cantidad de estibas plásticas no aptas por residuos de huevo'].sum() if 'Cantidad de estibas plásticas no aptas por residuos de huevo' in df.columns else 0,
        'Lodo': df['Cantidad de estibas plásticas no aptas por lodo'].sum() if 'Cantidad de estibas plásticas no aptas por lodo' in df.columns else 0,
        'Polvo Crítico': df['Cantidad de estibas plásticas no aptas por polvo critico'].sum() if 'Cantidad de estibas plásticas no aptas por polvo critico' in df.columns else 0
    }
    
    df_causas = pd.DataFrame(list(causas_dict.items()), columns=['Causa', 'Cantidad Total'])
    fig_causas = px.bar(df_causas, x='Causa', y='Cantidad Total', text_auto=True,
                        color='Causa', color_discrete_sequence=px.colors.sequential.Sunsetdark)
    st.plotly_chart(fig_causas, use_container_width=True)

    # 8. Visualización de los últimos datos crudos ingresados
    st.markdown("---")
    st.subheader("📋 Últimos 10 Reportes Recibidos")
    st.dataframe(df.tail(10), use_container_width=True)

except Exception as e:
    st.error(f"Ocurrió un error al intentar leer los datos en tiempo real: {e}")
    st.warning("Verifica que el Google Sheet esté compartido públicamente como 'Lector' para cualquier persona con el enlace.")