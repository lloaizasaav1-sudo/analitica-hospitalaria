import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Gerencia Financiera - Analítica Hospitalaria",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Analítica Financiera y Toma de Decisiones Gerenciales")
st.markdown("**Estudiante:** Laura Juliana Loaiza Saavedra | **ID:** 428429 | **UNIMINUTO**")
st.markdown("---")

# ==============================================================================
# CARGA Y ENTRENAMIENTO DEL MODELO (CACHEADO)
# ==============================================================================
@st.cache_resource
def cargar_y_entrenar():
    archivo_excel = 'CONSOLIDADO.xlsx'
    nombre_hoja = 'Plantilla De Informe'
    df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja)
    
    columna_eps = 'NOMBRE ENTIDAD' if 'NOMBRE ENTIDAD' in df.columns else 'ENTIDAD'
    
    df['TIPO_SERVICIO_COD'] = pd.factorize(df['TIPO SERVICIO'])[0]
    df['EPS_COD'] = pd.factorize(df[columna_eps])[0]
    
    features = ['EDAD', 'CANTIDAD', 'TIPO_SERVICIO_COD', 'EPS_COD']
    target = 'VALOR FACTURADO'
    
    X = df[features].dropna()
    y = df.loc[X.index, target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    return modelo, df, columna_eps

try:
    modelo_rf, df, columna_eps = cargar_y_entrenar()
    datos_cargados = True
except Exception as e:
    datos_cargados = False
    st.error(f"⚠️ Error al cargar 'CONSOLIDADO.xlsx'. Asegúrate de subirlo a GitHub. Detalle: {e}")

if datos_cargados:
    
    # ==============================================================================
    # 💎 SECCIÓN NUEVA: ENFOQUE GERENCIAL (REVENUE DRIVERS)
    # ==============================================================================
    st.header("📊 Enfoque Gerencial: ¿Cuáles son los Servicios que más Dinero Dan?")
    
    # Agrupamos por servicio para ver facturación total y volumen
    resumen_servicios = df.groupby('NOMBRE ARTICULO').agg(
        Facturacion_Total=('VALOR FACTURADO', 'sum'),
        Atenciones_Totales=('VALOR FACTURADO', 'count'),
        Costo_Promedio=('VALOR FACTURADO', 'mean')
    ).reset_index().sort_values(by='Facturacion_Total', ascending=False)
    
    top_1_servicio = resumen_servicios.iloc[0]
    
    # Mostramos métricas ejecutivas clave arriba
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(
            label="💎 Servicio Estrella (Mayor Facturación Total)", 
            value=f"${top_1_servicio['Facturacion_Total']:,.0f}",
            delta=f"{top_1_servicio['NOMBRE ARTICULO']}"
        )
    with col_m2:
        st.metric(
            label="📈 Facturación Global Acumulada", 
            value=f"${df['VALOR FACTURADO'].sum():,.0f}"
        )
    with col_m3:
        st.metric(
            label="🏥 Total de Atenciones Analizadas", 
            value=f"{df.shape[0]:,} registros"
        )
        
    st.markdown("---")

    # Gráfico de barras interactivo con Streamlit para el Top 10 de servicios por ingresos
    st.subheader("🏆 Top 10 de Servicios Generadores de Ingresos (Revenue Drivers)")
    st.markdown("Este gráfico muestra a la gerencia qué procedimientos son los que verdaderamente sostienen el balance financiero positivo de la institución.")
    
    top_10_ingresos = resumen_servicios.head(10).set_index('NOMBRE ARTICULO')['Facturacion_Total']
    st.bar_chart(top_10_ingresos, color="#20B2AA")

    st.markdown("---")

    # ==============================================================================
    # PANEL LATERAL Y SIMULADOR PREDICTIVO
    # ==============================================================================
    st.sidebar.header("🛠️ Simulador Predictivo de Costos")
    st.sidebar.markdown("Estime el valor de una atención para la toma de decisiones:")

    edad = st.sidebar.slider("Edad del Paciente", 0, 100, 35)
    cantidad = st.sidebar.number_input("Cantidad de Procedimientos", min_value=1, max_value=50, value=1)

    tipo_servicio_lista = df['TIPO SERVICIO'].dropna().unique()
    tipo_servicio_sel = st.sidebar.selectbox("Tipo de Servicio", tipo_servicio_lista)

    eps_lista = df[columna_eps].dropna().unique()
    eps_sel = st.sidebar.selectbox("Entidad / EPS", eps_lista)

    tipo_servicio_cod = list(tipo_servicio_lista).index(tipo_servicio_sel)
    eps_cod = list(eps_lista).index(eps_sel)

    if st.sidebar.button("🚀 Calcular Valor Estimado", type="primary"):
        entrada = pd.DataFrame({
            'EDAD': [edad],
            'CANTIDAD': [cantidad],
            'TIPO_SERVICIO_COD': [tipo_servicio_cod],
            'EPS_COD': [eps_cod]
        })
        
        prediccion = modelo_rf.predict(entrada)[0]
        st.sidebar.success(f"### 💰 Estimado: ${prediccion:,.2f}")
