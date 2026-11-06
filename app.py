import streamlit as st
import pandas as pd
import html as html_lib
import streamlit.components.v1 as components
import base64
import os

st.set_page_config(
    page_title="Coca-Cola FEMSA DSS CAPEX Barranquilla",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ZONAS = {
    "Nave L6": (0.3109, 0.0869, -0.0969),
    "Ed. Administrativo": (-0.0787, 0.0909, -0.2365),
    "Preparación Jarabes": (-0.0134, 0.0549, -0.1497),
    "Nave L5": (-0.0908, 0.0740, 0.0775),
    "PTAP": (0.1250, 0.0105, -0.2363),
    "Maquinaria Auxiliar": (0.1860, 0.0700, -0.1343),
    "Almacén Materia Prima": (0.1700, 0.0729, -0.0558),
    "Taller de Mantenimiento": (0.1995, 0.0338, 0.1309),
    "Almacén PT en planta": (0.0538, 0.0610, 0.1215),
    "Almacén central": (0.1879, 0.0398, 0.2870),
    "Almacén Seco y Refrigerado": (0.0012, 0.0729, 0.0481),
    "CIP 2": (-0.0146, 0.0409, -0.2411),
    "Laboratorios": (0.1035, 0.0458, -0.1947),
    "Bodega de Almacenamiento": (-0.2996, 0.1126, 0.1435),
    "Almacén PT": (-0.3069, 0.0863, -0.1013),
    "Planta de Aguas Residuales": (0.0046, 0.0560, 0.3222),
    "Línea San Martín": (0.0442, 0.0729, -0.0451),
    "Línea Krones": (0.1245, 0.0729, -0.0544),
    "Línea Simonazzi": (0.0048, 0.0729, -0.0600),
    "Línea Caraballo": (0.0800, 0.0729, -0.0742),
}

CRITERIOS = [
    {"id": "C1", "nombre": "Alineación estratégica y LRP", "tipo": "Beneficio", "peso": 13.99},
    {"id": "C2", "nombre": "Rentabilidad y optimización de recursos", "tipo": "Beneficio", "peso": 20.53},
    {"id": "C3", "nombre": "Continuidad operativa y salud de activos", "tipo": "Beneficio", "peso": 18.94},
    {"id": "C4", "nombre": "Seguridad y cumplimiento normativo", "tipo": "Beneficio", "peso": 31.97},
    {"id": "C5", "nombre": "Gestión de riesgos técnicos y operacionales", "tipo": "Costo", "peso": 8.72},
    {"id": "C6", "nombre": "Complejidad y desafíos de ejecución técnica", "tipo": "Costo", "peso": 3.83},
    {"id": "C7", "nombre": "Impacto en el servicio y desarrollo humano", "tipo": "Beneficio", "peso": 2.02},
]

ESCALA_MIN, ESCALA_MAX, ESCALA_DEFECTO = 1, 10, 5

def cop(valor: float) -> str:
    return "$" + f"{valor:,.0f}".replace(",", ".")

def iniciar_estado():
    st.session_state.setdefault("autenticado", False)
    st.session_state.setdefault("usuario", "")
    st.session_state.setdefault("proyectos", [])
    st.session_state.setdefault("presupuesto", 1_500_000_000)

iniciar_estado()

if not st.session_state.autenticado:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("## Coca-Cola FEMSA\n### DSS CAPEX Barranquilla")
        st.write("Sistema de soporte a la decisión para proyectos de inversión.")
    with col2:
        st.subheader("Iniciar sesión")
        u = st.text_input("Usuario", value="admin")
        p = st.text_input("Contraseña", type="password", value="1234")
        if st.button("Ingresar", use_container_width=True):
            if u.lower() == "admin" and p == "1234":
                st.session_state.autenticado = True
                st.session_state.usuario = u
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Use admin / 1234")
else:
    st.sidebar.write(f"**Usuario:** {st.session_state.usuario}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["Presupuesto", "Registrar proyecto", "Portafolio y Optimización"])
    
    with tab1:
        st.subheader("Presupuesto CAPEX disponible")
        st.number_input("Presupuesto (COP)", min_value=0, step=10_000, key="presupuesto")
        st.markdown("#### Ponderación de Criterios AHP")
        st.dataframe(pd.DataFrame(CRITERIOS), hide_index=True, use_container_width=True)

    with tab2:
        st.subheader("Registrar un proyecto nuevo")
        with st.form("form_reg", clear_on_submit=True):
            nombre = st.text_input("Nombre del proyecto")
            costo = st.number_input("Costo CAPEX (COP)", min_value=0, step=10_000)
            zona = st.selectbox("Zona de la planta", list(ZONAS.keys()), index=None, placeholder="Seleccione una zona")
            
            puntajes = {}
            for c in CRITERIOS:
                puntajes[c["id"]] = st.slider(f"{c['id']}: {c['nombre']}", ESCALA_MIN, ESCALA_MAX, ESCALA_DEFECTO)
                
            enviado = st.form_submit_button("Agregar proyecto")
            if enviado:
                if not nombre.strip():
                    st.error("Ingrese el nombre del proyecto.")
                elif costo <= 0:
                    st.error("Ingrese un costo mayor a cero.")
                elif zona is None:
                    st.error("Seleccione una zona de la planta.")
                else:
                    st.session_state.proyectos.append({
                        "Proyecto": nombre.strip(),
                        "Zona": zona,
                        "CAPEX (COP)": int(costo),
                        "Aprobado": False,
                        **puntajes
                    })
                    st.success("Proyecto agregado con éxito.")

    with tab3:
        st.subheader("Portafolio y Optimización Multicriterio")
        proys = st.session_state.proyectos
        if not proys:
            st.info("Aún no hay proyectos registrados. Añada proyectos en la pestaña anterior.")
        else:
            df = pd.DataFrame(proys)
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.markdown("---")
            st.markdown("#### Estado de Zonas en la Planta")
            st.success("Aplicación funcionando correctamente.")
