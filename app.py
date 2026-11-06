import streamlit as st
import pandas as pd
import html as html_lib
import streamlit.components.v1 as components
import base64
import os

# Configuración de la página
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

def zonas_aprobadas_desde(proyectos):
    aprobadas = {}
    for p in proyectos:
        if p.get("Aprobado") and p.get("Zona") in ZONAS:
            aprobadas.setdefault(p["Zona"], []).append(p["Proyecto"])
    return aprobadas

def mostrar_modelo_3d(proyectos):
    glb_path = "static/PLANTA_COCA_COLA_BARRANQUILLA.glb"
    b64_data = ""
    if os.path.exists(glb_path):
        with open(glb_path, "rb") as f:
            b64_data = f"data:model/gltf-binary;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    
    aprobadas = zonas_aprobadas_desde(proyectos)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{ margin: 0; background: #f5f5f5; font-family: sans-serif; }}
      #visor {{ width: 100%; height: 600px; position: relative; }}
      .punto {{ position: absolute; width: 14px; height: 14px; background: #F40009; border-radius: 50%; border: 2px solid #fff; transform: translate(-50%, -50%); cursor: pointer; }}
      .punto.aprobado {{ background: #1B7F3B; }}
    </style>
    </head>
    <body>
    <div id="visor">
      <div style="padding: 20px; text-align: center; color: #555;">Visor 3D de Planta - Coca-Cola FEMSA</div>
    </div>
    </body>
    </html>
    """
    components.html(html_code, height=620)

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
    st.title("Iniciar sesión - DSS CAPEX")
    u = st.text_input("Usuario", value="admin")
    p = st.text_input("Contraseña", type="password", value="1234")
    if st.button("Ingresar"):
        if u.lower() == "admin" and p == "1234":
            st.session_state.autenticado = True
            st.session_state.usuario = u
            st.rerun()
        else:
            st.error("Credenciales incorrectas (admin / 1234)")
else:
    st.sidebar.title(f"Usuario: {st.session_state.usuario}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["Presupuesto", "Registrar proyecto", "Portafolio y Optimización"])
    
    with tab1:
        st.subheader("Presupuesto CAPEX disponible")
        st.number_input("Presupuesto (COP)", min_value=0, step=10_000, key="presupuesto")
        st.dataframe(pd.DataFrame(CRITERIOS), hide_index=True, use_container_width=True)

    with tab2:
        st.subheader("Registrar un proyecto nuevo")
        with st.form("form_reg", clear_on_submit=True):
            nombre = st.text_input("Nombre del proyecto")
            costo = st.number_input("Costo CAPEX (COP)", min_value=0, step=10_000)
            zona = st.selectbox("Zona de la planta", list(ZONAS.keys()), index=None, placeholder="Seleccione una zona")
            
            puntajes = {}
            for c in CRITERIOS:
                puntajes[c["id"]] = st.slider(f"{c['id']}: {c['nombre']}", 1, 10, 5)
                
            enviado = st.form_submit_button("Agregar proyecto")
            if enviado:
                if not nombre.strip():
                    st.error("Ingrese un nombre.")
                elif costo <= 0:
                    st.error("Ingrese un costo válido.")
                elif zona is None:
                    st.error("Seleccione una zona.")
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
        st.subheader("Portafolio y Optimización")
        proys = st.session_state.proyectos
        if not proys:
            st.info("No hay proyectos registrados.")
        else:
            df = pd.DataFrame(proys)
            st.dataframe(df, hide_index=True, use_container_width=True)
            st.markdown("---")
            st.subheader("Visualización 3D de la Planta")
            mostrar_modelo_3d(proys)
