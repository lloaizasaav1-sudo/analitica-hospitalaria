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
# PANEL LATERAL: CARGA DE ARCHIVO Y SELECCIÓN DE PERIODO (XENCO)
# ==============================================================================
st.sidebar.header("📁 Carga de Datos y Periodo")
st.sidebar.markdown("Suba el archivo de Xenco y especifique el periodo:")

mes_seleccionado = st.sidebar.selectbox(
    "Mes de Facturación", 
    ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
)
anio_seleccionado = st.sidebar.selectbox("Año", [2026, 2025, 2024, 2023])

archivo_subido = st.sidebar.file_uploader("Cargar Facturación Xenco (.xlsx)", type=["xlsx"])

@st.cache_data
def cargar_datos_por_defecto():
    try:
        return pd.read_excel('CONSOLIDADO.xlsx', sheet_name='Plantilla De Informe')
    except:
        return None

if archivo_subido is not None:
    try:
        df = pd.read_excel(archivo_subido)
        st.sidebar.success(f"✅ Archivo Xenco cargado para **{mes_seleccionado} {anio_seleccionado}**")
        datos_cargados = True
    except Exception as e:
        st.sidebar.error(f"⚠️ Error al leer el archivo: {e}")
        datos_cargados = False
else:
    df = cargar_datos_por_defecto()
    if df is not None:
        datos_cargados = True
        st.sidebar.info(f"📌 Usando archivo predeterminado (**Periodo: {mes_seleccionado} {anio_seleccionado}**).")
    else:
        datos_cargados = False
        st.warning("📌 Por favor, suba el archivo Excel de Xenco en el panel lateral.")

