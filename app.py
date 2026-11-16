import streamlit as st
import pandas as pd
import io

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Gerencia Financiera - Hospital de Yotoco",
    page_icon="🏥",
    layout="wide"
)

# Estilo visual corporativo limpio
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# CABECERA INSTITUCIONAL CON LOS DOS LOGOS DEL HOSPITAL
# ==============================================================================
col_logo1, col_titulo, col_logo2 = st.columns([1, 4, 1])

with col_logo1:
    try:
        st.image("logo1.png", width=120)
    except:
        st.write("📌 [Logo 1]")

with col_titulo:
    st.title("🏥 Inteligencia Financiera y Costos Hospitalarios")
    st.markdown("**E.S.E. Hospital Local de Yotoco** | *Autora:* Laura Juliana Loaiza Saavedra (ID: 428429) - **UNIMINUTO**")

with col_logo2:
    try:
        st.image("logo2.png", width=120)
    except:
        st.write("📌 [Logo 2]")

st.markdown("---")

# ==============================================================================
# PANEL LATERAL: CARGA DE ARCHIVO Y SELECCIÓN DE PERIODO (MES / AÑO)
# ==============================================================================
st.sidebar.header("📁 Carga de Datos y Periodo")
st.sidebar.markdown("Suba el archivo Excel de facturación y especifique el periodo correspondiente:")

# Selector de Mes y Año
mes_seleccionado = st.sidebar.selectbox(
    "Mes de Facturación", 
    ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
)
anio_seleccionado = st.sidebar.selectbox("Año", [2026, 2025, 2024, 2023])

archivo_subido = st.sidebar.file_uploader("Cargar Facturación Mensual (.xlsx)", type=["xlsx"])

@st.cache_data
def cargar_datos_por_defecto():
    try:
        return pd.read_excel('CONSOLIDADO.xlsx', sheet_name='Plantilla De Informe')
    except:
        return None

if archivo_subido is not None:
    try:
        df = pd.read_excel(archivo_subido)
        st.sidebar.success(f"✅ Archivo cargado correctamente para **{mes_seleccionado} {anio_seleccionado}**")
        datos_cargados = True
    except Exception as e:
        st.sidebar.error(f"⚠️ Error al leer el archivo subido: {e}")
        datos_cargados = False
else:
    df = cargar_datos_por_defecto()
    if df is not None:
        datos_cargados = True
        st.sidebar.info(f"📌 Usando archivo predeterminado del sistema (**Periodo: {mes_seleccionado} {anio_seleccionado}**).")
    else:
        datos_cargados = False
        st.warning("📌 Por favor, suba un archivo Excel de facturación en el panel lateral para iniciar el análisis.")

if datos_cargados:
    
    # Detección inteligente de columnas clave
    columnas_disponibles = list(df.columns)
    
    col_unidad = 'UNIDAD FUNCIONAL' if 'UNIDAD FUNCIONAL' in df.columns else columnas_disponibles[0]
    col_detalle = 'C. COSTOS DETALLE' if 'C. COSTOS DETALLE' in df.columns else (columnas_disponibles[1] if len(columnas_disponibles) > 1 else columnas_disponibles[0])
    col_emisor = 'C. COSTOS ENCAB-EMISOR' if 'C. COSTOS ENCAB-EMISOR' in df.columns else (columnas_disponibles[2] if len(columnas_disponibles) > 2 else columnas_disponibles[0])
    col_articulo = 'NOMBRE ARTICULO' if 'NOMBRE ARTICULO' in df.columns else (columnas_disponibles[3] if len(columnas_disponibles) > 3 else columnas_disponibles[0])
    col_factura = 'VALOR FACTURADO' if 'VALOR FACTURADO' in df.columns else 'VALOR'

    # ==============================================================================
    # FILTROS GERENCIALES ADICIONALES
    # ==============================================================================
    st.sidebar.markdown("---")
    st.sidebar.header("🎛️ Filtros Gerenciales")
    
    unidades_disponibles = list(df[col_unidad].dropna().unique())
    unidad_seleccionada = st.sidebar.selectbox("Filtrar por Unidad Funcional", ["Todas"] + [str(u) for u in unidades_disponibles])

    if unidad_seleccionada != "Todas":
        df_filtrado = df[df[col_unidad].astype(str) == unidad_seleccionada]
    else:
        df_filtrado = df.copy()

    st.sidebar.markdown("---")
    st.sidebar.header("📥 Descarga de Informes")
    
    # Función para convertir dataframe a Excel incluyendo metadatos del periodo
    def convertir_a_excel(df_exportar, nombre_hoja_excel):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_exportar.to_excel(writer, index=False, sheet_name=nombre_hoja_excel)
        return output.getvalue()

    # ==============================================================================
    # CABECERA VISIBLE DEL PERIODO SELECCIONADO
    # ==============================================================================
    st.subheader(f"📅 Reporte Financiero Correspondiente a: **{mes_seleccionado} de {anio_seleccionado}**")
    st.markdown(f"**Unidad Funcional Analizada:** `{unidad_seleccionada}`")
    st.markdown("---")

    # ==============================================================================
    # MÉTRICAS EJECUTIVAS GLOBALES
    # ==============================================================================
    st.header("📈 Indicadores Financieros Globales")
    
    total_facturado = df_filtrado[col_factura].sum() if col_factura in df_filtrado.columns else 0
    total_atenciones = len(df_filtrado)
    promedio_atencion = total_facturado / total_atenciones if total_atenciones > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Facturación Total del Periodo", value=f"${total_facturado:,.2f}")
    with col2:
        st.metric(label="📋 Volumen Total de Atenciones", value=f"{total_atenciones:,}")
    with col3:
        st.metric(label="📊 Valor Promedio por Atención", value=f"${promedio_atencion:,.2f}")

    st.markdown("---")

    # ==============================================================================
    # MÓDULO 1: ANÁLISIS DE SERVICIOS (Revenue Drivers vs Baja Rentabilidad)
    # ==============================================================================
    st.header("💎 Análisis de Servicios: ¿Qué factura más y qué factura menos?")
    
    col_s1, col_s2 = st.columns(2)

    if col_articulo in df_filtrado.columns and col_factura in df_filtrado.columns:
        resumen_servicios = df_
