import streamlit as st
import pandas as pd
import numpy as np
import io
import time
import os
import base64
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="SIVIGILA VALIDADOR | IDS Norte de Santander",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS DE ALTA GAMA (Sin cajas fantasma) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        /* Eliminar todo el ruido de Streamlit */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {padding-top: 1rem !important;}

        /* Fondo de Pantalla */
        .stApp {
            background: #050505 !important;
            font-family: 'Outfit', sans-serif;
        }

        /* Contenedor Principal IDS */
        .ids-container {
            text-align: center;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        /* Branding Elite */
        .elite-title {
            font-size: 5rem;
            font-weight: 800;
            letter-spacing: -3px;
            background: linear-gradient(135deg, #FF3B30 0%, #D72C21 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            line-height: 1.1;
        }

        .inst-label {
            color: #8E8E93;
            font-size: 1.1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 500;
        }

        .obs-label {
            color: #FF3B30;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 5px;
            font-weight: 700;
            margin-top: 10px;
            display: block;
        }

        /* Estilo para el Logo */
        .logo-img {
            max-width: 110px;
            margin-bottom: 20px;
            filter: drop-shadow(0 10px 20px rgba(255, 59, 48, 0.2));
        }

        /* Cargador de Archivos IDS */
        .stFileUploader section {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 2px dashed rgba(255, 255, 255, 0.1) !important;
            border-radius: 30px !important;
            padding: 40px !important;
            transition: 0.3s ease;
        }
        
        /* Botón de Fusión IDS */
        div.stButton {
            text-align: center;
            display: flex;
            justify-content: center;
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #FF3B30 0%, #B22222 100%) !important;
            color: white !important;
            border-radius: 24px !important;
            border: none !important;
            height: 85px !important;
            width: 100% !important;
            max-width: 900px !important;
            font-size: 1.8rem !important;
            font-weight: 900 !important;
            box-shadow: 0 15px 45px rgba(255, 59, 48, 0.4) !important;
            margin-top: 35px !important;
            text-transform: uppercase;
            transition: 0.4s all ease !important;
        }

        .stButton>button:hover {
            transform: translateY(-5px) scale(1.01);
            box-shadow: 0 25px 60px rgba(255, 59, 48, 0.6) !important;
            filter: brightness(1.2);
        }

        /* Métricas */
        .metric-card {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 24px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            margin-top: 20px;
        }

        /* Ocultar iconos de enlace de Streamlit */
        a.anchor-link {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Centrado manual de la APP
    _, center_col, _ = st.columns([1, 8, 1])

    with center_col:
        # LOGO E IDENTIDAD
        st.markdown('<div class="ids-container">', unsafe_allow_html=True)
        
        # Logo IDS (si existe archivo local)
        if os.path.exists("logo_ids.png"):
            with open("logo_ids.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{encoded_string}" class="logo-img">', unsafe_allow_html=True)
        
        st.markdown('<div class="elite-title">SIVIGILA VALIDADOR</div>', unsafe_allow_html=True)
        st.markdown('<div class="inst-label">Instituto Departamental de Salud de Norte de Santander</div>', unsafe_allow_html=True)
        st.markdown('<div class="obs-label">Observatorio de Salud Pública</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # SECCIÓN DE CARGA
        st.markdown("<br>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Cargar archivos", 
            accept_multiple_files=True, 
            type=['xlsx', 'xls', 'csv'],
            label_visibility="collapsed"
        )

        if uploaded_files:
            st.markdown(f'<div style="color:#34C759; font-weight:700; font-size:1.1rem; text-align:center; padding-top:10px;">🛡️ {len(uploaded_files)} ARCHIVOS OFICIALES DETECTADOS</div>', unsafe_allow_html=True)
            
            if st.button("🚀 INICIAR CONSOLIDACIÓN"):
                with st.status("🛠️ Ejecutando Motor SIVIGILA ELITE...", expanded=False) as status:
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
                        if col_clas:
                            df_all = df_all[~df_all[col_clas].astype(str).str.lower().str.contains('sospecho', na=False)]

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
                        status.update(label="✅ ÉXITO", state="complete")
                        st.balloons()
                        
                        # Resultados
                        m1, m2 = st.columns(2)
                        with m1: st.markdown(f'<div class="metric-card"><h2 style="color:white; margin:0; font-size:3rem;">{len(df_final):,}</h2><p style="color:#8E8E93; text-transform:uppercase; font-size:0.8rem;">Casos Consolidados</p></div>', unsafe_allow_html=True)
                        with m2: st.markdown(f'<div class="metric-card"><h2 style="color:white; margin:0; font-size:3rem;">{len(dfs)}</h2><p style="color:#8E8E93; text-transform:uppercase; font-size:0.8rem;">Fuentes Unidas</p></div>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 DESCARGAR REPORTE MAESTRO (.XLSX)",
                            data=output.getvalue(),
                            file_name=f"MAESTRO_SIVIGILA_IDS_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    st.markdown(f'<div style="text-align:center; color:#333; font-size:0.8rem; padding:60px;">SIVIGILA ELITE v5.2 | IDS NORTE DE SANTANDER | {datetime.now().year}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
