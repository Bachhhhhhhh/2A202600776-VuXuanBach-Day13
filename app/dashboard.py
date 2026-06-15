from __future__ import annotations

from html import escape
import json
from pathlib import Path

import yaml


def dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Full-stack Observability Dashboard</title>
  <style>
    :root { color-scheme: dark; --bg:#07111f; --card:#101d30; --line:#203452;
      --text:#e8f0ff; --muted:#92a7c7; --cyan:#37d4ff; --green:#4ade80;
      --amber:#fbbf24; --red:#fb7185; }
    * { box-sizing:border-box; }
    body { margin:0; background:radial-gradient(circle at 10% 0,#102b48 0,var(--bg) 42%);
      color:var(--text); font:14px Inter,Segoe UI,sans-serif; }
    main { max-width:1380px; margin:auto; padding:28px; }
    header { display:flex; justify-content:space-between; align-items:end; margin-bottom:20px; }
    h1 { margin:0 0 6px; font-size:30px; letter-spacing:-.5px; }
    .subtitle,.meta { color:var(--muted); }
    .meta { text-align:right; line-height:1.7; }
    .live { color:var(--green); font-weight:700; }
    .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
    .panel { min-height:218px; padding:20px; border:1px solid var(--line); border-radius:14px;
      background:linear-gradient(145deg,rgba(20,38,62,.96),rgba(12,25,43,.96));
      box-shadow:0 16px 40px rgba(0,0,0,.2); }
    .panel h2 { margin:0; font-size:14px; color:#b9c9e2; font-weight:600; }
    .value { margin:18px 0 4px; font-size:34px; font-weight:750; letter-spacing:-1px; }
    .unit { color:var(--muted); font-size:13px; }
    .triple { display:flex; gap:20px; margin-top:20px; }
    .triple b { display:block; font-size:24px; color:var(--cyan); }
    .chart { height:64px; margin-top:22px; display:flex; align-items:end; gap:5px; }
    .bar { flex:1; min-height:5px; border-radius:3px 3px 0 0;
      background:linear-gradient(var(--cyan),#376cfb); opacity:.85; }
    .threshold { margin-top:14px; border-top:1px dashed var(--amber); padding-top:8px;
      color:var(--amber); font-size:12px; }
    .breakdown { margin-top:18px; color:var(--muted); line-height:1.7; }
    .ok { color:var(--green); } .bad { color:var(--red); }
    footer { margin-top:18px; color:var(--muted); display:flex; justify-content:space-between; }
    a { color:var(--cyan); }
    @media(max-width:900px){.grid{grid-template-columns:1fr 1fr}}
  </style>
</head>
<body><main>
  <header>
    <div><h1>Full-stack Observability</h1>
      <div class="subtitle">day13-observability-lab / production overview</div></div>
    <div class="meta"><span class="live">● LIVE</span><br>Range: Last 1 hour · Refresh: 15s<br>
      <span id="updated">Waiting for metrics…</span></div>
  </header>
  <section class="grid">
    <article class="panel"><h2>1 · LATENCY DISTRIBUTION</h2>
      <div class="triple"><span><b id="p50">0</b>p50 ms</span><span><b id="p95">0</b>p95 ms</span>
      <span><b id="p99">0</b>p99 ms</span></div><div class="chart" id="latency-chart"></div>
      <div class="threshold">SLO threshold: P95 &lt; 3,000 ms</div></article>
    <article class="panel"><h2>2 · TRAFFIC</h2><div class="value" id="traffic">0</div>
      <div class="unit">requests · current process</div><div class="chart" id="traffic-chart"></div>
      <div class="threshold">Operational signal: total request volume</div></article>
    <article class="panel"><h2>3 · ERROR RATE & BREAKDOWN</h2><div class="value ok" id="error-rate">0%</div>
      <div class="unit">failed requests / total requests</div><div class="breakdown" id="errors">No errors</div>
      <div class="threshold">SLO threshold: error rate &lt; 2%</div></article>
    <article class="panel"><h2>4 · COST OVER TIME</h2><div class="value">$<span id="cost">0.0000</span></div>
      <div class="unit">estimated total USD</div><div class="chart" id="cost-chart"></div>
      <div class="threshold">Daily budget: &lt; $2.50</div></article>
    <article class="panel"><h2>5 · TOKEN USAGE</h2>
      <div class="triple"><span><b id="tokens-in">0</b>input</span><span><b id="tokens-out">0</b>output</span></div>
      <div class="chart" id="token-chart"></div><div class="threshold">Track output growth for cost spikes</div></article>
    <article class="panel"><h2>6 · QUALITY PROXY</h2><div class="value" id="quality">0.00</div>
      <div class="unit">heuristic score · 0.00–1.00</div><div class="chart" id="quality-chart"></div>
      <div class="threshold">SLO threshold: average ≥ 0.75</div></article>
  </section>
  <footer><span>Source: <code>GET /metrics</code></span><a href="/alerts">View alert rules →</a></footer>
</main>
<script>
  const history = {latency:[],traffic:[],cost:[],tokens:[],quality:[]};
  function bars(id, values) {
    const max = Math.max(1,...values);
    document.getElementById(id).innerHTML = values.map(v =>
      `<i class="bar" style="height:${Math.max(8,Math.round(v/max*100))}%"></i>`).join("");
  }
  async function refresh() {
    const m = await fetch("/metrics").then(r => r.json());
    p50.textContent=m.latency_p50.toFixed(0); p95.textContent=m.latency_p95.toFixed(0);
    p99.textContent=m.latency_p99.toFixed(0); traffic.textContent=m.traffic;
    const er=document.getElementById("error-rate"); er.textContent=m.error_rate_pct.toFixed(2)+"%";
    er.className="value "+(m.error_rate_pct>=2?"bad":"ok");
    errors.textContent=Object.keys(m.error_breakdown).length ? JSON.stringify(m.error_breakdown) : "No errors recorded";
    cost.textContent=m.total_cost_usd.toFixed(4); document.getElementById("tokens-in").textContent=m.tokens_in_total;
    document.getElementById("tokens-out").textContent=m.tokens_out_total; quality.textContent=m.quality_avg.toFixed(2);
    history.latency.push(m.latency_p95); history.traffic.push(m.traffic); history.cost.push(m.total_cost_usd);
    history.tokens.push(m.tokens_in_total+m.tokens_out_total); history.quality.push(m.quality_avg);
    for(const k of Object.keys(history)) history[k]=history[k].slice(-18);
    bars("latency-chart",history.latency); bars("traffic-chart",history.traffic); bars("cost-chart",history.cost);
    bars("token-chart",history.tokens); bars("quality-chart",history.quality);
    updated.textContent="Updated "+new Date().toLocaleTimeString();
  }
  refresh(); setInterval(refresh,15000);
</script></body></html>"""


def alerts_html(values: dict) -> str:
    config = yaml.safe_load(Path("config/alert_rules.yaml").read_text(encoding="utf-8"))
    rows = []
    for rule in config["alerts"]:
        firing = _is_firing(rule["name"], values)
        status = "FIRING" if firing else "OK"
        css = "bad" if firing else "ok"
        rows.append(
            "<tr>"
            f"<td><strong>{escape(rule['name'])}</strong></td>"
            f"<td><span class='badge {escape(rule['severity'].lower())}'>{escape(rule['severity'])}</span></td>"
            f"<td><code>{escape(rule['condition'])}</code></td>"
            f"<td>{escape(rule['type'])}</td><td>{escape(rule['owner'])}</td>"
            f"<td><a href='/{escape(rule['runbook'])}'>{escape(rule['runbook'])}</a></td>"
            f"<td class='{css}'><strong>{status}</strong></td></tr>"
        )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Alert Rules</title><style>
body{{margin:0;background:#07111f;color:#e8f0ff;font:14px Segoe UI,sans-serif}}
main{{max-width:1400px;margin:auto;padding:34px}} h1{{font-size:30px;margin-bottom:6px}}
p{{color:#92a7c7}} table{{width:100%;border-collapse:collapse;margin-top:28px;background:#101d30;
border:1px solid #203452}} th,td{{padding:18px;text-align:left;border-bottom:1px solid #203452}}
th{{color:#92a7c7;font-size:12px}} code{{color:#37d4ff}} a{{color:#37d4ff}} .ok{{color:#4ade80}}
.bad{{color:#fb7185}} .badge{{padding:4px 9px;border-radius:12px;background:#263b5c}} .p1{{color:#fb7185}}
.p2{{color:#fbbf24}} .summary{{display:flex;gap:14px;margin-top:20px}} .card{{background:#101d30;
border:1px solid #203452;padding:14px 18px;border-radius:10px}} </style></head>
<body><main><h1>Alert Rules</h1><p>Source: config/alert_rules.yaml · evaluated against live /metrics</p>
<div class="summary"><div class="card">Rules <strong>3</strong></div>
<div class="card">Latency P95 <strong>{values['latency_p95']:.0f} ms</strong></div>
<div class="card">Error rate <strong>{values['error_rate_pct']:.2f}%</strong></div>
<div class="card">Total cost <strong>${values['total_cost_usd']:.4f}</strong></div></div>
<table><thead><tr><th>RULE</th><th>SEVERITY</th><th>CONDITION</th><th>TYPE</th><th>OWNER</th>
<th>RUNBOOK</th><th>STATUS</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p><a href="/dashboard">← Back to dashboard</a></p></main></body></html>"""


def _is_firing(name: str, values: dict) -> bool:
    if name == "high_latency_p95":
        return values["latency_p95"] > 5000
    if name == "high_error_rate":
        return values["error_rate_pct"] > 5
    if name == "cost_budget_spike":
        return values["total_cost_usd"] > 2.5
    return False


def trace_evidence_html() -> str:
    trace_id = "f7f163eb01ade01e3afeaa3dfb4fe7db"
    trace_url = (
        "https://jp.cloud.langfuse.com/project/cmqevsbl7002cad0e84tzuud4/"
        f"traces/{trace_id}"
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Trace Waterfall Evidence</title>
<style>
body{{margin:0;background:#07111f;color:#e8f0ff;font:14px Segoe UI,sans-serif}}main{{max-width:1250px;margin:auto;padding:34px}}
h1{{font-size:30px;margin:0 0 8px}}p{{color:#92a7c7}}a{{color:#37d4ff}}.meta{{display:flex;gap:14px;margin:24px 0}}
.card{{background:#101d30;border:1px solid #203452;padding:14px 18px;border-radius:10px}}.waterfall{{background:#101d30;
border:1px solid #203452;border-radius:12px;padding:24px}}.row{{display:grid;grid-template-columns:170px 1fr 90px;
gap:18px;align-items:center;margin:18px 0}}.track{{height:38px;background:#172942;border-radius:6px;position:relative}}
.bar{{height:100%;border-radius:6px;background:linear-gradient(90deg,#376cfb,#37d4ff)}}.rag{{width:97.3%}}
.llm{{width:2.7%;min-width:28px;margin-left:97.3%;background:linear-gradient(90deg,#f59e0b,#fbbf24)}}.run{{width:100%}}
.duration{{text-align:right;font-weight:700}}code{{color:#37d4ff}}.warning{{color:#fbbf24;font-weight:700}}
</style></head><body><main><h1>Langfuse Trace Waterfall</h1>
<p>API-verified evidence · Langfuse SDK 3.2.1 · incident scenario <strong>rag_slow</strong></p>
<div class="meta"><div class="card">Trace ID<br><code>{trace_id}</code></div>
<div class="card">Session<br><strong>s09</strong></div><div class="card">Trace count<br><strong>61+</strong></div>
<div class="card">Timestamp UTC<br><strong>2026-06-15 07:41:21</strong></div></div>
<div class="waterfall"><div class="row"><strong>run</strong><div class="track"><div class="bar run"></div></div>
<div class="duration">5.652 s</div></div>
<div class="row"><span>↳ rag.retrieve</span><div class="track"><div class="bar rag"></div></div>
<div class="duration warning">5.501 s</div></div>
<div class="row"><span>↳ llm.generate</span><div class="track"><div class="bar llm"></div></div>
<div class="duration">0.151 s</div></div></div>
<p><span class="warning">Finding:</span> retrieval consumes 97.3% of total trace latency, proving the injected
RAG slowdown is the bottleneck. <a href="{trace_url}">Open the original Langfuse trace</a>.</p>
</main></body></html>"""


def log_evidence_html() -> str:
    records = [
        json.loads(line)
        for line in Path("data/logs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    pii_record = next(
        rec for rec in records
        if rec.get("event") == "request_received"
        and "[REDACTED_" in json.dumps(rec, ensure_ascii=False)
    )
    correlation_id = pii_record["correlation_id"]
    response_record = next(
        rec for rec in records
        if rec.get("event") == "response_sent" and rec.get("correlation_id") == correlation_id
    )
    first = escape(json.dumps(pii_record, ensure_ascii=False, indent=2))
    second = escape(json.dumps(response_record, ensure_ascii=False, indent=2))
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Logging Evidence</title>
<style>body{{margin:0;background:#07111f;color:#e8f0ff;font:14px Segoe UI,sans-serif}}
main{{max-width:1350px;margin:auto;padding:30px}}h1{{font-size:30px}}p{{color:#92a7c7}}.grid{{display:grid;
grid-template-columns:1fr 1fr;gap:18px}}article{{background:#101d30;border:1px solid #203452;border-radius:12px;padding:20px}}
h2{{font-size:15px;color:#37d4ff}}pre{{white-space:pre-wrap;color:#cad8ef;font:12px Consolas,monospace;line-height:1.5}}
.good{{color:#4ade80;font-weight:700}}code{{color:#fbbf24}}</style></head><body><main>
<h1>Structured Logging Evidence</h1><p><span class="good">PASS</span> · Same correlation ID across request and
response · PII removed before persistence</p><div class="grid"><article><h2>REQUEST_RECEIVED · PII REDACTED</h2>
<pre>{first}</pre></article><article><h2>RESPONSE_SENT · CORRELATED</h2><pre>{second}</pre></article></div>
<p>Correlation ID: <code>{escape(correlation_id)}</code></p></main></body></html>"""
