"""Genere un dashboard HTML autonome et soigne a partir de reports/report.csv.

    py dashboard/build.py
    -> reports/dashboard.html  (a ouvrir dans un navigateur)
"""
import json
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / 'reports' / 'report.csv')

records = df[['panel_id', 'lat', 'lon', 'classe', 'confiance', 'anomalie']].to_dict('records')
total = len(df)
n_anom = int(df['anomalie'].sum())
rate = round(100 * n_anom / total, 1)
type_counts = dict(Counter(df.loc[df['anomalie'] == 1, 'classe']).most_common())
top_type = next(iter(type_counts), '—')
center = [float(df['lat'].mean()), float(df['lon'].mean())]

TEMPLATE = r'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SolarScan — Dashboard d'inspection</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root{
    --bg:#0b1220; --panel:#131c2e; --panel2:#1b2740; --line:#243352;
    --txt:#e7ecf5; --muted:#93a2bd; --accent:#f59e0b; --blue:#3b82f6;
    --green:#22c55e; --red:#ef4444;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--txt);}
  header{display:flex;align-items:center;gap:14px;padding:18px 28px;
    background:linear-gradient(90deg,#0f3c82,#1b2740);border-bottom:1px solid var(--line)}
  header .logo{font-size:26px}
  header h1{font-size:20px;font-weight:600}
  header p{font-size:13px;color:var(--muted)}
  main{padding:24px 28px;max-width:1320px;margin:0 auto}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:22px}
  .kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px}
  .kpi .label{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
  .kpi .value{font-size:30px;font-weight:700;margin-top:6px}
  .kpi .value.warn{color:var(--accent)}
  .kpi .value.red{color:var(--red)}
  .grid{display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:22px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px}
  .card h2{font-size:15px;font-weight:600;margin-bottom:14px;display:flex;align-items:center;gap:8px}
  #map{height:460px;border-radius:10px;overflow:hidden}
  .legend{display:flex;gap:18px;margin-top:14px;font-size:13px;color:var(--muted)}
  .dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px;vertical-align:middle}
  .table-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
  input#search{background:var(--panel2);border:1px solid var(--line);color:var(--txt);
    padding:8px 12px;border-radius:8px;font-size:13px;width:220px;outline:none}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line)}
  th{color:var(--muted);font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.4px}
  tbody tr:hover{background:var(--panel2)}
  .badge{padding:3px 9px;border-radius:20px;font-size:12px;background:rgba(239,68,68,.15);color:#fca5a5}
  .conf{color:var(--muted)}
  footer{text-align:center;color:var(--muted);font-size:12px;padding:20px}
  @media(max-width:900px){.kpis{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<header>
  <span class="logo">☀️</span>
  <div><h1>SolarScan — Dashboard d'inspection</h1>
  <p>Détection de défauts sur panneaux solaires par imagerie thermique de drone</p></div>
</header>
<main>
  <section class="kpis">
    <div class="kpi"><div class="label">Panneaux inspectés</div><div class="value">__TOTAL__</div></div>
    <div class="kpi"><div class="label">Anomalies détectées</div><div class="value red">__ANOM__</div></div>
    <div class="kpi"><div class="label">Taux d'anomalie</div><div class="value warn">__RATE__ %</div></div>
    <div class="kpi"><div class="label">Défaut dominant</div><div class="value" style="font-size:20px;margin-top:12px">__TOP__</div></div>
  </section>
  <section class="grid">
    <div class="card">
      <h2>🗺️ Carte de la centrale</h2>
      <div id="map"></div>
      <div class="legend">
        <span><span class="dot" style="background:#22c55e"></span>Sain</span>
        <span><span class="dot" style="background:#ef4444"></span>Anomalie</span>
        <span>📍 Benguerir (GPS simulé)</span>
      </div>
    </div>
    <div class="card">
      <h2>📊 Répartition des défauts</h2>
      <canvas id="chart" height="240"></canvas>
    </div>
  </section>
  <section class="card">
    <div class="table-head">
      <h2>📋 Anomalies localisées</h2>
      <input id="search" placeholder="Rechercher un type / id…">
    </div>
    <table>
      <thead><tr><th>Panneau</th><th>Type de défaut</th><th>Confiance</th><th>Latitude</th><th>Longitude</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </section>
</main>
<footer>SolarScan · Souleymane Diallo · modèle ResNet-18 (macro-F1 0.66)</footer>
<script>
  const DATA = __DATA__;
  const TYPES = __TYPES__;
  const CENTER = __CENTER__;

  const map = L.map('map').setView(CENTER, 20);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {maxZoom:24, attribution:'© OpenStreetMap'}).addTo(map);
  DATA.forEach(p => {
    const anom = p.anomalie === 1;
    const c = anom ? '#ef4444' : '#22c55e';
    L.circleMarker([p.lat, p.lon], {radius:7, color:c, fillColor:c, fillOpacity:.9, weight:1})
      .bindPopup('<b>Panneau '+p.panel_id+'</b><br>'+p.classe+' — '+Math.round(p.confiance*100)+'%<br>'+p.lat+', '+p.lon)
      .addTo(map);
  });

  const palette = ['#f59e0b','#3b82f6','#ef4444','#22c55e','#a855f7','#14b8a6','#eab308','#f472b6','#60a5fa','#fb923c'];
  new Chart(document.getElementById('chart'), {
    type:'doughnut',
    data:{labels:Object.keys(TYPES), datasets:[{data:Object.values(TYPES), backgroundColor:palette, borderColor:'#131c2e', borderWidth:2}]},
    options:{plugins:{legend:{position:'bottom', labels:{color:'#93a2bd', font:{size:11}, padding:10}}}}
  });

  const anomalies = DATA.filter(p=>p.anomalie===1).sort((a,b)=>b.confiance-a.confiance);
  const tbody = document.getElementById('tbody');
  function render(rows){
    tbody.innerHTML = rows.map(p =>
      '<tr><td>#'+p.panel_id+'</td><td><span class="badge">'+p.classe+'</span></td>'+
      '<td class="conf">'+Math.round(p.confiance*100)+'%</td><td class="conf">'+p.lat+'</td><td class="conf">'+p.lon+'</td></tr>'
    ).join('');
  }
  render(anomalies);
  document.getElementById('search').addEventListener('input', e=>{
    const q = e.target.value.toLowerCase();
    render(anomalies.filter(p => p.classe.toLowerCase().includes(q) || String(p.panel_id).includes(q)));
  });
</script>
</body>
</html>'''

html = (TEMPLATE
        .replace('__DATA__', json.dumps(records))
        .replace('__TYPES__', json.dumps(type_counts, ensure_ascii=False))
        .replace('__CENTER__', json.dumps(center))
        .replace('__TOTAL__', str(total))
        .replace('__ANOM__', str(n_anom))
        .replace('__RATE__', str(rate))
        .replace('__TOP__', top_type))

out = ROOT / 'reports' / 'dashboard.html'
out.write_text(html, encoding='utf-8')
print('Dashboard genere :', out)
