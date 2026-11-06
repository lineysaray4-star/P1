import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import html as html_lib
import streamlit.components.v1 as components
import base64
import os

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Coca-Cola FEMSA DSS CAPEX Barranquilla",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ZONAS DE LA PLANTA Y COORDENADAS 3D
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

# FUNCIONES DE CÁLCULO TOPSIS / AHP
def calcular_topsis(df_proyectos, criterios):
    """
    Ejecuta el algoritmo TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
    y retorna el DataFrame con los cálculos intermedios y el score final.
    """
    df = df_proyectos.copy()
    if df.empty:
        return df

    matriz_decision = df[[c["id"] for c in criterios]].values
    
    # 1. Normalización Vectorial (Vector Normalization)
    suma_cuadrados = np.sqrt(np.sum(matriz_decision**2, axis=0))
    suma_cuadrados[suma_cuadrados == 0] = 1 # Evitar división por cero
    matriz_normalizada = matriz_decision / suma_cuadrados

    # 2. Ponderación de la Matriz Normalizada (AHP Weights)
    pesos = np.array([c["peso"] / 100 for c in criterios])
    matriz_ponderada = matriz_normalizada * pesos

    # 3. Determinar Solución Ideal Positiva (A+) y Negativa (A-)
    a_plus = np.zeros(len(criterios))
    a_minus = np.zeros(len(criterios))

    for j, crit in enumerate(criterios):
        if crit["tipo"] == "Beneficio":
            a_plus[j] = np.max(matriz_ponderada[:, j])
            a_minus[j] = np.min(matriz_ponderada[:, j])
        else: # Costo
            a_plus[j] = np.min(matriz_ponderada[:, j])
            a_minus[j] = np.max(matriz_ponderada[:, j])

    # 4. Calcular Distancias Euclidianas a A+ y A-
    d_plus = np.sqrt(np.sum((matriz_ponderada - a_plus)**2, axis=1))
    d_minus = np.sqrt(np.sum((matriz_ponderada - a_minus)**2, axis=1))

    # 5. Calcular Coeficiente de Cercanía Relativa (Score TOPSIS)
    cc_score = np.where((d_plus + d_minus) == 0, 0, d_minus / (d_plus + d_minus))

    # Guardar resultados en el DataFrame
    df["Distancia A+ ($d_i^+$)"] = np.round(d_plus, 4)
    df["Distancia A- ($d_i^-$)"] = np.round(d_minus, 4)
    df["Score TOPSIS ($CC_i$)"] = np.round(cc_score, 4)
    
    return df

# VISOR 3D (OPTIMIZADO PARA CARGA DIRECTA)
PLANTILLA_VISOR = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<style>
  body { margin: 0; background: #f5f5f5; overflow: hidden; font-family: sans-serif; }
  #visor { width: 100vw; height: 100vh; position: absolute; top:0; left:0; }
  .Hotspot { position: absolute; width: 20px; height: 20px; border-radius: 50%; border: 3px solid #fff;
    box-shadow: 0 0 15px rgba(27,127,59,1); transform: translate(-50%, -50%);
    background: #1B7F3B; animation: pulse 1.5s infinite; cursor: pointer; z-index: 10;}
  @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(27, 127, 59, 0.8); } 70% { box-shadow: 0 0 0 15px rgba(27, 127, 59, 0); } 100% { box-shadow: 0 0 0 0 rgba(27, 127, 59, 0); } }
  .HotspotAnnotation { display: none; position: absolute; bottom: 25px; left: 50%; transform: translateX(-50%);
    background: #fff; border-left: 4px solid #1B7F3B; border-radius: 4px; padding: 5px 10px; font-size: 12px;
    font-weight: bold; white-space: nowrap; box-shadow: 0 2px 5px rgba(0,0,0,0.3); pointer-events: none;}
  .Hotspot:hover .HotspotAnnotation { display: block; }
</style>
<script type="importmap">{"imports": {"three": "https://unpkg.com/three@0.160.0/build/three.module.js", "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"}}</script>
</head><body>
<div id="visor">__HOTSPOTS__</div>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('visor').appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

const light = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
scene.add(light);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(10, 20, 10);
scene.add(dirLight);

const matLinea = new LineMaterial({ color: 0x2b4a63, linewidth: 1.5, worldUnits: false });
matLinea.resolution.set(window.innerWidth, window.innerHeight);

// Carga del modelo en Base64 para evitar errores de ruta
const loader = new GLTFLoader();
loader.load("__GLB_B64__", function (gltf) {
    const model = gltf.scene;
    model.traverse((o) => {
        if (o.isMesh) {
            const edges = new THREE.EdgesGeometry(o.geometry, 35);
            const line = new LineSegments2(new LineSegmentsGeometry().fromEdgesGeometry(edges), matLinea);
            o.add(line);
        }
    });
    scene.add(model);
    
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    
    controls.target.copy(center);
    camera.position.set(center.x + maxDim, center.y + maxDim, center.z + maxDim);
    controls.update();
});

