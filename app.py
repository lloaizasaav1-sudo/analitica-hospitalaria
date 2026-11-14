import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Analítica Financiera Hospitalaria",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Analítica Predictiva y Financiera Hospitalaria")
st.markdown("**Estudiante:** Laura Juliana Loaiza Saavedra | **ID:** 428429 | **UNIMINUTO**")
st.markdown("---")

# ==============================================================================
# CARGA Y ENTRENAMIENTO DEL MODELO (CACHEADO)
# ==============================================================================
@st.cache_resource
def cargar_y_entrenar():
    # Cargar el archivo institucional
    archivo_excel = 'CONSOLIDADO.xlsx'
    nombre_hoja = 'Plantilla De Informe'
    df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja)
    
    columna_eps = 'NOMBRE ENTIDAD' if 'NOMBRE ENTIDAD' in df.columns else 'ENTIDAD'
    
    # Preparación y codificación
    df['TIPO_SERVICIO_COD'] = pd.factorize(df['TIPO SERVICIO'])[0]
    df['EPS_COD'] = pd.factorize(df[columna_eps])[0]
    
    features = ['EDAD', 'CANTIDAD', 'TIPO_SERVICIO_COD', 'EPS_COD']
    target = 'VALOR FACTURADO'
    
    X = df[features].dropna()
    y = df.loc[X.index, target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entrenamiento del modelo Random Forest
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    return modelo, df, columna_eps

# Cargar elementos
try:
    modelo_rf, df, columna_eps = cargar_y_entrenar()
    datos_cargados = True
except Exception as e:
    datos_cargados = False
    st.error(f"⚠️ Error al cargar 'CONSOLIDADO.xlsx'. Asegúrate de subirlo al repositorio de GitHub junto a este código. Detalle: {e}")

if datos_cargados:
    # ==============================================================================
    # PANEL LATERAL: CONTROLES DE SIMULACIÓN (INPUTS)
    # ==============================================================================
    st.sidebar.header("🛠️ Parámetros de Simulación")
    st.sidebar.markdown("Modifique las variables para estimar la facturación de una nueva atención:")

    edad = st.sidebar.slider("Edad del Paciente", 0, 100, 35)
    cantidad = st.sidebar.number_input("Cantidad de Procedimientos", min_value=1, max_value=50, value=1)

    tipo_servicio_lista = df['TIPO SERVICIO'].dropna().unique()
    tipo_servicio_sel = st.sidebar.selectbox("Tipo de Servicio", tipo_servicio_lista)

    eps_lista = df[columna_eps].dropna().unique()
    eps_sel = st.sidebar.selectbox("Entidad / EPS", eps_lista)

    # Codificar selección del usuario
    tipo_servicio_cod = list(tipo_servicio_lista).index(tipo_servicio_sel)
    eps_cod = list(eps_lista).index(eps_sel)

    # ==============================================================================
    # CUERPO PRINCIPAL: PREDICCIÓN Y RESULTADOS
    # ==============================================================================
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Simulación de Costo Asistencial")
        if st.button("🚀 Calcular Valor Facturado Estimado", type="primary"):
            entrada = pd.DataFrame({
                'EDAD': [edad],
                'CANTIDAD': [cantidad],
                'TIPO_SERVICIO_COD': [tipo_servicio_cod],
                'EPS_COD': [eps_cod]
            })
            
            prediccion = modelo_rf.predict(entrada)[0]
            
            st.success(f"### 💰 Facturación Estimada: ${prediccion:,.2f}")
            st.info("📌 **Nota Gerencial:** Este valor es una estimación basada en Machine Learning (Random Forest). Recuerde tener en cuenta los márgenes de error en atenciones atípicas de alto costo.")

    with col2:
        st.subheader("📈 Resumen del Dataset Institucional")
        st.metric(label="Registros Totales Analizados", value=f"{df.shape[0]:,}")
        st.metric(label="Promedio General Facturado", value=f"${df['VALOR FACTURADO'].mean():,.2f}")

    # ==============================================================================
    # SECCIÓN DE ESTADÍSTICAS Y VISUALIZACIÓN
    # ==============================================================================
    st.markdown("---")
    st.subheader("📊 Indicadores Clave para la Toma de Decisiones")

    tab1, tab2 = st.tabs(["Top Servicios (Facturación)", "Concentración por EPS"])

    with tab1:
        top_serv = df.groupby('NOMBRE ARTICULO')['VALOR FACTURADO'].sum().sort_values(ascending=False).head(5)
        st.bar_chart(top_serv)

    with tab2:
        top_entidad = df.groupby(columna_eps)['VALOR FACTURADO'].sum().sort_values(ascending=False).head(5)
        st.bar_chart(top_entidad)
