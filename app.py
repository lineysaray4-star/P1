import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import html as html_lib
import streamlit.components.v1 as components
import base64
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Coca-Cola FEMSA DSS CAPEX Barranquilla",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. ZONAS DE LA PLANTA Y COORDENADAS 3D
ZONAS = {
    "Nave L6": (0.3109, 0.0869, -0.0969), "Ed. Administrativo": (-0.0787, 0.0909, -0.2365),
    "Preparación Jarabes": (-0.0134, 0.0549, -0.1497), "Nave L5": (-0.0908, 0.0740, 0.0775),
    "PTAP": (0.1250, 0.0105, -0.2363), "Maquinaria Auxiliar": (0.1860, 0.0700, -0.1343),
    "Almacén Materia Prima": (0.1700, 0.0729, -0.0558), "Taller de Mantenimiento": (0.1995, 0.0338, 0.1309),
    "Almacén PT en planta": (0.0538, 0.0610, 0.1215), "Almacén central": (0.1879, 0.0398, 0.2870),
    "Almacén Seco y Refrigerado": (0.0012, 0.0729, 0.0481), "CIP 2": (-0.0146, 0.0409, -0.2411),
    "Laboratorios": (0.1035, 0.0458, -0.1947), "Bodega de Almacenamiento": (-0.2996, 0.1126, 0.1435),
    "Almacén PT": (-0.3069, 0.0863, -0.1013), "Planta de Aguas Residuales": (0.0046, 0.0560, 0.3222),
    "Línea San Martín": (0.0442, 0.0729, -0.0451), "Línea Krones": (0.1245, 0.0729, -0.0544),
    "Línea Simonazzi": (0.0048, 0.0729, -0.0600), "Línea Caraballo": (0.0800, 0.0729, -0.0742),
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

# 3. LÓGICA MATEMÁTICA DE LOS MODELOS (TOPSIS y Ponderación Simple)
def calcular_topsis(df_proyectos, criterios):
    df = df_proyectos.copy()
    matriz_decision = df[[c["id"] for c in criterios]].values
    
    # Normalización y Ponderación
    suma_cuadrados = np.sqrt(np.sum(matriz_decision**2, axis=0))
    suma_cuadrados[suma_cuadrados == 0] = 1 
    matriz_normalizada = matriz_decision / suma_cuadrados
    pesos = np.array([c["peso"] / 100 for c in criterios])
    matriz_ponderada = matriz_normalizada * pesos

    # Solución Ideal A+ y A-
    a_plus, a_minus = np.zeros(len(criterios)), np.zeros(len(criterios))
    for j, crit in enumerate(criterios):
        if crit["tipo"] == "Beneficio":
            a_plus[j], a_minus[j] = np.max(matriz_ponderada[:, j]), np.min(matriz_ponderada[:, j])
        else: 
            a_plus[j], a_minus[j] = np.min(matriz_ponderada[:, j]), np.max(matriz_ponderada[:, j])

    # Distancias
    d_plus = np.sqrt(np.sum((matriz_ponderada - a_plus)**2, axis=1))
    d_minus = np.sqrt(np.sum((matriz_ponderada - a_minus)**2, axis=1))
    cc_score = np.where((d_plus + d_minus) == 0, 0, d_minus / (d_plus + d_minus))

    df["Distancia A+ ($d_i^+$)"] = np.round(d_plus, 4)
    df["Distancia A- ($d_i^-$)"] = np.round(d_minus, 4)
    df["Score Analítico"] = np.round(cc_score, 4)
    return df

def calcular_ponderacion_simple(df_proyectos, criterios):
    df = df_proyectos.copy()
    scores = []
    for _, row in df.iterrows():
        score_total = 0
        for c in criterios:
            val = row[c["id"]]
            peso_frac = c["peso"] / 100.0
            if c["tipo"] == "Beneficio":
                score_total += ((val - ESCALA_MIN) / (ESCALA_MAX - ESCALA_MIN)) * peso_frac
            else:
                score_total += ((ESCALA_MAX - val) / (ESCALA_MAX - ESCALA_MIN)) * peso_frac
        scores.append(round(score_total, 4))
    
    df["Distancia A+ ($d_i^+$)"] = 0.0 # No aplica en este modelo
    df["Distancia A- ($d_i^-$)"] = 0.0 # No aplica en este modelo
    df["Score Analítico"] = scores
    return df

# 4. VISOR 3D (Súper optimizado para carga rápida, sin líneas de contorno pesadas)
PLANTILLA_VISOR = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<style>
  body { margin: 0; background: #f5f5f5; overflow: hidden; font-family: sans-serif; }
  #visor { width: 100vw; height: 100vh; position: absolute; top:0; left:0; }
  .Hotspot { position: absolute; width: 22px; height: 22px; border-radius: 50%; border: 3px solid #fff;
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

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 0.1, 5000);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.getElementById('visor').appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

const light = new THREE.HemisphereLight(0xffffff, 0x666666, 1.2);
scene.add(light);
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(20, 30, 20);
scene.add(dirLight);

const loader = new GLTFLoader();
loader.load("__GLB_B64__", function (gltf) {
    const model = gltf.scene;
    scene.add(model);
    
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    
    controls.target.copy(center);
    camera.position.set(center.x + maxDim * 1.1, center.y + maxDim * 0.9, center.z + maxDim * 1.1);
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

def construir_html_visor(proyectos, altura=650):
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
        st.warning("⚠️ Archivo 3D no encontrado en static/PLANTA_COCA_COLA_BARRANQUILLA.glb")

    puntos_html = ""
    for zona, lista in aprobadas.items():
        x, y, z = ZONAS[zona]
        proyectos_str = ", ".join(lista)
        puntos_html += f'<div class="Hotspot" data-x="{x}" data-y="{y}" data-z="{z}"><div class="HotspotAnnotation">{zona}<br><small>{proyectos_str}</small></div></div>'

    html_final = PLANTILLA_VISOR.replace("__GLB_B64__", glb_data_url).replace("__HOTSPOTS__", puntos_html)
    return components.html(html_final, height=altura, scrolling=False)

# 5. ESTILOS CORPORATIVOS
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
    st.markdown('<div class="topbar"><h2>Coca-Cola FEMSA | DSS CAPEX Barranquilla</h2><p style="margin:0; color:#555;">Sistema Integrado de Toma de Decisiones y Gemelo Digital</p></div>', unsafe_allow_html=True)
    
    if "proyectos" not in st.session_state: st.session_state.proyectos = []
    if "presupuesto" not in st.session_state: st.session_state.presupuesto = 1500000000

    t1, t2, t3, t4 = st.tabs(["Presupuesto y Criterios", "Registrar Proyecto", "Portafolio y Optimización", "Dashboard 3D e Indicadores"])
    
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
                # Los nombres de los criterios están completos aquí
                puntos[c["id"]] = col.slider(f"{c['id']}: {c['nombre']} ({c['tipo']})", 1, 10, 5)
            
            if st.form_submit_button("Registrar Proyecto") and nom and cost > 0:
                st.session_state.proyectos.append({"Proyecto": nom, "Zona": zon, "CAPEX (COP)": cost, "Aprobado": False, **puntos})
                st.success("Proyecto registrado con éxito.")

    with t3:
        st.markdown('<p class="sec-title">Cálculos Matemáticos y Optimización del Portafolio</p>', unsafe_allow_html=True)
        
        # EL SELECTOR DE MODELOS AHORA SÍ CAMBIA LA LÓGICA Y LOS RESULTADOS
        modelo = st.selectbox(
            "Seleccione el Modelo de Decisión para evaluar el Portafolio:", 
            [
                "Alternativa 1 - Modelo 1: TOPSIS + Restricción de Presupuesto (Prioriza Valor/Costo)", 
                "Alternativa 1 - Modelo 2: TOPSIS Ranking Directo (Prioriza solo el Score ideal)",
                "Alternativa 2 - Modelo 1: Ponderación Simple AHP (Suma ponderada clásica)"
            ]
        )
        
        if not st.session_state.proyectos:
            st.info("Registre proyectos para realizar el análisis.")
            return

        df_raw = pd.DataFrame(st.session_state.proyectos)
        
        # APLICACIÓN DE LA LÓGICA SEGÚN EL MODELO SELECCIONADO
        if "Ponderación Simple" in modelo:
            df_calc = calcular_ponderacion_simple(df_raw, CRITERIOS)
            # Ordenar por Score Analítico
            df_sorted = df_calc.sort_values(by="Score Analítico", ascending=False).copy()
        elif "Ranking Directo" in modelo:
            df_calc = calcular_topsis(df_raw, CRITERIOS)
            # Ordenar solo por Score TOPSIS
            df_sorted = df_calc.sort_values(by="Score Analítico", ascending=False).copy()
        else: # TOPSIS + Presupuesto (Valor/Costo)
            df_calc = calcular_topsis(df_raw, CRITERIOS)
            # Ordenar por Eficiencia: Score / Costo
            df_calc["Eficiencia (Score/CAPEX)"] = df_calc["Score Analítico"] / df_calc["CAPEX (COP)"]
            df_sorted = df_calc.sort_values(by="Eficiencia (Score/CAPEX)", ascending=False).copy()

        # Selección de proyectos hasta que se acabe el presupuesto
        acum, sel = 0, []
        for _, row in df_sorted.iterrows():
            if acum + row["CAPEX (COP)"] <= st.session_state.presupuesto:
                acum += row["CAPEX (COP)"]
                sel.append(True)
            else:
                sel.append(False)
        df_sorted["Seleccionado"] = sel
        df_opt = df_sorted[df_sorted["Seleccionado"]].copy()

        # Guardar estado de aprobados para el Dashboard
        aprobados_set = set(df_opt["Proyecto"])
        for p in st.session_state.proyectos:
            p["Aprobado"] = p["Proyecto"] in aprobados_set

        st.markdown("##### Matriz de Resultados del Modelo Elegido")
        st.dataframe(df_sorted.drop(columns=["Seleccionado"]), use_container_width=True)

        if "TOPSIS" in modelo:
            st.markdown("---")
            st.markdown("##### 🎯 Gráfica del Punto Ideal (Solución A+ y Distancias)")
            
            # Gráfica Cartesiana 2D demostrando la distancia al Punto Ideal
            fig_topsis = go.Figure()
            max_d_minus = df_sorted["Distancia A- ($d_i^-$)"].max() * 1.1 
            
            # 1. Trazar el Punto Ideal (Estrella Dorada en x=0, y=Max)
            fig_topsis.add_trace(go.Scatter(
                x=[0], y=[max_d_minus], mode="markers+text",
                marker=dict(color="#FFD700", size=22, symbol="star", line=dict(color="black", width=1)),
                text=["<b>PUNTO IDEAL (A+)</b>"], textposition="top right", name="Solución Ideal"
            ))

            # 2. Trazar los proyectos evaluados
            fig_topsis.add_trace(go.Scatter(
                x=df_sorted["Distancia A+ ($d_i^+$)"], y=df_sorted["Distancia A- ($d_i^-$)"],
                mode="markers+text", marker=dict(color="#1B7F3B", size=14),
                text=df_sorted["Proyecto"], textposition="bottom center", name="Proyectos"
            ))

            # 3. Líneas punteadas desde el proyecto hasta el Punto Ideal
            for i, row in df_sorted.iterrows():
                fig_topsis.add_trace(go.Scatter(
                    x=[0, row["Distancia A+ ($d_i^+$)"]], y=[max_d_minus, row["Distancia A- ($d_i^-$)"]],
                    mode="lines", line=dict(color="#F40009", dash="dot", width=1.5), showlegend=False
                ))

            fig_topsis.update_layout(
                title="Mapa 2D de Distancias al Punto Ideal (Se busca estar lo más cerca a la Estrella Dorada)",
                xaxis_title="Distancia al Ideal (d⁺) ➔ ¡Cercano a 0 es mejor!",
                yaxis_title="Distancia al Anti-Ideal (d⁻) ➔ ¡Mayor es mejor!",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_topsis.update_xaxes(showgrid=True, gridcolor='LightGrey', range=[-0.02, df_sorted["Distancia A+ ($d_i^+$)"].max() * 1.2])
            fig_topsis.update_yaxes(showgrid=True, gridcolor='LightGrey')
            st.plotly_chart(fig_topsis, use_container_width=True)

    with t4:
        st.markdown('<p class="sec-title">Dashboard Analítico y Gemelo Digital 3D</p>', unsafe_allow_html=True)
        
        aprobados = [p for p in st.session_state.proyectos if p["Aprobado"]]
        capex_usado = sum(p["CAPEX (COP)"] for p in aprobados)
        presupuesto = st.session_state.presupuesto
        
        # 1. MÉTRICAS CLAVE (KPIs del Dashboard)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Proyectos Aprobados", len(aprobados))
        m2.metric("Inversión CAPEX Total", cop(capex_usado))
        m3.metric("Presupuesto Restante", cop(presupuesto - capex_usado))
        m4.metric("Eficiencia de Asignación (%)", f"{(capex_usado / presupuesto) * 100:.1f}%" if presupuesto > 0 else "0%")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. VISOR 3D Y GRÁFICAS DE DISTRIBUCIÓN
        col_3d, col_graficas = st.columns([2.5, 1.5], gap="large")
        
        with col_3d:
            st.markdown("##### 🏭 Visualización Espacial (Zonas Aprobadas)")
            construir_html_visor(st.session_state.proyectos, altura=550)
            
        with col_graficas:
            st.markdown("##### 📊 Distribución y Costos")
            if aprobados:
                df_ap = pd.DataFrame(aprobados)
                
                # Gráfica Circular: Distribución de Presupuesto por Zona
                fig_pie = px.pie(df_ap, values="CAPEX (COP)", names="Zona", title="CAPEX Aprobado por Zona", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
                fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10))
                st.plotly_chart(fig_pie, use_container_width=True, height=250)
                
                # Gráfica de Barras: Costo CAPEX de Proyectos
                fig_bar = px.bar(df_ap, x="Proyecto", y="CAPEX (COP)", text_auto='.2s', title="Costo CAPEX por Proyecto Aprobado", color="CAPEX (COP)", color_continuous_scale=["#f8d7da", "#880007"])
                fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(t=40, b=10, l=10, r=10))
                st.plotly_chart(fig_bar, use_container_width=True, height=250)
            else:
                st.info("No hay proyectos aprobados en el portafolio para mostrar métricas.")

if __name__ == "__main__":
    app_principal()
