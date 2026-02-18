import streamlit as st
import pandas as pd
import numpy as np
import io
import time
from datetime import datetime

# Configuración de página con SEO y título Elite
st.set_page_config(
    page_title="SIVIGILA ELITE PRO | Intelligence Hub",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SISTEMA DE DISEÑO PREMIUM (Glassmorphism + Apple Aesthetic) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600;800&family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        /* Global Styles */
        .stApp {
            background: radial-gradient(circle at top right, #1a1a1a, #050505) !important;
            color: #ffffff;
            font-family: 'SF Pro Display', 'Outfit', sans-serif;
        }
        
        /* Ocultar elementos de Streamlit */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* Glassmorphism Card Container */
        .main-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 35px;
            padding: 50px;
            margin: 20px auto;
            max-width: 900px;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6);
        }
        
        /* Typography con Centrado Real */
        .title-container {
            text-align: center;
            margin-bottom: 50px;
            width: 100%;
        }
        
        .elite-title {
            font-size: 4.5rem;
            font-weight: 800;
            letter-spacing: -3px;
            background: linear-gradient(135deg, #FF3B30 0%, #FF9500 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            padding: 0;
            line-height: 1;
        }
        
        .elite-subtitle {
            font-size: 1.1rem;
            color: #8E8E93;
            font-weight: 500;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-top: 15px;
        }
        
        /* Botón de Fusión Rediseñado */
        .stButton>button {
            background: linear-gradient(135deg, #FF3B30 0%, #D72C21 100%) !important;
            color: white !important;
            border-radius: 22px !important;
            border: none !important;
            height: 75px !important;
            font-size: 1.4rem !important;
            font-weight: 800 !important;
            transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1) !important;
            box-shadow: 0 12px 35px rgba(255, 59, 48, 0.4) !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stButton>button:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 20px 50px rgba(255, 59, 48, 0.6) !important;
            filter: brightness(1.2);
        }
        
        /* File Uploader Estilizado */
        .stFileUploader {
            padding-bottom: 30px;
        }
        
        .stFileUploader section[data-testid="stFileUploadDropzone"] {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 2px dashed rgba(255, 255, 255, 0.15) !important;
            border-radius: 28px !important;
            padding: 40px !important;
            transition: 0.3s;
        }
        
        /* Metrics Cards */
        .metric-box {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 24px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            text-align: center;
            transition: 0.3s;
        }
        
        .metric-box:hover {
            background: rgba(255, 255, 255, 0.07);
            border-color: rgba(255, 59, 48, 0.4);
        }
        
        .val { font-size: 2.8rem; font-weight: 800; color: #ffffff; line-height: 1;}
        .lab { font-size: 0.8rem; color: #8E8E93; text-transform: uppercase; margin-top: 10px; letter-spacing: 1px;}
        
        /* Mensajes de Éxito */
        .stAlert {
            border-radius: 20px !important;
            background: rgba(52, 199, 89, 0.1) !important;
            border: 1px solid rgba(52, 199, 89, 0.2) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- HEADER SECTION ---
    st.markdown("""
        <div class="title-container">
            <div class="elite-title">SIVIGILA ELITE PRO</div>
            <div class="elite-subtitle">Intelligence Hub & Data Consolidation Engine</div>
        </div>
    """, unsafe_allow_html=True)

    # --- MAIN UI CONTAINER ---
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown('<h3 style="color:#ffffff; font-weight:600; margin-bottom:25px; font-size:1.5rem;">📥 FUENTES DE DATOS</h3>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Reportes Sivigila", 
        accept_multiple_files=True, 
        type=['xlsx', 'xls', 'csv'],
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.markdown(f'<div style="color:#34C759; font-weight:700; font-size:1.1rem; margin-bottom:20px;">🛡️ {len(uploaded_files)} ARCHIVOS PROTEGIDOS Y LISTOS</div>', unsafe_allow_html=True)
        
        if st.button("🚀 FUSIONAR SISTEMA ELITE"):
            if len(uploaded_files) < 2:
                st.error("Se requieren al menos 2 archivos para la consolidación.")
                return

            with st.status("💎 OPERACIÓN ELITE v5.2 | Consolidando a alta fidelidad...", expanded=True) as status:
                try:
                    start_time = time.time()
                    mapeo = {
                        'num_ide_': ['num_ide_', 'num_ide', 'identificacion', 'documento'],
                        'tip_ide_': ['tip_ide_', 'tip_ide', 'tipo_id', 'tipo_doc'],
                        'cod_eve': ['cod_eve', 'evento', 'codigo_evento'],
                        'fec_not': ['fec_not', 'fecha_notificacion'],
                    }
                    
                    dfs = []
                    for uploaded_file in uploaded_files:
                        status.write(f"📥 Leyendo: **{uploaded_file.name}**")
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin-1', on_bad_lines='skip', dtype=str) 
                        else:
                            try:
                                df = pd.read_excel(uploaded_file, engine='calamine', dtype=str)
                            except:
                                df = pd.read_excel(uploaded_file, dtype=str)
                        
                        df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]
                        for std, vars in mapeo.items():
                            real = next((v for v in vars if v in df.columns), None)
                            if real: df.rename(columns={real: std}, inplace=True)
                        
                        if 'num_ide_' in df.columns:
                            df = df.dropna(subset=['num_ide_'])
                            df['num_ide_'] = df['num_ide_'].str.extract(r'(\d+)')[0]
                            df = df.dropna(subset=['num_ide_'])
                        
                        dfs.append(df)

                    status.write("🧹 Depurando registros sospechosos...")
                    df_all = pd.concat(dfs, ignore_index=True, sort=False)
                    
                    if 'fec_not' in df_all.columns:
                        df_all['fec_not_dt'] = pd.to_datetime(df_all['fec_not'], errors='coerce')
                        df_all = df_all.dropna(subset=['fec_not_dt'])
                    
                    col_clas = next((c for c in df_all.columns if 'clasific' in c or 'cla_fin' in c), None)
                    if col_clas:
                        df_all = df_all[~df_all[col_clas].astype(str).str.lower().str.contains('sospecho', na=False)]

                    df_all['semana_epi'] = df_all['fec_not_dt'].dt.isocalendar().week
                    df_all['año_epi'] = df_all['fec_not_dt'].dt.isocalendar().year

                    status.write("🧠 Sincronizando episodios clínicos...")
                    df_all['_llave'] = (df_all['tip_ide_'].fillna('') + "-" + df_all['num_ide_'].fillna('') + "-" + df_all['cod_eve'].fillna(''))
                    df_all = df_all.sort_values(by=['_llave', 'fec_not_dt'])
                    df_all['diff'] = df_all.groupby('_llave')['fec_not_dt'].diff().dt.days.abs()
                    es_nuevo = (df_all['_llave'] != df_all['_llave'].shift(1)) | (df_all['diff'] > 4)
                    df_all['epid'] = pd.Series(es_nuevo).fillna(True).cumsum()
                    
                    df_final = df_all.sort_values(by=['epid', 'fec_not_dt'], ascending=[True, False]).groupby('epid').first().reset_index()
                    df_final = df_final.drop(columns=['_llave', 'diff', 'epid', 'fec_not_dt'], errors='ignore')
                    
                    df_resumen = df_final.groupby('cod_eve').size().reset_index(name='total_casos')

                    status.write("📊 Finalizando reporte maestro...")
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_final.to_excel(writer, index=False, sheet_name='BASE_CONSOLIDADA')
                        df_resumen.to_excel(writer, index=False, sheet_name='RESUMEN')
                    
                    total_time = time.time() - start_time
                    status.update(label=f"🌟 FUSIÓN EXITOSA | {total_time:.1f} segundos", state="complete")
                    
                    st.balloons()
                    
                    # --- METRICS SECTION ---
                    st.markdown('<div style="margin-top: 40px;">', unsafe_allow_html=True)
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f'<div class="metric-box"><div class="val">{len(df_final):,}</div><div class="lab">Casos Consolidados</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.markdown(f'<div class="metric-box"><div class="val">{len(dfs)}</div><div class="lab">Fuentes Unidas</div></div>', unsafe_allow_html=True)
                    with m3:
                        st.markdown(f'<div class="metric-box"><div class="val">{total_time:.1f}s</div><div class="lab">Tiempo de Vuelo</div></div>', unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📥 DESCARGAR CONSOLIDADO ELITE PRO (.XLSX)",
                        data=output.getvalue(),
                        file_name=f"SIVIGILA_ELITE_PRO_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    status.update(label="❌ ERROR EN ENGINE", state="error")
                    st.error(f"Falla crítica: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

    # --- FOOTER ---
    st.markdown(
        f'<div style="text-align: center; color: #48484A; padding: 50px; font-size: 0.85rem; font-weight:500; letter-spacing:1px;">'
        f'SIVIGILA ELITE ENGINE v5.2 PRO | {datetime.now().year} | DATA INTELLIGENCE UNIT'
        f'</div>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
