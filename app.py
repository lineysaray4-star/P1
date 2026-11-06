import streamlit as st

import hashlib
import hmac
import os
import pandas as pd
import streamlit as st

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
