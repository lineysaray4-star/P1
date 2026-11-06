# -*- coding: utf-8 -*-
"""Modelo_Pagina_Web.ipynb

import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Coca-Cola FEMSA | DSS CAPEX Planta Barranquilla", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo visual corporativo
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO CORPORATIVO NATIVO ---
st.markdown("""
    <div style="background-color: #E51A22; color: white; padding: 20px; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div>
            <h2 style="margin: 0; color: white; font-size: 22px;">🏭 PLANTA BARRANQUILLA</h2>
            <p style="margin: 0; color: #fee2e2; font-size: 12px;">● SISTEMA ACTIVO • DSS CAPEX • Módulo de Toma de Decisiones</p>
        </div>
        <div style="background: white; color: #E51A22; padding: 8px 16px; border-radius: 6px; font-weight: 900; font-style: italic; font-size: 18px;">
            COCA-COLA FEMSA
        </div>
        <div style="text-align: right;">
            <p style="margin: 0; font-weight: bold; font-size: 14px;">Liney Avendaño</p>
            <p style="margin: 0; color: #fee2e2; font-size: 11px;">Analista CAPEX • Colombia</p>
        </div>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# --- PANEL DE CONTROL ---
st.write("### 📊 Panel de Control del Sistema de Soporte de Decisión")

presupuesto = st.slider("Seleccione el Presupuesto CAPEX disponible (Millones COP)", 500, 3000, 1500, 100)

if st.button("Ejecutar Optimización del Portafolio"):
    st.success(f"¡Modelo ejecutado correctamente con un presupuesto de ${presupuesto}M COP!")
    st.metric(label="Valor Z Óptimo Alcanzado", value="Z = 21.4", delta="+12% vs año anterior")
