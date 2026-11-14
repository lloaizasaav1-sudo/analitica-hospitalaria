# analitica-hospitalaria
# 🏥 Analítica Financiera y Toma de Decisiones Gerenciales (CRISP-DM)

Aplicativo web interactivo de analítica de datos y modelado predictivo diseñado para apoyar la gestión financiera hospitalaria, identificando los servicios médicos de mayor rentabilidad e impacto en la facturación (*revenue drivers*) para asegurar un balance financiero positivo.

## 📌 Información Académica
* **Estudiante:** Laura Juliana Loaiza Saavedra  
* **ID:** 428429  
* **Programa:** Ingeniería Industrial  
* **Institución:** Corporación Universitaria Minuto de Dios (UNIMINUTO)  
* **Docente:** Xammy Alexander Victoria González  

---

## 🎯 Propósito Gerencial del Aplicativo
Desarrollado bajo la metodología **CRISP-DM**, este prototipo responde a las necesidades estratégicas de la gerencia hospitalaria:
1. **Identificación de Servicios Estrella (*Revenue Drivers*):** Determina cuál es el servicio médico que genera mayor volumen de facturación total para priorizar recursos y asegurar la sostenibilidad financiera.
2. **Análisis de Balance Financiero:** Permite contrastar la demanda operativa frente al ingreso neto generado por procedimiento y entidad pagadora (EPS).
3. **Simulador Predictivo de Costos (Machine Learning):** Implementa un modelo **Random Forest Regressor** para estimar el valor facturado de nuevas atenciones médicas en tiempo real, integrando el análisis de márgenes de error y límites operativos del modelo.

---

## 📂 Estructura del Repositorio
* `app.py`: Código fuente del dashboard gerencial y simulador predictivo desarrollado en **Streamlit**.
* `CONSOLIDADO.xlsx`: Base de datos institucional con los registros de atenciones médicas.
* `requirements.txt`: Archivo de configuración con las librerías necesarias para el despliegue en la nube.

---

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python
* **Procesamiento de Datos:** Pandas, NumPy, Openpyxl
* **Machine Learning:** Scikit-learn (Random Forest Regressor)
* **Interfaz Web y Despliegue:** Streamlit Community Cloud & GitHub

---

## 🔗 Acceso al Aplicativo Interactivo
Puedes explorar el tablero gerencial y realizar simulaciones en el siguiente enlace:  
👉 [Abrir Aplicativo en Streamlit Cloud](#) *(Reemplaza el `#` por el enlace web que te genere Streamlit al finalizar el despliegue)*