const hotspots = [];
document.querySelectorAll('.Hotspot').forEach(el => {
    hotspots.push({ element: el, pos: new THREE.Vector3(parseFloat(el.dataset.x), parseFloat(el.dataset.y), parseFloat(el.dataset.z)) });
});

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    matLinea.resolution.set(window.innerWidth, window.innerHeight);
});

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    hotspots.forEach(h => {
        const p = h.pos.clone().project(camera);
        if (p.z > 1) { h.element.style.display = 'none'; } else {
            h.element.style.display = 'block';
            h.element.style.left = (p.x * .5 + .5) * window.innerWidth + 'px';
            h.element.style.top = (p.y * -.5 + .5) * window.innerHeight + 'px';
        }
    });
    renderer.render(scene, camera);
}
animate();
</script></body></html>"""

def construir_html_visor(proyectos, altura=600):
    aprobadas = {}
    for p in proyectos:
        if p.get("Aprobado") and p.get("Zona") in ZONAS:
            aprobadas.setdefault(p["Zona"], []).append(p["Proyecto"])
            
    glb_path = "static/PLANTA_COCA_COLA_BARRANQUILLA.glb"
    glb_data_url = ""
    if os.path.exists(glb_path):
        with open(glb_path, "rb") as f:
            glb_data_url = f"data:model/gltf-binary;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    else:
        st.warning("⚠️ Archivo 3D no encontrado. Verifica que 'static/PLANTA_COCA_COLA_BARRANQUILLA.glb' exista en el repositorio.")

    puntos_html = ""
    for zona, lista in aprobadas.items():
        x, y, z = ZONAS[zona]
        proyectos_str = ", ".join(lista)
        puntos_html += f'<div class="Hotspot" data-x="{x}" data-y="{y}" data-z="{z}"><div class="HotspotAnnotation">{zona}<br><small>{proyectos_str}</small></div></div>'

    html_final = PLANTILLA_VISOR.replace("__GLB_B64__", glb_data_url).replace("__HOTSPOTS__", puntos_html)
    return components.html(html_final, height=altura, scrolling=False)


# ESTILOS CORPORATIVOS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    :root { --cc-red: #F40009; --cc-ink: #1F1F1F; --cc-bg: #F8F9FA; --cc-ok: #187F3B; }
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stApp { background: var(--cc-bg); color: var(--cc-ink); }
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 1.2rem; max-width: 1400px; }
    .topbar { background: #FFFFFF; border-bottom: 4px solid var(--cc-red); padding: 1rem 1.5rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
    .sec-title { font-size: 1.2rem; font-weight: 700; color: var(--cc-ink); border-bottom: 2px solid #E3E3E3; padding-bottom: 5px; margin-bottom: 15px;}
    div[data-testid="stMetric"] { background: #FFFFFF; border-left: 4px solid var(--cc-red); border-radius: 6px; padding: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True
)

def cop(valor): return f"${valor:,.0f}".replace(",", ".")

def app_principal():
    st.markdown('<div class="topbar"><h2>Coca-Cola FEMSA | DSS CAPEX Barranquilla</h2><p style="margin:0; color:#555;">Soporte de Decisión Multicriterio (AHP/TOPSIS) e Integración 3D</p></div>', unsafe_allow_html=True)
    
    if "proyectos" not in st.session_state:
        st.session_state.proyectos = []
    if "presupuesto" not in st.session_state:
        st.session_state.presupuesto = 1500000000

    t1, t2, t3, t4 = st.tabs(["Presupuesto y Criterios", "Registrar Proyecto", "Análisis TOPSIS y Portafolio", "Dashboard 3D"])
    
    with t1:
        st.markdown('<p class="sec-title">Restricción de Capital y Matriz de Criterios (AHP)</p>', unsafe_allow_html=True)
        st.session_state.presupuesto = st.number_input("Presupuesto CAPEX (COP)", value=st.session_state.presupuesto, step=10000)
        st.dataframe(pd.DataFrame(CRITERIOS), use_container_width=True)

    with t2:
        st.markdown('<p class="sec-title">Evaluación Técnica de Proyectos</p>', unsafe_allow_html=True)
        with st.form("reg"):
            c1, c2, c3 = st.columns(3)
            nom = c1.text_input("Nombre del proyecto")
            cost = c2.number_input("CAPEX (COP)", min_value=0, step=10000)
            zon = c3.selectbox("Zona", list(ZONAS.keys()))
            
            puntos = {}
            ca, cb = st.columns(2)
            for i, c in enumerate(CRITERIOS):
                col = ca if i % 2 == 0 else cb
                puntos[c["id"]] = col.slider(f"{c['id']} ({c['tipo']}) - {c['peso']}%", 1, 10, 5)
            
            if st.form_submit_button("Registrar Proyecto") and nom and cost > 0:
                st.session_state.proyectos.append({"Proyecto": nom, "Zona": zon, "CAPEX (COP)": cost, "Aprobado": False, **puntos})
                st.success("Proyecto registrado.")

    with t3:
        st.markdown('<p class="sec-title">Optimización del Portafolio: Algoritmo TOPSIS</p>', unsafe_allow_html=True)
        modelo = st.selectbox("Modelo Analítico", ["Alternativa 1: Optimización TOPSIS con Restricción Presupuestaria", "Alternativa 2: Ponderación Simple"])
        
        if not st.session_state.proyectos:
            st.info("Registre proyectos para realizar el análisis.")
            return

        df_raw = pd.DataFrame(st.session_state.proyectos)
        df_calc = calcular_topsis(df_raw, CRITERIOS)
        
        # Selección por restricción presupuestaria basada en Score TOPSIS
        df_sorted = df_calc.sort_values(by="Score TOPSIS ($CC_i$)", ascending=False).copy()
        acum, sel = 0, []
        for _, row in df_sorted.iterrows():
            if acum + row["CAPEX (COP)"] <= st.session_state.presupuesto:
                acum += row["CAPEX (COP)"]
                sel.append(True)
            else:
                sel.append(False)
        df_sorted["Seleccionado"] = sel
        df_opt = df_sorted[df_sorted["Seleccionado"]].copy()

        # Actualizar estado de aprobación para el Dashboard 3D
        aprobados_set = set(df_opt["Proyecto"])
        for p in st.session_state.proyectos:
            p["Aprobado"] = p["Proyecto"] in aprobados_set

        c1, c2, c3 = st.columns(3)
        c1.metric("Proyectos Evaluados", len(df_raw))
        c2.metric("Inversión Óptima Asignada", cop(df_opt["CAPEX (COP)"].sum()))
        c3.metric("Eficiencia del Capital", f"{(df_opt['CAPEX (COP)'].sum() / st.session_state.presupuesto) * 100:.1f}%" if st.session_state.presupuesto > 0 else "0%")

        st.markdown("##### Matriz de Decisión y Resultados TOPSIS")
        st.dataframe(df_sorted.drop(columns=["Seleccionado"]), use_container_width=True)

        st.markdown("---")
        st.markdown("##### 📈 Análisis Analítico: Distancia a Solución Ideal ($A^+$) y Anti-Ideal ($A^-$)")
        
        # Gráfica avanzada de líneas y marcadores para A+ y A-
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Scatter(
            x=df_sorted["Proyecto"], y=df_sorted["Distancia A+ ($d_i^+$)"],
            mode='lines+markers', name='Distancia al Ideal ($d_i^+$) - Menor es mejor',
            line=dict(color='#1B7F3B', width=3, dash='dash'), marker=dict(size=10, symbol='circle')
        ))
        fig_dist.add_trace(go.Scatter(
            x=df_sorted["Proyecto"], y=df_sorted["Distancia A- ($d_i^-$)"],
            mode='lines+markers', name='Distancia al Anti-Ideal ($d_i^-$) - Mayor es mejor',
            line=dict(color='#F40009', width=3), marker=dict(size=10, symbol='square')
        ))
        fig_dist.update_layout(
            title="Comparativa de Distancias Euclidianas por Proyecto (Algoritmo TOPSIS)",
            xaxis_title="Proyectos Evaluados", yaxis_title="Distancia Euclidiana Normalizada",
            plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_dist.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        fig_dist.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
        
        st.plotly_chart(fig_dist, use_container_width=True)

    with t4:
        st.markdown('<p class="sec-title">Gemelo Digital 3D - Monitoreo de Asignación CAPEX</p>', unsafe_allow_html=True)
        col_3d, col_panel = st.columns([3.5, 1.2], gap="medium")
        
        with col_3d:
            construir_html_visor(st.session_state.proyectos, altura=650)
            
        with col_panel:
            st.markdown("##### 📌 Resumen de Inversión")
            aprobados = [p for p in st.session_state.proyectos if p["Aprobado"]]
            if aprobados:
                for p in aprobados:
                    st.markdown(
                        f"""<div style="background:#fff; border-left:4px solid #1B7F3B; padding:10px; margin-bottom:10px; box-shadow:0 1px 3px rgba(0,0,0,0.1);">
                        <strong>{p['Proyecto']}</strong><br><small style="color:#555;">{p['Zona']}</small><br><span style="color:#1B7F3B; font-weight:bold;">{cop(p['CAPEX (COP)'])}</span>
                        </div>""", unsafe_allow_html=True
                    )
            else:
                st.warning("No hay proyectos aprobados en el portafolio actual.")

if __name__ == "__main__":
    app_principal()
