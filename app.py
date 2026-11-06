import streamlit as st
import pandas as pd
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
    "Nave L6": (0.31095747354216186, 0.08699999749660495, -0.09699846057785132),
    "Ed. Administrativo": (-0.07874717105732765, 0.09099999815225607, -0.23654998297975738),
    "Preparación Jarabes": (-0.013443761457189785, 0.05499999970197681, -0.14972857999926314),
    "Nave L5": (-0.09089336728148145, 0.07400000095367408, 0.07752296034716412),
    "PTAP": (0.12499999999999997, 0.010584891122769335, -0.2363998271227059),
    "Maquinaria Auxiliar": (0.1860000044107437, 0.0700554942389611, -0.13439330552842252),
    "Almacén Materia Prima": (0.1700819621994647, 0.07299999892711663, -0.05582385538161948),
    "Taller de Mantenimiento": (0.19953637767854035, 0.03386482627182549, 0.13097029633538382),
    "Almacén PT en planta": (0.0538323273132143, 0.061060169521544444, 0.12156740429218583),
    "Almacén central": (0.18799373139715855, 0.039899417710736955, 0.2870783195681461),
    "Almacén Seco y Refrigerado": (0.0012084420549271502, 0.07299999892711638, 0.04818980943480068),
    "CIP 2": (-0.01460114631312015, 0.04090899974107726, -0.24110309246762462),
    "Laboratorios": (0.10358284547294576, 0.045865267973078036, -0.1947381537866647),
    "Bodega de Almacenamiento": (-0.29963034614982303, 0.11264454480419347, 0.14350582712963567),
    "Almacén PT": (-0.3069817277842968, 0.08633417902238952, -0.10139923260685907),
    "Planta de Aguas Residuales": (0.004633314922293019, 0.05606578030616742, 0.3222373928443619),
    "Línea San Martín": (0.04421036936912598, 0.07299999892711641, -0.04519489950444283),
    "Línea Krones": (0.12451313042184067, 0.07299999892711619, -0.05447401664876847),
    "Línea Simonazzi": (0.0048294256531618285, 0.07299999892711641, -0.060003292869562075),
    "Línea Caraballo": (0.08001537821140972, 0.07299999892711619, -0.07427136327536349),
}

VISOR = {
    "COLOR_CONTORNO": "#2b4a63", "GROSOR": 1.4, "ANGULO": 35,
    "COLOR_BASE": "#d9ebf9", "COLOR_BORDE_BASE": "#2b4a63",
    "LUZ_CIELO": 1.00, "LUZ_SUELO": 0.35, "FUERZA_SOL": 0.40,
    "SOL_AZIMUT": 40, "SOL_ELEVACION": 55, "FONDO": "#f5f5f5",
    "COLOR_APROBADO": "#1B7F3B", "GIRO_AUTOMATICO": "false",
}

PLANTILLA_VISOR = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; background: __FONDO__; overflow: hidden;
    font-family: "Plus Jakarta Sans", "Segoe UI", Arial, sans-serif; }
  #visor { width: 100%; height: 100%; position: relative; }
  #visor canvas { display: block; }
  #cargando { position: absolute; inset: 0; display: flex; align-items: center;
    justify-content: center; color: #555B63; font-size: 0.95rem; background: __FONDO__; z-index: 10; }
  .Hotspot { position: absolute; width: 20px; height: 20px; padding: 0; border-radius: 50%;
    border: 3px solid #fff; box-shadow: 0 0 12px rgba(27,127,59,0.8); cursor: pointer;
    transform: translate(-50%, -50%); transition: transform .2s ease; z-index: 5;
    background: __COLOR_APROBADO__; animation: pulse 1.8s infinite; }
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(27, 127, 59, 0.7); }
    70% { box-shadow: 0 0 0 12px rgba(27, 127, 59, 0); }
    100% { box-shadow: 0 0 0 0 rgba(27, 127, 59, 0); }
  }
  .Hotspot:hover { transform: translate(-50%, -50%) scale(1.4); z-index: 20; }
  .HotspotAnnotation { display: none; position: absolute; bottom: 26px; left: 50%;
    transform: translateX(-50%); background: #fff; border-left: 4px solid __COLOR_APROBADO__;
    border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,.25); color: #1F1F1F;
    font-size: 11px; font-weight: 600; padding: 6px 10px; white-space: nowrap; pointer-events: none; }
  .Hotspot:hover .HotspotAnnotation { display: block; }
  .HotspotAnnotation small { display: block; font-weight: 500; color: #555B63; margin-top: 2px; }
  .leyenda { position: absolute; left: 12px; bottom: 12px; z-index: 6; background: #fff;
    border: 1px solid #E3E3E3; border-radius: 8px; padding: 8px 12px; font-size: 12px; color: #1F1F1F; }
  .leyenda span { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; background: __COLOR_APROBADO__; }
</style>
<script type="importmap">
{"imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
}}
</script></head>
<body>
<div id="visor">
  <div id="cargando">Cargando modelo 3D de la planta…</div>
  <div id="hotspots-container">__HOTSPOTS__</div>
  <div class="leyenda">
    <div><span></span>Zona con Proyecto Aprobado</div>
  </div>
</div>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";

const GLB = "__GLB_RUTA__";
const contenedor = document.getElementById("visor");

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
contenedor.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 5000);

