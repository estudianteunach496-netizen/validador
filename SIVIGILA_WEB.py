import streamlit as st
import pandas as pd
import numpy as np
import io
import time
import os
from datetime import datetime

# Configuración de página con SEO y título Elite
st.set_page_config(
    page_title="SIVIGILA ELITE PRO | IDS Norte de Santander",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SISTEMA DE DISEÑO PREMIUM IDS (Dark Elite) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        /* Global Styles */
        .stApp {
            background: radial-gradient(circle at top right, #1a0a0a, #050505) !important;
            color: #ffffff !important;
            font-family: 'Outfit', sans-serif;
        }
        
        /* Ocultar elementos de Streamlit */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Glassmorphism Card Container */
        .master-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 40px;
            padding: 50px;
            margin: 20px auto;
            max-width: 950px;
            box-shadow: 0 40px 100px rgba(0, 0, 0, 0.7);
            text-align: center;
        }
        
        /* Typography */
        .elite-title {
            font-size: 4.8rem;
            font-weight: 800;
            letter-spacing: -3px;
            background: linear-gradient(135deg, #FF3B30 0%, #D72C21 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            line-height: 1;
        }
        
        .inst-name {
            font-size: 1.1rem;
            color: #8E8E93;
            font-weight: 500;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-top: 15px;
        }
        
        .obs-name {
            font-size: 0.9rem;
            color: #FF3B30;
            font-weight: 700;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-top: 10px;
            opacity: 0.8;
        }
        
        /* Custom Button */
        .stButton>button {
            background: linear-gradient(135deg, #FF3B30 0%, #B22222 100%) !important;
            color: white !important;
            border-radius: 25px !important;
            border: none !important;
            height: 80px !important;
            font-size: 1.6rem !important;
            font-weight: 800 !important;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 15px 45px rgba(255, 59, 48, 0.4) !important;
            margin: 40px auto !important;
            width: 100% !important;
            max-width: 600px;
        }
        
        .stButton>button:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 25px 60px rgba(255, 59, 48, 0.6) !important;
        }
        
        /* File Uploader Redesign */
        .stFileUploader section {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 2px dashed rgba(255, 255, 255, 0.12) !important;
            border-radius: 30px !important;
            padding: 40px !important;
        }
        
        /* Metrics */
        .metric-card {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 24px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            margin-top: 20px;
        }
        
        .metric-val { font-size: 3.2rem; font-weight: 800; color: #ffffff; line-height: 1; }
        .metric-lab { font-size: 0.85rem; color: #8E8E93; text-transform: uppercase; margin-top: 12px; letter-spacing: 1px; }

        /* Barra de Estado */
        .stStatus {
            border-radius: 24px !important;
            background: rgba(255, 59, 48, 0.05) !important;
            border: 1px solid rgba(255, 59, 48, 0.15) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- MASTER CONTAINER ---
    st.markdown('<div class="master-card">', unsafe_allow_html=True)
    
    # Logo Integration
    if os.path.exists("logo.png"):
        st.image("logo.png", width=180, use_container_width=False)
    else:
        st.markdown("<h1 style='font-size: 60px; margin-bottom:10px;'>🏥</h1>", unsafe_allow_html=True)

    # Header Text
    st.markdown('<div class="elite-title">SIVIGILA ELITE</div>', unsafe_allow_html=True)
    st.markdown('<div class="inst-name">Instituto Departamental de Salud de Norte de Santander</div>', unsafe_allow_html=True)
    st.markdown('<div class="obs-name">Observatorio de Salud Pública</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 40px;"></div>', unsafe_allow_html=True)
    
    # File Uploader
    uploaded_files = st.file_uploader(
        "Arrastra tus reportes oficiales aquí", 
        accept_multiple_files=True, 
        type=['xlsx', 'xls', 'csv'],
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.markdown(f'<div style="color:#34C759; font-weight:700; font-size:1.1rem; margin-top:20px;">✓ {len(uploaded_files)} ARCHIVOS EN COLA PARA FUSIÓN</div>', unsafe_allow_html=True)
        
        if st.button("🚀 INICIAR CONSOLIDACIÓN"):
            if len(uploaded_files) < 2:
                st.error("Se requieren mínimo 2 archivos.")
                return

            with st.status("�️ Ejecutando Motor ELITE v5.2...", expanded=True) as status:
                try:
                    start_time = time.time()
                    mapeo = {'num_ide_': ['num_ide_', 'num_ide', 'identificacion', 'documento'], 'tip_ide_': ['tip_ide_', 'tip_ide', 'tipo_id', 'tipo_doc'], 'cod_eve': ['cod_eve', 'evento', 'codigo_evento'], 'fec_not': ['fec_not', 'fecha_notificacion']}
                    dfs = []
                    for uploaded_file in uploaded_files:
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin-1', on_bad_lines='skip', dtype=str) 
                        else:
                            try: df = pd.read_excel(uploaded_file, engine='calamine', dtype=str)
                            except: df = pd.read_excel(uploaded_file, dtype=str)
                        
                        df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]
                        for std, vars in mapeo.items():
                            real = next((v for v in vars if v in df.columns), None)
                            if real: df.rename(columns={real: std}, inplace=True)
                        if 'num_ide_' in df.columns:
                            df = df.dropna(subset=['num_ide_'])
                            df['num_ide_'] = df['num_ide_'].str.extract(r'(\d+)')[0]
                            df = df.dropna(subset=['num_ide_'])
                        dfs.append(df)

                    df_all = pd.concat(dfs, ignore_index=True, sort=False)
                    if 'fec_not' in df_all.columns:
                        df_all['fec_not_dt'] = pd.to_datetime(df_all['fec_not'], errors='coerce')
                        df_all = df_all.dropna(subset=['fec_not_dt'])
                    col_clas = next((c for c in df_all.columns if 'clasific' in c or 'cla_fin' in c), None)
                    if col_clas: df_all = df_all[~df_all[col_clas].astype(str).str.lower().str.contains('sospecho', na=False)]
                    df_all['semana_epi'] = df_all['fec_not_dt'].dt.isocalendar().week
                    df_all['año_epi'] = df_all['fec_not_dt'].dt.isocalendar().year
                    df_all['_llave'] = (df_all['tip_ide_'].fillna('') + "-" + df_all['num_ide_'].fillna('') + "-" + df_all['cod_eve'].fillna(''))
                    df_all = df_all.sort_values(by=['_llave', 'fec_not_dt'])
                    df_all['diff'] = df_all.groupby('_llave')['fec_not_dt'].diff().dt.days.abs()
                    es_nuevo = (df_all['_llave'] != df_all['_llave'].shift(1)) | (df_all['diff'] > 4)
                    df_all['epid'] = pd.Series(es_nuevo).fillna(True).cumsum()
                    df_final = df_all.sort_values(by=['epid', 'fec_not_dt'], ascending=[True, False]).groupby('epid').first().reset_index()
                    df_final = df_final.drop(columns=['_llave', 'diff', 'epid', 'fec_not_dt'], errors='ignore')
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_final.to_excel(writer, index=False, sheet_name='CONSOLIDADO')
                    
                    total_time = time.time() - start_time
                    status.update(label=f"🌟 FUSIÓN COMPLETADA EN {total_time:.1f}s", state="complete")
                    st.balloons()
                    
                    # Results
                    m1, m2 = st.columns(2)
                    with m1: st.markdown(f'<div class="metric-card"><div class="metric-val">{len(df_final):,}</div><div class="metric-lab">Casos Consolidados</div></div>', unsafe_allow_html=True)
                    with m2: st.markdown(f'<div class="metric-card"><div class="metric-val">{len(dfs)}</div><div class="metric-lab">Fuentes Unidas</div></div>', unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📥 DESCARGAR RESULTADO MAESTRO (.XLSX)",
                        data=output.getvalue(),
                        file_name=f"MAESTRO_SIVIGILA_IDS_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    st.error(f"Falla: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center; color:#333; font-size:0.8rem; padding:40px;">SIVIGILA ELITE v5.2 | IDS NORTE DE SANTANDER | {datetime.now().year}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
