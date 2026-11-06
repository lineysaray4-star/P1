import streamlit as st
import pandas as pd
import hashlib
import hmac
import os

# ----------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Coca-Cola FEMSA | DSS CAPEX Barranquilla",
    page_icon="🥤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------
# CRITERIOS AHP (pesos tomados del Excel de la Alternativa 1)
# ----------------------------------------------------------------------
CRITERIOS = [
    {"id": "C1", "nombre": "Alineación estratégica y LRP", "tipo": "Beneficio", "peso": 13.99},
    {"id": "C2", "nombre": "Rentabilidad y optimización de recursos", "tipo": "Beneficio", "peso": 20.53},
    {"id": "C3", "nombre": "Continuidad operativa y salud de activos", "tipo": "Beneficio", "peso": 18.94},
    {"id": "C4", "nombre": "Seguridad y cumplimiento normativo", "tipo": "Beneficio", "peso": 31.97},
    {"id": "C5", "nombre": "Gestión de riesgos técnicos y operacionales", "tipo": "Costo", "peso": 8.72},
    {"id": "C6", "nombre": "Complejidad y desafíos de ejecución técnica", "tipo": "Costo", "peso": 3.83},
    {"id": "C7", "nombre": "Impacto en el servicio y desarrollo humano", "tipo": "Beneficio", "peso": 2.02},
]
assert abs(sum(c["peso"] for c in CRITERIOS) - 100) < 1e-6, "Los pesos AHP deben sumar 100%"

ESCALA_MIN, ESCALA_MAX, ESCALA_DEFECTO = 1, 10, 5

