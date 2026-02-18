import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="SIVIGILA ELITE WEB", page_icon="🏥", layout="wide")

# Estilo CSS para que se vea de lujo (Rojo y Premium)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button {
        background-color: #E63946;
        color: white;
        border-radius: 20px;
        height: 3em;
        width: 100%;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #D62828;
        border: none;
        color: white;
    }
    h1 { color: #E63946; font-family: 'Arial'; }
    .css-10trblm { color: #f1f1f1; }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🏥 SIVIGILA ELITE v5.0")
    st.subheader("Consolidador Universal Epidemiológico")
    
    st.info("Sube tus archivos de Sivigila (Excel o CSV) para fusionarlos con inteligencia de prevalencia.")

    # Carga de archivos
    uploaded_files = st.file_uploader("Arrastra aquí tus archivos", accept_multiple_files=True, type=['xlsx', 'xls', 'csv'])

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} archivos cargados correctamente.")
        
        if st.button("🚀 INICIAR CONSOLIDACIÓN"):
            if len(uploaded_files) < 2:
                st.error("Por favor sube al menos 2 archivos.")
                return

            with st.spinner("Procesando datos con inteligencia ELITE..."):
                try:
                    mapeo = {
                        'num_ide_': ['num_ide_', 'num_ide', 'identificacion', 'documento'],
                        'tip_ide_': ['tip_ide_', 'tip_ide', 'tipo_id', 'tipo_doc'],
                        'cod_eve': ['cod_eve', 'evento', 'codigo_evento'],
                        'fec_not': ['fec_not', 'fecha_notificacion'],
                    }
                    
                    dfs = []
                    for uploaded_file in uploaded_files:
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='latin-1', on_bad_lines='skip')
                        else:
                            df = pd.read_excel(uploaded_file)
                        
                        # Limpieza básica
                        df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]
                        for std, vars in mapeo.items():
                            real = next((v for v in vars if v in df.columns), None)
                            if real: df.rename(columns={real: std}, inplace=True)
                        
                        if 'num_ide_' in df.columns:
                            df = df.dropna(subset=['num_ide_'])
                            df['num_ide_'] = df['num_ide_'].astype(str).str.extract(r'(\d+)')[0]
                            df = df.dropna(subset=['num_ide_'])
                        
                        if 'fec_not' in df.columns:
                            df['fec_not_dt'] = pd.to_datetime(df['fec_not'], errors='coerce')
                            if df['fec_not_dt'].isna().mean() > 0.5:
                                df['fec_not_dt'] = pd.to_datetime(df['fec_not'], dayfirst=True, errors='coerce')
                            df = df.dropna(subset=['fec_not_dt'])
                        
                        dfs.append(df)

                    # Lógica de prevalencia
                    df_all = pd.concat(dfs, ignore_index=True, sort=False)
                    df_all['_llave'] = (df_all['tip_ide_'].astype(str) + "-" + 
                                       df_all['num_ide_'].astype(str) + "-" + 
                                       df_all['cod_eve'].astype(str))
                    
                    df_all = df_all.sort_values(by=['_llave', 'fec_not_dt'])
                    df_all['diff'] = df_all.groupby('_llave')['fec_not_dt'].diff().dt.days.abs()
                    es_nuevo = (df_all['_llave'] != df_all['_llave'].shift(1)) | (df_all['diff'] > 4)
                    df_all['epid'] = np.cumsum(es_nuevo.fillna(True).values)
                    
                    df_final = df_all.sort_values(by=['epid', 'fec_not_dt'], ascending=[True, False]).groupby('epid').first().reset_index()

                    # Preparar descarga
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df_final.to_excel(writer, index=False, sheet_name='CONSOLIDADO')
                    
                    st.balloons()
                    st.success(f"✨ Fusión completa: {len(df_final):,} registros únicos encontrados.")
                    
                    st.download_button(
                        label="📥 DESCARGAR CONSOLIDADO ELITE",
                        data=output.getvalue(),
                        file_name=f"CONSOLIDADO_SIVIGILA_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                except Exception as e:
                    st.error(f"Error técnico: {str(e)}")

    st.markdown("---")
    st.caption("SIVIGILA ELITE v5.0 | Desarrollado para alta precisión epidemiológica.")

if __name__ == "__main__":
    main()