const hemi = new THREE.HemisphereLight(0xffffff, 0xffffff, __LUZ_CIELO__ * Math.PI * 0.75);
hemi.groundColor.setScalar(__LUZ_SUELO__);
scene.add(hemi);

const sol = new THREE.DirectionalLight(0xffffff, __FUERZA_SOL__ * Math.PI * 1.6);
sol.castShadow = true;
sol.shadow.mapSize.set(2048, 2048);
scene.add(sol);
scene.add(sol.target);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.autoRotate = __GIRO_AUTOMATICO__;
controls.maxPolarAngle = Math.PI * 0.49;

const matLinea = new LineMaterial({
  color: new THREE.Color("__COLOR_CONTORNO__").getHex(), linewidth: __GROSOR__, worldUnits: false
});

function ajustarTamano() {
  const w = contenedor.clientWidth, h = contenedor.clientHeight;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  matLinea.resolution.set(w, h);
}
window.addEventListener("resize", ajustarTamano);
ajustarTamano();

const hotspotCoords = [];
document.querySelectorAll(".Hotspot").forEach((el) => {
  hotspotCoords.push({
    element: el,
    position: new THREE.Vector3(parseFloat(el.dataset.x), parseFloat(el.dataset.y), parseFloat(el.dataset.z)),
  });
});

const tmp = new THREE.Vector3();
function actualizarHotspots() {
  const w = contenedor.clientWidth, h = contenedor.clientHeight;
  hotspotCoords.forEach((item) => {
    tmp.copy(item.position).project(camera);
    if (tmp.z > 1) { item.element.style.display = "none"; return; }
    item.element.style.display = "block";
    item.element.style.left = ((tmp.x * 0.5 + 0.5) * w) + "px";
    item.element.style.top = ((tmp.y * -0.5 + 0.5) * h) + "px";
  });
}

new GLTFLoader().load(GLB, (gltf) => {
  const modelo = gltf.scene;
  modelo.traverse((o) => {
    if (o.isMesh) {
      o.castShadow = true; o.receiveShadow = true;
      const aristas = new THREE.EdgesGeometry(o.geometry, __ANGULO__);
      const contorno = new LineSegments2(new LineSegmentsGeometry().fromEdgesGeometry(aristas), matLinea);
      contorno.raycast = () => {};
      o.add(contorno);
    }
  });
  scene.add(modelo);

  const caja = new THREE.Box3().setFromObject(modelo);
  const centro = caja.getCenter(new THREE.Vector3());
  const tam = caja.getSize(new THREE.Vector3());
  const radio = Math.max(tam.x, tam.y, tam.z);

  const geoPlat = new THREE.PlaneGeometry(tam.x * 1.15, tam.z * 1.15);
  const plataforma = new THREE.Mesh(geoPlat, new THREE.MeshLambertMaterial({ color: "__COLOR_BASE__", side: THREE.DoubleSide }));
  plataforma.rotation.x = -Math.PI / 2;
  plataforma.position.set(centro.x, caja.min.y - 0.001, centro.z);
  plataforma.receiveShadow = true;
  scene.add(plataforma);

  controls.target.copy(centro);
  const az = THREE.MathUtils.degToRad(35), pol = THREE.MathUtils.degToRad(62), dist = radio * 1.5;
  camera.position.set(
    centro.x + dist * Math.sin(pol) * Math.sin(az),
    centro.y + dist * Math.cos(pol),
    centro.z + dist * Math.sin(pol) * Math.cos(az)
  );
  camera.near = radio / 100; camera.far = radio * 20;
  camera.updateProjectionMatrix();
  controls.minDistance = radio * 0.3; controls.maxDistance = radio * 4;
  controls.update();

  document.getElementById("cargando").remove();
}, undefined, (e) => {
  document.getElementById("cargando").textContent = "Error al cargar el modelo 3D";
  console.error(e);
});