# ----------------------------------------------------------------------
# ESTILOS CORPORATIVOS
# ----------------------------------------------------------------------
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --cc-red: #F40009;
        --cc-red-dark: #B80007;
        --cc-ink: #1F1F1F;
        --cc-slate: #555B63;
        --cc-line: #E3E3E3;
        --cc-bg: #F5F5F5;
        --cc-ok: #1B7F3B;
    }

    html, body, .stApp, [class*="css"], button, input, textarea {
        font-family: 'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif !important;
    }
    .stApp { background: var(--cc-bg); color: var(--cc-ink); }
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
    .block-container { padding-top: 1.5rem; max-width: 1200px; }

    /* Botones */
    .stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: var(--cc-red);
        color: #FFFFFF;
        border: 0;
        border-radius: 999px;
        font-weight: 600;
        padding: 0.55rem 1.6rem;
        transition: background 0.15s ease;
    }
    .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background: var(--cc-red-dark);
        color: #FFFFFF;
    }

    /* Pantalla de acceso */
    .login-panel {
        background: var(--cc-red);
        color: #FFFFFF;
        border-radius: 16px;
        padding: 3rem 2.5rem;
        min-height: 520px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .login-brand { font-size: 2.4rem; font-weight: 800; letter-spacing: -1.5px; line-height: 1; }
    .login-brand span {
        display: inline-block; margin-left: 0.5rem; padding: 3px 9px;
        background: #FFFFFF; color: var(--cc-red);
        font-size: 0.7rem; font-weight: 800; letter-spacing: 1px; border-radius: 4px;
        vertical-align: middle;
    }
    .login-headline { font-size: 1.9rem; font-weight: 700; line-height: 1.25; max-width: 24ch; margin: 0; }
    .login-sub { font-size: 0.95rem; opacity: 0.92; max-width: 42ch; margin: 0.9rem 0 0 0; line-height: 1.55; }
    .login-foot { font-size: 0.8rem; opacity: 0.85; margin: 0; }
    .login-form-top { height: 3.2rem; }

    /* Barra superior */
    .topbar {
        background: #FFFFFF;
        border-radius: 12px;
        border-bottom: 4px solid var(--cc-red);
        padding: 0.9rem 1.5rem;
        display: flex; align-items: center; justify-content: space-between; gap: 1rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
    }
    .topbar-brand { font-size: 1.35rem; font-weight: 800; color: var(--cc-red); letter-spacing: -0.8px; }
    .topbar-brand span {
        margin-left: 0.4rem; padding: 2px 7px; background: var(--cc-red); color: #FFFFFF;
        font-size: 0.62rem; letter-spacing: 1px; border-radius: 3px; vertical-align: middle;
    }
    .topbar-title { margin: 0; font-size: 1rem; font-weight: 700; color: var(--cc-ink); }
    .topbar-sub { margin: 2px 0 0 0; font-size: 0.78rem; color: var(--cc-slate); }
    .topbar-user { text-align: right; }
    .topbar-user p { margin: 0; font-size: 0.82rem; font-weight: 600; }
    .topbar-user .ok { color: var(--cc-ok); font-size: 0.74rem; }

    /* Encabezados de sección y métricas */
    .sec-title { margin: 0.4rem 0 0.2rem 0; font-size: 1.15rem; font-weight: 700; color: var(--cc-ink); }
    .sec-text { margin: 0 0 1rem 0; font-size: 0.88rem; color: var(--cc-slate); line-height: 1.55; max-width: 80ch; }
    div[data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid var(--cc-line);
        border-left: 4px solid var(--cc-red); border-radius: 10px; padding: 0.9rem 1.2rem;
    }
    div[data-testid="stForm"] {
        background: #FFFFFF; border: 1px solid var(--cc-line); border-radius: 12px; padding: 1.4rem 1.6rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# UTILIDADES
# ----------------------------------------------------------------------
def cop(valor: float) -> str:
    return "$" + f"{valor:,.0f}".replace(",", ".")

def _credenciales():
    try:
        return st.secrets["auth"]["usuario"], st.secrets["auth"]["password_sha256"]
    except Exception:
        pass
    usuario = os.environ.get("APP_USUARIO")
    clave_hash = os.environ.get("APP_PASSWORD_SHA256")
    if usuario and clave_hash:
        return usuario, clave_hash
    return None, None

def validar_acceso(usuario: str, clave: str) -> bool:
    usuario_ok, hash_ok = _credenciales()
    if not usuario_ok:
        return False
    coincide_usuario = hmac.compare_digest(usuario.strip().encode(), usuario_ok.encode())
    hash_ingresado = hashlib.sha256(clave.encode()).hexdigest()
    coincide_clave = hmac.compare_digest(hash_ingresado.encode(), hash_ok.strip().lower().encode())
    return coincide_usuario and coincide_clave

def iniciar_estado():
    st.session_state.setdefault("autenticado", False)
    st.session_state.setdefault("usuario", "")
    st.session_state.setdefault("intentos", 0)
    st.session_state.setdefault("proyectos", [])
    st.session_state.setdefault("presupuesto", 1_500_000_000)

MAX_INTENTOS = 5

def pantalla_login():
    izquierda, derecha = st.columns([1.15, 1], gap="large")
    with izquierda:
        st.markdown(
            """
            <div class="login-panel">
                <div class="login-brand">Coca-Cola<span>FEMSA</span></div>
                <div>
                    <p class="login-headline">Decisiones de inversión con criterio técnico y financiero.</p>
                    <p class="login-sub">Sistema de soporte a la decisión para priorizar y seleccionar los proyectos CAPEX de la Planta Barranquilla.</p>
                </div>
                <p class="login-foot">Acceso restringido a personal autorizado.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with derecha:
        st.markdown('<div class="login-form-top"></div>', unsafe_allow_html=True)
        st.markdown('<p class="sec-title" style="font-size:1.6rem;">Iniciar sesión</p>', unsafe_allow_html=True)
        st.markdown('<p class="sec-text">Ingrese las credenciales corporativas asignadas a su equipo.</p>', unsafe_allow_html=True)

        bloqueado = st.session_state.intentos >= MAX_INTENTOS
        if bloqueado:
            st.error("Se superó el número de intentos permitidos. Recargue la página.")

        with st.form("form_login", border=False):
            usuario = st.text_input("Usuario", placeholder="usuario.corporativo")
            clave = st.text_input("Contraseña", type="password")
            entrar = st.form_submit_button("Ingresar", use_container_width=True, disabled=bloqueado)

        if entrar:
            if validar_acceso(usuario, clave):
                st.session_state.autenticado = True
                st.session_state.usuario = usuario.strip()
                st.session_state.intentos = 0
                st.rerun()
            else:
                st.session_state.intentos += 1
                restantes = MAX_INTENTOS - st.session_state.intentos
                st.error(f"Credenciales incorrectas. Intentos restantes: {max(restantes, 0)}.")

# ----------------------------------------------------------------------
# APLICACIÓN PRINCIPAL
# ----------------------------------------------------------------------
def barra_superior():
    col_barra, col_salir = st.columns([6, 1], vertical_alignment="center")
    with col_barra:
        st.markdown(
            f"""
            <div class="topbar">
                <div class="topbar-brand">Coca-Cola<span>FEMSA</span></div>
                <div>
                    <p class="topbar-title">DSS CAPEX, Planta Barranquilla</p>
                    <p class="topbar-sub">Selección y optimización del portafolio de inversión</p>
                </div>
                <div class="topbar-user">
                    <p>{st.session_state.usuario}</p>
                    <p class="ok">Sesión activa</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_salir:
        if st.button("Salir", use_container_width=True):
            for k in ("autenticado", "usuario", "proyectos"):
                st.session_state.pop(k, None)
            st.rerun()

def seccion_presupuesto():
    st.markdown('<p class="sec-title">Presupuesto CAPEX disponible</p>', unsafe_allow_html=True)
    st.markdown('<p class="sec-text">Ingrese el monto exacto en pesos colombianos. Este valor será el límite de inversión.</p>', unsafe_allow_html=True)

    col_in, col_kpi = st.columns(2, gap="large")
    with col_in:
        st.number_input("Presupuesto CAPEX disponible (COP)", min_value=0, step=10_000, format="%d", key="presupuesto")
    with col_kpi:
        presupuesto = st.session_state.presupuesto
        if presupuesto > 0:
            st.metric("Límite de inversión configurado", f"{cop(presupuesto)} COP")
        else:
            st.metric("Límite de inversión configurado", "Sin definir")
            st.warning("Ingrese un presupuesto mayor a cero.")

    st.markdown('<p class="sec-title" style="margin-top:1.8rem;">Ponderación de criterios (AHP)</p>', unsafe_allow_html=True)
    tabla = pd.DataFrame(CRITERIOS).rename(columns={"id": "Código", "nombre": "Criterio", "tipo": "Tipo", "peso": "Peso (%)"})
    st.dataframe(tabla, hide_index=True, use_container_width=True, column_config={"Peso (%)": st.column_config.NumberColumn(format="%.2f%%")})

def seccion_registro():
    st.markdown('<p class="sec-title">Registrar un proyecto nuevo</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sec-text">Califique el proyecto de {ESCALA_MIN} a {ESCALA_MAX} en cada criterio.</p>', unsafe_allow_html=True)

    with st.form("form_proyecto", clear_on_submit=True):
        col_nombre, col_costo = st.columns([2, 1], gap="large")
        nombre = col_nombre.text_input("Nombre del proyecto")
        costo = col_costo.number_input("Costo CAPEX estimado (COP)", min_value=0, value=0, step=10_000, format="%d")

        puntajes = {}
        col_a, col_b = st.columns(2, gap="large")
        for i, c in enumerate(CRITERIOS):
            destino = col_a if i % 2 == 0 else col_b
            with destino:
                puntajes[c["id"]] = st.slider(
                    f'{c["id"]}: {c["nombre"]}',
                    min_value=ESCALA_MIN,
                    max_value=ESCALA_MAX,
                    value=ESCALA_DEFECTO,
                    help=f'Criterio de {c["tipo"].lower()}. Peso AHP: {c["peso"]:.2f}%.',
                )
        enviado = st.form_submit_button("Agregar proyecto")

    if enviado:
        nombre_limpio = nombre.strip()
        existentes = {p["Proyecto"].lower() for p in st.session_state.proyectos}
        if not nombre_limpio:
            st.error("Escriba el nombre del proyecto.")
        elif nombre_limpio.lower() in existentes:
            st.error("Ya existe un proyecto con ese nombre.")
        elif costo <= 0:
            st.error("Ingrese un costo CAPEX mayor a cero.")
        else:
            st.session_state.proyectos.append({"Proyecto": nombre_limpio, "CAPEX (COP)": int(costo), **puntajes})
            st.success(f"Proyecto «{nombre_limpio}» agregado con éxito.")

def seccion_portafolio():
    st.markdown('<p class="sec-title">Portafolio registrado</p>', unsafe_allow_html=True)
    proyectos = st.session_state.proyectos
    if not proyectos:
        st.info("Aún no hay proyectos registrados.")
        return

    df = pd.DataFrame(proyectos)
    total_capex = int(df["CAPEX (COP)"].sum())
    presupuesto = st.session_state.presupuesto

    m1, m2, m3 = st.columns(3, gap="large")
    m1.metric("Proyectos registrados", len(df))
    m2.metric("CAPEX total solicitado", cop(total_capex))
    m3.metric("Presupuesto disponible", cop(presupuesto))

    st.dataframe(df, hide_index=True, use_container_width=True, column_config={"CAPEX (COP)": st.column_config.NumberColumn(format="$%d")})

    col_sel, col_del, col_csv = st.columns([2, 1, 1], gap="large", vertical_alignment="bottom")
    with col_sel:
        a_eliminar = st.selectbox("Eliminar un proyecto", df["Proyecto"].tolist())
    with col_del:
        if st.button("Eliminar", use_container_width=True):
            st.session_state.proyectos = [p for p in proyectos if p["Proyecto"] != a_eliminar]
            st.rerun()
    with col_csv:
        st.download_button("Descargar CSV", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="portafolio_capex.csv", mime="text/csv", use_container_width=True)

def app_principal():
    barra_superior()
    st.write("")
    tab_pres, tab_reg, tab_port = st.tabs(["Presupuesto", "Registrar proyecto", "Portafolio"])
    with tab_pres:
        seccion_presupuesto()
    with tab_reg:
        seccion_registro()
    with tab_port:
        seccion_portafolio()

iniciar_estado()
if st.session_state.autenticado:
    app_principal()
else:
    pantalla_login()
