import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Analítica Financiera - Centros de Costos",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Analítica de Costos e Ingresos Operativos (CRISP-DM)")
st.markdown("**Estudiante:** Laura Juliana Loaiza Saavedra | **ID:** 428429 | **UNIMINUTO**")
st.markdown("---")

# ==============================================================================
# FASE 1 Y 2: CARGA Y COMPRENSIÓN DE DATOS (Con caché)
# ==============================================================================
@st.cache_resource
def cargar_y_procesar_datos():
    archivo_excel = 'CONSOLIDADO.xlsx'
    nombre_hoja = 'Plantilla De Informe'
    df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja)
    
    # Identificar columnas clave de forma segura según la estructura del Excel
    col_unidad = 'UNIDAD FUNCIONAL' if 'UNIDAD FUNCIONAL' in df.columns else df.columns[0]
    col_detalle = 'C. COSTOS DETALLE' if 'C. COSTOS DETALLE' in df.columns else df.columns[1]
    col_emisor = 'C. COSTOS ENCAB-EMISOR' if 'C. COSTOS ENCAB-EMISOR' in df.columns else df.columns[2]
    
    # Codificación para Machine Learning
    df['UNIDAD_COD'] = pd.factorize(df[col_unidad])[0]
    df['DETALLE_COD'] = pd.factorize(df[col_detalle])[0]
    df['EMISOR_COD'] = pd.factorize(df[col_emisor])[0]
    
    features = ['EDAD', 'CANTIDAD', 'UNIDAD_COD', 'DETALLE_COD', 'EMISOR_COD']
    target = 'VALOR FACTURADO'
    
    X = df[features].dropna()
    y = df.loc[X.index, target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Modelo Random Forest (Fase 4: Modelado)
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    return modelo, df, col_unidad, col_detalle, col_emisor

try:
    modelo_rf, df, col_unidad, col_detalle, col_emisor = cargar_y_procesar_datos()
    datos_cargados = True
except Exception as e:
    datos_cargados = False
    st.error(f"⚠️ Error al cargar 'CONSOLIDADO.xlsx'. Asegúrate de subirlo a GitHub. Detalle: {e}")

if datos_cargados:
    
    # ==============================================================================
    # FASE 5: EVALUACIÓN FINANCIERA Y COMPARATIVA DE CENTROS DE COSTOS
    # ==============================================================================
    st.header("📊 Comparativa de Costos e Ingresos por Centro de Costos")
    st.markdown("Este módulo permite a la gerencia contrastar el rendimiento financiero y operativo entre las unidades funcionales y los centros de costos.")

    # Métricas ejecutivas globales
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="💰 Facturación Global Acumulada", value=f"${df['VALOR FACTURADO'].sum():,.0f}")
    with col2:
        st.metric(label="🏥 Total Registros Analizados", value=f"{df.shape[0]:,}")
    with col3:
        st.metric(label="📈 Promedio por Atenciones", value=f"${df['VALOR FACTURADO'].mean():,.2f}")

    st.markdown("---")

    # Pestañas de análisis por Centro de Costos y Unidad Funcional
    tab1, tab2, tab3 = st.tabs(["Unidad Funcional", "Centro de Costos (Detalle)", "Centro de Costos (Emisor)"])

    with tab1:
        st.subheader("Rendimiento Financiero por Unidad Funcional")
        df_unidad = df.groupby(col_unidad)['VALOR FACTURADO'].sum().reset_index().sort_values(by='VALOR FACTURADO', ascending=False)
        st.bar_chart(df_unidad.set_index(col_unidad), color="#20B2AA")
        st.dataframe(df_unidad, use_container_width=True)

    with tab2:
        st.subheader("Rendimiento por Centro de Costos Detalle")
        df_detalle = df.groupby(col_detalle)['VALOR FACTURADO'].sum().reset_index().sort_values(by='VALOR FACTURADO', ascending=False)
        st.bar_chart(df_detalle.set_index(col_detalle), color="#4682B4")
        st.dataframe(df_detalle, use_container_width=True)

    with tab3:
        st.subheader("Rendimiento por Centro de Costos Emisor")
        df_emisor = df.groupby(col_emisor)['VALOR FACTURADO'].sum().reset_index().sort_values(by='VALOR FACTURADO', ascending=False)
        st.bar_chart(df_emisor.set_index(col_emisor), color="#9370DB")
        st.dataframe(df_emisor, use_container_width=True)

    # ==============================================================================
    # FASE 6: SIMULADOR PREDICTIVO (Panel Lateral)
    # ==============================================================================
    st.sidebar.header("🛠️ Simulador Predictivo de Costos")
    st.sidebar.markdown("Estime la facturación según los centros de costos:")

    edad = st.sidebar.slider("Edad del Paciente", 0, 100, 35)
    cantidad = st.sidebar.number_input("Cantidad", min_value=1, max_value=50, value=1)

    unidad_lista = df[col_unidad].dropna().unique()
    unidad_sel = st.sidebar.selectbox("Unidad Funcional", unidad_lista)

    detalle_lista = df[col_detalle].dropna().unique()
    detalle_sel = st.sidebar.selectbox("C. Costos Detalle", detalle_lista)

    emisor_lista = df[col_emisor].dropna().unique()
    emisor_sel = st.sidebar.selectbox("C. Costos Emisor", emisor_lista)

    # Codificación de la selección del usuario
    u_cod = list(unidad_lista).index(unidad_sel)
    d_cod = list(detalle_lista).index(detalle_sel)
    e_cod = list(emisor_lista).index(emisor_sel)

    if st.sidebar.button("🚀 Calcular Valor Estimado", type="primary"):
        entrada = pd.DataFrame({
            'EDAD': [edad],
            'CANTIDAD': [cantidad],
            'UNIDAD_COD': [u_cod],
            'DETALLE_COD': [d_cod],
            'EMISOR_COD': [e_cod]
        })
        
        prediccion = modelo_rf.predict(entrada)[0]
        st.sidebar.success(f"### 💰 Estimado: ${prediccion:,.2f}")