renderer.setAnimationLoop(() => {
  controls.update();
  actualizarHotspots();
  renderer.render(scene, camera);
});
</script></body></html>
"""

def zonas_aprobadas_desde(proyectos):
    aprobadas = {}
    for p in proyectos:
        if p.get("Aprobado") and p.get("Zona") in ZONAS:
            aprobadas.setdefault(p["Zona"], []).append(p["Proyecto"])
    return aprobadas

def construir_html_visor(proyectos, altura=520):
    aprobadas = zonas_aprobadas_desde(proyectos)
    glb_path = "static/PLANTA_COCA_COLA_BARRANQUILLA.glb"
    glb_data_url = ""
    if os.path.exists(glb_path):
        with open(glb_path, "rb") as f:
            glb_b64 = base64.b64encode(f.read()).decode("utf-8")
        glb_data_url = f"data:model/gltf-binary;base64,{glb_b64}"

    puntos = []
    for nombre, lista in aprobadas.items():
        if nombre in ZONAS:
            x, y, z = ZONAS[nombre]
            detalle = "<small>" + html_lib.escape(", ".join(lista)) + "</small>"
            puntos.append(
                f'<div class="Hotspot" data-x="{x}" data-y="{y}" data-z="{z}">'
                f'<div class="HotspotAnnotation">{html_lib.escape(nombre)}{detalle}</div></div>'
            )

    salida = PLANTILLA_VISOR.replace("__HOTSPOTS__", "".join(puntos)).replace("__GLB_RUTA__", glb_data_url)
    for clave, valor in VISOR.items():
        salida = salida.replace(f"__{clave}__", str(valor))
    return components.html(salida, height=altura, scrolling=False)

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

# ESTILOS CORPORATIVOS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    :root {
      --cc-red: #F40009;
      --cc-red-dark: #880007;
      --cc-ink: #1F1F1F;
      --cc-slate: #555863;
      --cc-line: #E3E3E3;
      --cc-bg: #F5F5F5;
      --cc-ok: #187F3B;
    }
    html, body, stApp, [class*="css"], button, input, textarea {
      font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif !important;
    }
    .stApp { background: var(--cc-bg); color: var(--cc-ink); }
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 1.5rem; max-width: 1200px; }
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
      background: var(--cc-red); color: #FFFFFF; border: 0; border-radius: 999px;
      font-weight: 600; padding: 0.55rem 1.6rem; transition: background 0.15s ease;
    }
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
      background: var(--cc-red-dark); color: #FFFFFF;
    }
    .login-panel {
      background: var(--cc-red); color: #FFFFFF; border-radius: 16px; padding: 3rem 2.5rem;
      min-height: 520px; display: flex; flex-direction: column; justify-content: space-between;
    }
    .login-brand { font-size: 2.4rem; font-weight: 800; letter-spacing: -1.5px; line-height: 1; }
    .login-brand span {
      display: inline-block; margin-left: 0.5rem; padding: 3px 9px; background: #FFFFFF; color: var(--cc-red);
      font-size: 0.7rem; font-weight: 800; letter-spacing: 1px; border-radius: 4px; vertical-align: middle;
    }
    .login-headline { font-size: 1.9rem; font-weight: 700; line-height: 1.25; max-width: 24ch; margin: 0; }
    .login-sub { font-size: 0.95rem; opacity: 0.92; max-width: 42ch; margin: 0.9rem 0 0 0; line-height: 1.55; }
    .topbar {
      background: #FFFFFF; border-radius: 12px; border-bottom: 4px solid var(--cc-red);
      padding: 0.9rem 1.5rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06); margin-bottom: 1.5rem;
    }
    .topbar-brand { font-size: 1.35rem; font-weight: 800; color: var(--cc-red); letter-spacing: -0.8px; }
    .topbar-brand span { margin-left: 0.4rem; padding: 2px 7px