if datos_cargados:
    
    # Mapeo exacto de columnas de Xenco
    col_unidad = 'UNIDAD FUNCIONAL' if 'UNIDAD FUNCIONAL' in df.columns else df.columns[0]
    col_detalle = 'C. COSTOS DETALLE' if 'C. COSTOS DETALLE' in df.columns else df.columns[1]
    col_articulo = 'NOMBRE ARTICULO' if 'NOMBRE ARTICULO' in df.columns else df.columns[2]
    col_factura = 'VALOR FACTURADO' if 'VALOR FACTURADO' in df.columns else 'VALOR FACTURADO'
    col_costo = 'VALOR COSTO' if 'VALOR COSTO' in df.columns else 'VALOR COSTO'
    col_profesional = 'NOMBRE PROFESIONAL' if 'NOMBRE PROFESIONAL' in df.columns else 'NOMBRE PROFESIONAL'
    col_entidad = 'NOMBRE ENTIDAD' if 'NOMBRE ENTIDAD' in df.columns else 'NOMBRE ENTIDAD'

    # ==============================================================================
    # FILTROS GERENCIALES
    # ==============================================================================
    st.sidebar.markdown("---")
    st.sidebar.header("🎛️ Filtros Gerenciales")
    
    unidades_disponibles = list(df[col_unidad].dropna().unique()) if col_unidad in df.columns else []
    unidad_seleccionada = st.sidebar.selectbox("Filtrar por Unidad Funcional", ["Todas"] + [str(u) for u in unidades_disponibles])

    if unidad_seleccionada != "Todas" and col_unidad in df.columns:
        df_filtrado = df[df[col_unidad].astype(str) == unidad_seleccionada]
    else:
        df_filtrado = df.copy()

    st.sidebar.markdown("---")
    st.sidebar.header("📥 Descarga de Informes")
    
    def convertir_a_excel(df_exportar, nombre_hoja_excel):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_exportar.to_excel(writer, index=False, sheet_name=nombre_hoja_excel)
        return output.getvalue()

    # ==============================================================================
    # CABECERA DEL PERIODO
    # ==============================================================================
    st.subheader(f"📅 Reporte Financiero Xenco - **{mes_seleccionado} de {anio_seleccionado}**")
    st.markdown(f"**Unidad Funcional Filtrada:** `{unidad_seleccionada}`")
    st.markdown("---")

    # ==============================================================================
    # MÉTRICAS EJECUTIVAS GLOBALES + INDICADORES NUEVOS
    # ==============================================================================
    st.header("📈 Indicadores Financieros Globales")
    
    total_facturado = df_filtrado[col_factura].sum() if col_factura in df_filtrado.columns else 0
    total_costo = df_filtrado[col_costo].sum() if col_costo in df_filtrado.columns else 0
    utilidad_operativa = total_facturado - total_costo
    margen_utilidad = (utilidad_operativa / total_facturado * 100) if total_facturado > 0 else 0
    total_atenciones = len(df_filtrado)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="💰 Facturación Total", value=f"${total_facturado:,.2f}")
    with col2:
        st.metric(label="📉 Costo Operativo Total", value=f"${total_costo:,.2f}")
    with col3:
        st.metric(label="💼 Utilidad Operativa", value=f"${utilidad_operativa:,.2f}", delta=f"{margen_utilidad:.1f}% Margen")
    with col4:
        st.metric(label="📋 Total Registros Xenco", value=f"{total_atenciones:,}")

    st.markdown("---")

    # ==============================================================================
    # MÓDULO 1: PRODUCTIVIDAD MÉDICA (Médicos que más y menos facturan)
    # ==============================================================================
    st.header("👨‍⚕️ Análisis de Productividad por Profesional Médico")
    st.markdown("Evaluación del aporte económico de los profesionales de la salud según los registros de facturación.")

    if col_profesional in df_filtrado.columns and col_factura in df_filtrado.columns:
        resumen_medicos = df_filtrado.groupby(col_profesional)[col_factura].agg(['sum', 'count', 'mean']).reset_index()
        resumen_medicos.columns = ['Profesional Médico', 'Facturación Total ($)', 'Cantidad Atenciones', 'Promedio por Atención ($)']
        resumen_medicos = resumen_medicos.sort_values(by='Facturación Total ($)', ascending=False)

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader("🏆 Top 10 Médicos con Mayor Facturación")
            top_medicos = resumen_medicos.head(10).set_index('Profesional Médico')['Facturación Total ($)']
            st.bar_chart(top_medicos, color="#2ca02c")

        with col_m2:
            st.subheader("⚠️ Médicos con Menor Facturación Registrada")
            bottom_medicos = resumen_medicos.tail(10).set_index('Profesional Médico')['Facturación Total ($)']
            st.bar_chart(bottom_medicos, color="#d62728")

        excel_medicos = convertir_a_excel(resumen_medicos, "Productividad_Medica")
        st.download_button(
            label=f"📥 Descargar Reporte de Productividad Médica ({mes_seleccionado} {anio_seleccionado}) - Excel",
            data=excel_medicos,
            file_name=f"reporte_medicos_{mes_seleccionado.lower()}_{anio_seleccionado}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("ℹ️ No se detectó la columna de profesionales médicos en el archivo.")

    st.markdown("---")

    # ==============================================================================
    # MÓDULO 2: SERVICIOS ESTRELLA (Revenue Drivers)
    # ==============================================================================
    st.header("💎 Análisis de Servicios: ¿Qué factura más y qué factura menos?")
    
    col_s1, col_s2 = st.columns(2)

    if col_articulo in df_filtrado.columns and col_factura in df_filtrado.columns:
        resumen_servicios = df_filtrado.groupby(col_articulo)[col_factura].agg(['sum', 'count', 'mean']).reset_index()
        resumen_servicios.columns = ['Servicio / Artículo', 'Facturación Total ($)', 'Cantidad Atenciones', 'Promedio por Servicio ($)']
        resumen_servicios = resumen_servicios.sort_values(by='Facturación Total ($)', ascending=False)

        with col_s1:
            st.subheader("🏆 Top 10 Servicios Estrella (Mayor Ingreso)")
            top_10 = resumen_servicios.head(10).set_index('Servicio / Artículo')['Facturación Total ($)']
            st.bar_chart(top_10, color="#1f77b4")

        with col_s2:
            st.subheader("⚠️ Servicios de Menor Impacto / Facturación")
            bottom_10 = resumen_servicios.tail(10).set_index('Servicio / Artículo')['Facturación Total ($)']
            st.bar_chart(bottom_10, color="#ff7f0e")

        excel_servicios = convertir_a_excel(resumen_servicios, "Servicios_Financieros")
        st.download_button(
            label=f"📥 Descargar Reporte de Servicios ({mes_seleccionado} {anio_seleccionado}) - Excel",
            data=excel_servicios,
            file_name=f"reporte_servicios_{mes_seleccionado.lower()}_{anio_seleccionado}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown("---")

    # ==============================================================================
    # MÓDULO 3: INDICADORES ADICIONALES (Concentración de EPS / Pagadores)
    # ==============================================================================
    st.header("📊 Indicador Estratégico: Concentración de Ingresos por Entidad (EPS / Pagador)")
    st.markdown("Identifica cuáles entidades aportan mayor volumen financiero a la E.S.E.")

    if col_entidad in df_filtrado.columns and col_factura in df_filtrado.columns:
        resumen_entidades = df_filtrado.groupby(col_entidad)[col_factura].agg(['sum', 'count']).reset_index()
        resumen_entidades.columns = ['Entidad / EPS', 'Facturación Total ($)', 'Total Pacientes / Atenciones']
        resumen_entidades = resumen_entidades.sort_values(by='Facturación Total ($)', ascending=False)
        
        st.bar_chart(resumen_entidades.head(10).set_index('Entidad / EPS')['Facturación Total ($)'], color="#9467bd")
        st.dataframe(resumen_entidades, use_container_width=True)

    st.markdown("---")

    # ==============================================================================
    # MÓDULO 4: COMPARATIVA POR CENTROS DE COSTOS Y UNIDADES FUNCIONALES
    # ==============================================================================
    st.header("🏢 Rendimiento por Centros de Costos y Unidades Funcionales")

    tab1, tab2 = st.tabs(["Unidad Funcional", "C. Costos Detalle"])

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

    # Botón global de descarga de datos filtrados
    st.markdown("---")
    st.subheader("📦 Exportar Base de Datos Consolidada del Periodo")
    excel_global = convertir_a_excel(df_filtrado, "Consolidado_Gerencial")
    st.download_button(
        label=f"📥 Descargar Base de Datos Filtrada ({mes_seleccionado} {anio_seleccionado}) - Excel",
        data=excel_global,
        file_name=f"datos_hospital_yotoco_{mes_seleccionado.lower()}_{anio_seleccionado}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
