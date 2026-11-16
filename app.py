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

st.title("🏥 Sistema de Inteligencia Financiera y Costos Hospitalarios")
st.markdown("**Proyecto Académico & Gestión Gerencial** | *Estudiante:* Laura Juliana Loaiza Saavedra (ID: 428429) | *Institución:* UNIMINUTO")
st.markdown("---")

# ==============================================================================
# CARGA Y PROCESAMIENTO DE DATOS INSTITUCIONALES
# ==============================================================================
@st.cache_data
def cargar_datos():
    archivo_excel = 'CONSOLIDADO.xlsx'
    nombre_hoja = 'Plantilla De Informe'
    df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja)
    return df

try:
    df = cargar_datos()
    datos_cargados = True
except Exception as e:
    datos_cargados = False
    st.error(f"⚠️ Error al cargar el archivo institucional 'CONSOLIDADO.xlsx'. Asegúrate de subirlo al repositorio en GitHub. Detalle: {e}")

if datos_cargados:
    
    # Normalización de columnas clave
    col_unidad = 'UNIDAD FUNCIONAL' if 'UNIDAD FUNCIONAL' in df.columns else df.columns[0]
    col_detalle = 'C. COSTOS DETALLE' if 'C. COSTOS DETALLE' in df.columns else df.columns[1]
    col_emisor = 'C. COSTOS ENCAB-EMISOR' if 'C. COSTOS ENCAB-EMISOR' in df.columns else df.columns[2]
    col_articulo = 'NOMBRE ARTICULO' if 'NOMBRE ARTICULO' in df.columns else df.columns[3]
    col_factura = 'VALOR FACTURADO' if 'VALOR FACTURADO' in df.columns else 'VALOR'

    # ==============================================================================
    # PANEL LATERAL: FILTROS GERENCIALES Y EXPORTACIÓN
    # ==============================================================================
    st.sidebar.header("🎛️ Filtros Gerenciales")
    
    # Filtro por Unidad Funcional
    unidades_disponibles = list(df[col_unidad].dropna().unique())
    unidad_seleccionada = st.sidebar.selectbox("Filtrar por Unidad Funcional", ["Todas"] + unidades_disponibles)

    # Filtrar dataframe según selección
    if unidad_seleccionada != "Todas":
        df_filtrado = df[df[col_unidad] == unidad_seleccionada]
    else:
        df_filtrado = df.copy()

    st.sidebar.markdown("---")
    st.sidebar.header("📥 Descarga de Informes")
    st.sidebar.markdown("Exporte los resultados analíticos para la junta directiva:")

    # Función para convertir dataframe a Excel en memoria para descarga
    def convertir_a_excel(df_exportar):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_exportar.to_excel(writer, index=False, sheet_name='Informe_Gerencial')
        processed_data = output.getvalue()
        return processed_data

    # ==============================================================================
    # MÉTRICAS EJECUTIVAS GLOBALES
    # ==============================================================================
    st.header("📈 Indicadores Financieros Globales")
    
    total_facturado = df_filtrado[col_factura].sum()
    total_atenciones = len(df_filtrado)
    promedio_atencion = total_facturado / total_atenciones if total_atenciones > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Facturación Total Acumulada", value=f"${total_facturado:,.2f}")
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

    # Agrupar por nombre de artículo / servicio
    resumen_servicios = df_filtrado.groupby(col_articulo)[col_factura].agg(['sum', 'count', 'mean']).reset_index()
    resumen_servicios.columns = ['Servicio / Artículo', 'Facturación Total ($)', 'Cantidad Atenciones', 'Promedio por Servicio ($)']
    resumen_servicios = resumen_servicios.sort_values(by='Facturación Total ($)', ascending=False)

    with col_s1:
        st.subheader("🏆 Top 10 Servicios Estrella (Mayor Ingreso)")
        st.markdown("Procedimientos que sostienen el balance financiero positivo.")
        top_10 = resumen_servicios.head(10).set_index('Servicio / Artículo')['Facturación Total ($)']
        st.bar_chart(top_10, color="#1f77b4")

    with col_s2:
        st.subheader("⚠️ Servicios de Menor Impacto / Facturación")
        st.markdown("Procedimientos con baja aportación a la caja institucional.")
        bottom_10 = resumen_servicios.tail(10).set_index('Servicio / Artículo')['Facturación Total ($)']
        st.bar_chart(bottom_10, color="#ff7f0e")

    # Botón de descarga del reporte de servicios
    excel_servicios = convertir_a_excel(resumen_servicios)
    st.download_button(
        label="📥 Descargar Reporte Completo de Servicios (Excel)",
        data=excel_servicios,
        file_name="reporte_servicios_financieros.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    # ==============================================================================
    # MÓDULO 2: COMPARATIVA POR CENTROS DE COSTOS Y UNIDADES FUNCIONALES
    # ==============================================================================
    st.header("🏢 Rendimiento por Centros de Costos y Unidades Funcionales")

    tab1, tab2, tab3 = st.tabs(["Unidad Funcional", "C. Costos Detalle", "C. Costos Emisor"])

    with tab1:
        st.subheader("Facturación por Unidad Funcional")
        df_u = df_filtrado.groupby(col_unidad)[col_factura].sum().reset_index().sort_values(by=col_factura, ascending=False)
        st.bar_chart(df_u.set_index(col_unidad), color="#2ca02c")
        st.dataframe(df_u, use_container_width=True)

    with tab2:
        st.subheader("Facturación por Centro de Costos Detalle")
        df_d = df_filtrado.groupby(col_detalle)[col_factura].sum().reset_index().sort_values(by=col_factura, ascending=False)
        st.bar_chart(df_d.set_index(col_detalle), color="#d62728")
        st.dataframe(df_d, use_container_width=True)

    with tab3:
        st.subheader("Facturación por Centro de Costos Emisor")
        df_e = df_filtrado.groupby(col_emisor)[col_factura].sum().reset_index().sort_values(by=col_factura, ascending=False)
        st.bar_chart(df_e.set_index(col_emisor), color="#9467bd")
        st.dataframe(df_e, use_container_width=True)

    # Botón global de descarga de datos filtrados
    st.markdown("---")
    st.subheader("📦 Exportar Base de Datos Consolidada")
    excel_global = convertir_a_excel(df_filtrado)
    st.download_button(
        label="📥 Descargar Base de Datos Filtrada para Gerencia (.xlsx)",
        data=excel_global,
        file_name="datos_financieros_hospital_yotoco.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
