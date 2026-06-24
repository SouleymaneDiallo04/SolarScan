"""SolarScan — Dashboard d'inspection (Streamlit + folium).

Interface pour un ingenieur d'inspection : carte interactive de la centrale,
metriques, filtres par type de defaut, table des anomalies, export du rapport.

Lancement :
    streamlit run dashboard/app.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

ROOT = Path(__file__).resolve().parent.parent

st.set_page_config(page_title='SolarScan — Inspection', page_icon='☀️', layout='wide')
st.title('☀️ SolarScan — Dashboard d\'inspection')
st.caption('Détection de défauts sur panneaux solaires par imagerie thermique de drone')

report_path = ROOT / 'reports' / 'report.csv'
if not report_path.exists():
    st.warning('Aucun rapport trouvé. Lance d\'abord : `py pipeline/run_inspection.py`')
    st.stop()

df = pd.read_csv(report_path)
total = len(df)
n_anom = int(df['anomalie'].sum())

# --- Métriques ---
c1, c2, c3 = st.columns(3)
c1.metric('Panneaux inspectés', total)
c2.metric('Anomalies détectées', n_anom)
c3.metric("Taux d'anomalie", f'{100 * n_anom / total:.1f} %')

# --- Filtre ---
anomaly_types = sorted(df.loc[df['anomalie'] == 1, 'classe'].unique())
sel = st.multiselect('Filtrer par type de défaut', anomaly_types, default=anomaly_types)

left, right = st.columns([3, 2])

# --- Carte interactive ---
with left:
    st.subheader('🗺️ Carte de la centrale')
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()],
                   zoom_start=20, tiles='OpenStreetMap', max_zoom=24)
    for _, r in df.iterrows():
        is_anom = r['anomalie'] == 1
        if is_anom and r['classe'] not in sel:
            continue
        popup = (f"<b>Panel {r['panel_id']}</b><br>{r['classe']} "
                 f"({r['confiance']:.0%})<br>{r['lat']}, {r['lon']}")
        folium.CircleMarker(
            location=[r['lat'], r['lon']], radius=7,
            color='#d62728' if is_anom else '#2ca02c',
            fill=True, fill_opacity=0.9,
            popup=folium.Popup(popup, max_width=200)).add_to(m)
    st_folium(m, width=720, height=520)

# --- Table + export ---
with right:
    st.subheader('📋 Anomalies localisées')
    anom_df = df[(df['anomalie'] == 1) & (df['classe'].isin(sel))][
        ['panel_id', 'classe', 'confiance', 'lat', 'lon']]
    st.dataframe(anom_df, use_container_width=True, height=380)
    st.download_button('⬇️ Télécharger le rapport (CSV)',
                       df.to_csv(index=False), 'report.csv', 'text/csv')
    st.bar_chart(df.loc[df['anomalie'] == 1, 'classe'].value_counts())
