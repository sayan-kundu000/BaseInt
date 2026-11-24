"""Lightweight BaseInt Portal and Documentation Server running on port 3000.

Serves the 37 architectural documentation topics, REST endpoints, and security manifests.
Usage:
    python server.py
"""

import http.server
import socketserver
import json
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from app.config import settings
from app.agent.graph import execute_agent_pipeline
from app.database.schema import inspect_database_schema
from app.database.connection import get_engine

PORT = settings.docs_server_port or 3000
DOCS_DIR = Path(__file__).resolve().parent / "docs" / "topics"


class BaseIntHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving the BaseInt Localhost 3000 ecosystem."""

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = self._render_portal_home()
            self.wfile.write(html.encode("utf-8"))

        elif path in ("/dashboard", "/dashboard/"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = self._render_dashboard_page()
            self.wfile.write(html.encode("utf-8"))

        elif path == "/docs" or path == "/docs/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = self._render_docs_index()
            self.wfile.write(html.encode("utf-8"))

        elif path.startswith("/docs/topic-"):
            topic_id = path.replace("/docs/topic-", "").replace(".html", "").strip("/")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = self._render_topic_page(topic_id)
            self.wfile.write(html.encode("utf-8"))

        elif path == "/BaseInt_Documentation.pdf":
            pdf_file = Path(__file__).resolve().parent / "BaseInt_Documentation.pdf"
            if pdf_file.exists():
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Disposition", "inline; filename=BaseInt_Documentation.pdf")
                self.end_headers()
                self.wfile.write(pdf_file.read_bytes())
            else:
                self.send_response(404)
                self.end_headers()

        elif path == "/api/v1/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            resp = {
                "system": "BaseInt Analytics Agent",
                "status": "HEALTHY",
                "port": PORT,
                "ast_guardrails": "ENFORCED",
                "max_retries": settings.max_retries,
                "portal_url": f"http://localhost:{PORT}"
            }
            self.wfile.write(json.dumps(resp, indent=2).encode("utf-8"))

        elif path == "/security":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = self._render_security_page()
            self.wfile.write(html.encode("utf-8"))

        elif path == "/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            eng = get_engine()
            schema = inspect_database_schema(eng)
            resp = {
                "database": str(eng.url),
                "tables_monitored": list(schema.keys()),
                "total_columns": sum(len(v["columns"]) for v in schema.values()),
                "security_engine": "sqlparse AST + NeMo Rails",
                "links": {
                    "docs": f"http://localhost:{PORT}/docs",
                    "health": f"http://localhost:{PORT}/api/v1/health",
                    "streamlit": f"http://localhost:{settings.streamlit_server_port}"
                }
            }
            self.wfile.write(json.dumps(resp, indent=2).encode("utf-8"))

        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/v1/query":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                query = data.get("query", "")
                sim = data.get("simulate_error", False)
                state = execute_agent_pipeline(query, simulate_initial_error=sim)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                resp = {
                    "user_query": state.get("user_query"),
                    "generated_sql": state.get("generated_sql"),
                    "ast_passed": state.get("ast_passed"),
                    "retry_count": state.get("retry_count"),
                    "row_count": len(state.get("db_result") or []),
                    "db_result": state.get("db_result"),
                    "error_message": state.get("error_message"),
                    "telemetry_logs": state.get("telemetry_logs")
                }
                self.wfile.write(json.dumps(resp, indent=2).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def _render_portal_home(self) -> str:
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>BaseInt Hub | localhost:{PORT}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 40px; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
        .container {{ max-width: 960px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        h1 {{ color: #1e3a8a; margin-top: 0; }}
        .badge {{ display: inline-block; padding: 4px 10px; background: #dbeafe; color: #1d4ed8; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-top: 30px; }}
        .card {{ background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-decoration: none; color: inherit; transition: transform 0.15s ease; }}
        .card:hover {{ transform: translateY(-3px); background: #e2e8f0; }}
        .card h3 {{ margin-top: 0; color: #0f172a; }}
        code {{ background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
        footer {{ margin-top: 40px; text-align: center; color: #64748b; font-size: 0.9rem; border-top: 1px solid #e2e8f0; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <span class="badge">BaseInt Operational Portal • Port {PORT}</span>
        <h1>BaseInt SQL & Analytics Agent</h1>
        <p>Enterprise text-to-SQL system engineered with <strong>LangGraph reflection loops</strong>, <strong>SQLAlchemy metadata introspection</strong>, <strong>AST-based read-only security filters</strong>, and <strong>NeMo Guardrails wrappers</strong>.</p>
        
        <div class="grid">
            <a href="/dashboard" class="card" style="border: 2px solid #2563eb; background: #eff6ff;">
                <h3 style="color: #1d4ed8;">🚀 Interactive Query Dashboard</h3>
                <p>Run natural language queries, test self-correction reflection loops, AST guardrails, and render dynamic Plotly analytics charts.</p>
            </a>
            <a href="/docs" class="card">
                <h3>📚 37-Page Technical Manual</h3>
                <p>Complete documentation spanning 37 topics and 37 comprehensive pages covering architecture, AST safety, self-correction, and enterprise use cases.</p>
            </a>
            <a href="http://localhost:{settings.streamlit_server_port}" target="_blank" class="card">
                <h3>📊 Streamlit Analytics Dashboard</h3>
                <p>Standalone Streamlit UI on port {settings.streamlit_server_port} with collapsible telemetry feeds and Plotly canvas.</p>
            </a>
            <a href="/security" class="card">
                <h3>🛡️ Security & Guardrails Matrix</h3>
                <p>Review AST parse policies, Colang rules, tautology detection, and SQL injection blocking defenses.</p>
            </a>
            <a href="/telemetry" class="card">
                <h3>⚡ Telemetry & Diagnostics</h3>
                <p>Real-time database reflection telemetry, query execution latency metrics, and self-correction counter statuses.</p>
            </a>
        </div>

        <footer>
            BaseInt Core Architecture • Maintained by sayan-kundu000 • Running on <a href="http://localhost:{PORT}">localhost:{PORT}</a>
        </footer>
    </div>
</body>
</html>"""

    def _render_dashboard_page(self) -> str:
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>BaseInt Interactive Dashboard | localhost:{PORT}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 25px; background: #f8fafc; color: #1e293b; line-height: 1.5; }}
        .container {{ max-width: 1100px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 35px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 15px; margin-bottom: 20px; }}
        .header h1 {{ color: #1e3a8a; margin: 0; font-size: 1.8rem; }}
        .nav-links a {{ margin-left: 15px; color: #2563eb; text-decoration: none; font-weight: 500; font-size: 0.95rem; }}
        .presets {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }}
        .preset-btn {{ background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 12px; font-size: 0.85rem; cursor: pointer; transition: all 0.15s ease; }}
        .preset-btn:hover {{ background: #e2e8f0; border-color: #94a3b8; }}
        textarea {{ width: 100%; box-sizing: border-box; height: 80px; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 0.95rem; font-family: inherit; margin-bottom: 12px; }}
        .controls {{ display: flex; align-items: center; gap: 20px; margin-bottom: 25px; }}
        .run-btn {{ background: #2563eb; color: #fff; border: none; border-radius: 8px; padding: 10px 24px; font-size: 0.95rem; font-weight: 600; cursor: pointer; }}
        .run-btn:hover {{ background: #1d4ed8; }}
        .badges {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }}
        .badge-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center; }}
        .badge-card .title {{ font-size: 0.8rem; color: #64748b; text-transform: uppercase; }}
        .badge-card .val {{ font-size: 1.2rem; font-weight: 700; color: #0f172a; margin-top: 4px; }}
        .alert {{ padding: 12px 16px; border-radius: 8px; margin-bottom: 18px; font-weight: 500; display: none; }}
        .alert.error {{ background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}
        .alert.success {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
        .section-title {{ font-size: 1.15rem; color: #0f172a; margin: 25px 0 10px 0; font-weight: 600; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }}
        pre {{ background: #0f172a; color: #f8fafc; padding: 14px; border-radius: 8px; overflow-x: auto; font-size: 0.9rem; font-family: Consolas, monospace; margin: 0; }}
        details {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 15px; padding: 10px 14px; }}
        details summary {{ font-weight: 600; cursor: pointer; color: #334155; }}
        .log-line {{ font-family: Consolas, monospace; font-size: 0.85rem; padding: 4px 0; border-bottom: 1px solid #f1f5f9; }}
        .log-error {{ color: #dc2626; }}
        .log-reflect {{ color: #d97706; }}
        .log-success {{ color: #16a34a; }}
        .log-info {{ color: #64748b; }}
        .table-wrap {{ max-height: 280px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
        th, td {{ padding: 10px 12px; border: 1px solid #e2e8f0; text-align: left; }}
        th {{ background: #f1f5f9; position: sticky; top: 0; }}
        #chart {{ width: 100%; height: 420px; margin-top: 15px; }}
        footer {{ margin-top: 30px; text-align: center; color: #64748b; font-size: 0.85rem; border-top: 1px solid #e2e8f0; padding-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>BaseInt Analytics Dashboard</h1>
                <small style="color: #64748b;">LangGraph Reflection Loop • AST Safety Filter • Plotly Heuristic Canvas</small>
            </div>
            <div class="nav-links">
                <a href="/">← Hub</a>
                <a href="/docs">37-Topic Docs</a>
                <a href="/security">Security Matrix</a>
                <a href="/telemetry">Telemetry API</a>
                <a href="http://localhost:8501" target="_blank">Streamlit (8501) ↗</a>
            </div>
        </div>

        <div class="presets">
            <span style="font-weight: 600; font-size: 0.85rem; align-self: center;">⚡ Quick Presets:</span>
            <button class="preset-btn" onclick="setPreset('Show orders sorted by date', true)">Orders by Date (Test 1 Recovery)</button>
            <button class="preset-btn" onclick="setPreset('DROP TABLE orders; --', false)">DROP TABLE orders; -- (Test 2 AST Block)</button>
            <button class="preset-btn" onclick="setPreset('Show top 5 products by price', false)">Top 5 Products</button>
            <button class="preset-btn" onclick="setPreset('What is total revenue by customer region?', false)">Revenue by Region</button>
            <button class="preset-btn" onclick="setPreset('Show product count and average price by category', false)">Product Categories</button>
        </div>

        <textarea id="queryInput" placeholder="Enter natural language database question...">Show orders sorted by date</textarea>

        <div class="controls">
            <button class="run-btn" id="runBtn" onclick="runQuery()">🚀 Run Agentic Query</button>
            <label style="font-size: 0.9rem; cursor: pointer;">
                <input type="checkbox" id="simError"> Simulate initial column error (Test Case 1)
            </label>
            <span id="loading" style="display: none; color: #2563eb; font-weight: 500;">⏳ Executing LangGraph pipeline...</span>
        </div>

        <div id="alertBox" class="alert"></div>

        <div class="badges">
            <div class="badge-card">
                <div class="title">Execution Status</div>
                <div class="val" id="badgeStatus">—</div>
            </div>
            <div class="badge-card">
                <div class="title">Retries / Max 3</div>
                <div class="val" id="badgeRetries">—</div>
            </div>
            <div class="badge-card">
                <div class="title">AST Safety Filter</div>
                <div class="val" id="badgeAST">—</div>
            </div>
            <div class="badge-card">
                <div class="title">Rows Retrieved</div>
                <div class="val" id="badgeRows">—</div>
            </div>
        </div>

        <details open>
            <summary>📝 Generated SQL Statement</summary>
            <pre id="sqlBlock" style="margin-top: 8px;">-- Generated SQL statement will appear here</pre>
        </details>

        <details open>
            <summary>🔍 Telemetry & Self-Correction Logs</summary>
            <div id="logFeed" style="margin-top: 8px;">
                <div class="log-line log-info">Ready to process natural language queries.</div>
            </div>
        </details>

        <div class="section-title">📊 Tabular Query Results</div>
        <div class="table-wrap" id="tableContainer">
            <div style="padding: 20px; text-align: center; color: #64748b;">No query executed yet.</div>
        </div>

        <div class="section-title">📈 Dynamic Plotly Visualization Canvas</div>
        <div id="chartContainer">
            <div id="chart"></div>
        </div>

        <footer>
            BaseInt Analytics Engine • Port {PORT} &bull; Full Reflection Loops & AST Guardrails Active &bull; <a href="http://localhost:{PORT}">localhost:{PORT}</a>
        </footer>
    </div>

    <script>
        function setPreset(txt, sim) {{
            document.getElementById('queryInput').value = txt;
            document.getElementById('simError').checked = sim;
            runQuery();
        }}

        async function runQuery() {{
            const query = document.getElementById('queryInput').value.trim();
            const sim = document.getElementById('simError').checked;
            const loading = document.getElementById('loading');
            const alertBox = document.getElementById('alertBox');
            
            if (!query) return;

            loading.style.display = 'inline';
            alertBox.style.display = 'none';

            try {{
                const resp = await fetch('/api/v1/query', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ query: query, simulate_error: sim }})
                }});

                const data = await resp.json();
                loading.style.display = 'none';

                // Badges
                const astPassed = data.ast_passed;
                const errMsg = data.error_message;
                const rows = data.db_result || [];
                const retryCount = data.retry_count || 0;

                const statusEl = document.getElementById('badgeStatus');
                if (astPassed && !errMsg) {{
                    statusEl.innerText = 'Completed';
                    statusEl.style.color = '#16a34a';
                }} else if (!astPassed) {{
                    statusEl.innerText = 'Blocked';
                    statusEl.style.color = '#dc2626';
                }} else {{
                    statusEl.innerText = 'Retry Limit';
                    statusEl.style.color = '#d97706';
                }}

                document.getElementById('badgeRetries').innerText = retryCount + ' / 3';
                const astEl = document.getElementById('badgeAST');
                astEl.innerText = astPassed ? 'SAFE (SELECT)' : 'VIOLATION BLOCKED';
                astEl.style.color = astPassed ? '#16a34a' : '#dc2626';
                document.getElementById('badgeRows').innerText = rows.length;

                // Alerts
                if (errMsg) {{
                    alertBox.className = 'alert error';
                    alertBox.innerHTML = '🛡️ <strong>Notice:</strong> ' + errMsg;
                    alertBox.style.display = 'block';
                }} else {{
                    alertBox.className = 'alert success';
                    alertBox.innerHTML = '✅ Query validated by AST Safety Filter and executed successfully.';
                    alertBox.style.display = 'block';
                }}

                // SQL
                document.getElementById('sqlBlock').innerText = data.generated_sql || '-- Execution blocked prior to SQL generation.';

                // Logs
                const logFeed = document.getElementById('logFeed');
                logFeed.innerHTML = '';
                (data.telemetry_logs || []).forEach(l => {{
                    const d = document.createElement('div');
                    d.className = 'log-line';
                    const low = l.toLowerCase();
                    if (low.includes('error') || low.includes('blocked') || low.includes('alert')) d.classList.add('log-error');
                    else if (low.includes('reflect') || low.includes('correct')) d.classList.add('log-reflect');
                    else if (low.includes('success')) d.classList.add('log-success');
                    else d.classList.add('log-info');
                    d.innerText = l;
                    logFeed.appendChild(d);
                }});

                // Table
                const tableCont = document.getElementById('tableContainer');
                if (rows.length > 0) {{
                    const cols = Object.keys(rows[0]);
                    let html = '<table><thead><tr>' + cols.map(c => '<th>' + c + '</th>').join('') + '</tr></thead><tbody>';
                    rows.forEach(r => {{
                        html += '<tr>' + cols.map(c => '<td>' + (r[c] !== null ? r[c] : '<em>null</em>') + '</td>').join('') + '</tr>';
                    }});
                    html += '</tbody></table>';
                    tableCont.innerHTML = html;
                }} else {{
                    tableCont.innerHTML = '<div style="padding: 20px; text-align: center; color: #64748b;">No rows returned.</div>';
                }}

                // Plotly Chart
                renderChart(rows);

            }} catch (err) {{
                loading.style.display = 'none';
                alertBox.className = 'alert error';
                alertBox.innerText = 'Network/Execution error: ' + err.message;
                alertBox.style.display = 'block';
            }}
        }}

        function renderChart(rows) {{
            const chartDiv = document.getElementById('chart');
            if (!rows || rows.length === 0) {{
                Plotly.purge(chartDiv);
                chartDiv.innerHTML = '<div style="padding: 40px; text-align: center; color: #94a3b8;">No numeric data available for visualization.</div>';
                return;
            }}

            const cols = Object.keys(rows[0]);
            const numCols = cols.filter(c => c.toLowerCase() !== 'id' && typeof rows[0][c] === 'number');
            const nonNumCols = cols.filter(c => c.toLowerCase() !== 'id' && typeof rows[0][c] !== 'number');

            if (numCols.length === 0) {{
                Plotly.purge(chartDiv);
                chartDiv.innerHTML = '<div style="padding: 40px; text-align: center; color: #94a3b8;">Non-numeric data; standard tabular display active.</div>';
                return;
            }}

            const valCol = numCols[0];
            const dateCol = nonNumCols.find(c => /date|time|day|month|year/i.test(c));

            if (dateCol) {{
                // Time-Series Line Chart
                const trace = {{
                    x: rows.map(r => r[dateCol]),
                    y: rows.map(r => r[valCol]),
                    type: 'scatter',
                    mode: 'lines+markers',
                    marker: {{ color: '#2563eb', size: 8 }},
                    line: {{ color: '#2563eb', width: 3 }},
                    name: valCol
                }};
                Plotly.newPlot(chartDiv, [trace], {{
                    title: 'Trend Analysis: ' + valCol.toUpperCase() + ' over ' + dateCol.toUpperCase(),
                    margin: {{ t: 40, b: 60, l: 50, r: 20 }},
                    xaxis: {{ tickangle: -45 }}
                }}, {{ responsive: true }});
            }} else if (nonNumCols.length > 0) {{
                const catCol = nonNumCols[0];
                if (rows.length <= 7) {{
                    // Donut Chart
                    const trace = {{
                        labels: rows.map(r => r[catCol]),
                        values: rows.map(r => r[valCol]),
                        type: 'pie',
                        hole: 0.4
                    }};
                    Plotly.newPlot(chartDiv, [trace], {{
                        title: 'Distribution across ' + catCol.toUpperCase(),
                        margin: {{ t: 40, b: 20, l: 20, r: 20 }}
                    }}, {{ responsive: true }});
                }} else {{
                    // Bar Chart
                    const trace = {{
                        x: rows.map(r => r[catCol]),
                        y: rows.map(r => r[valCol]),
                        type: 'bar',
                        marker: {{ color: '#3b82f6' }}
                    }};
                    Plotly.newPlot(chartDiv, [trace], {{
                        title: valCol.toUpperCase() + ' by ' + catCol.toUpperCase(),
                        margin: {{ t: 40, b: 60, l: 50, r: 20 }},
                        xaxis: {{ tickangle: -45 }}
                    }}, {{ responsive: true }});
                }}
            }} else {{
                // Simple Metric Bar
                const trace = {{
                    y: rows.map(r => r[valCol]),
                    type: 'bar',
                    marker: {{ color: '#6366f1' }}
                }};
                Plotly.newPlot(chartDiv, [trace], {{
                    title: valCol.toUpperCase() + ' Metric Distribution',
                    margin: {{ t: 40, b: 30, l: 50, r: 20 }}
                }}, {{ responsive: true }});
            }}
        }}

        // Run default query on load
        window.addEventListener('DOMContentLoaded', () => {{
            runQuery();
        }});
    </script>
</body>
</html>"""

    def _render_docs_index(self) -> str:
        files = sorted(list(DOCS_DIR.glob("topic_*.md")), key=lambda p: int(p.stem.split("_")[1]) if p.stem.split("_")[1].isdigit() else 999)
        items_html = ""
        for f in files:
            t_id = f.stem.replace("topic_", "")
            # Read first line for title
            first_line = f.read_text(encoding="utf-8").split("\n")[0].replace("#", "").strip()
            items_html += f'<li><a href="/docs/topic-{t_id}"><strong>Topic {t_id}:</strong> {first_line}</a></li>\n'

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>BaseInt Documentation Index | localhost:{PORT}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 40px; background: #f8fafc; color: #1e293b; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        h1 {{ color: #1e3a8a; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ padding: 10px 14px; border-bottom: 1px solid #e2e8f0; }}
        li:hover {{ background: #f1f5f9; }}
        a {{ text-decoration: none; color: #2563eb; }}
        a:hover {{ text-decoration: underline; }}
        .back-link {{ display: inline-block; margin-bottom: 20px; color: #64748b; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to localhost:{PORT} Hub</a>
        <h1>BaseInt: 37 Technical Topics Documentation</h1>
        <p>Comprehensive 37-page engineering reference covering tech stack, reflection loops, AST guardrails, testing, and production deployment.</p>
        <ul>{items_html}</ul>
    </div>
</body>
</html>"""

    def _render_topic_page(self, topic_id: str) -> str:
        filepath = DOCS_DIR / f"topic_{topic_id}.md"
        if not filepath.exists():
            return f"<h1>Topic {topic_id} Not Found</h1><p><a href='/docs'>Back to Index</a></p>"

        content = filepath.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        title = paragraphs[0].replace("#", "").strip() if paragraphs else f"Topic {topic_id}"
        body_p = paragraphs[1:]

        p_html = "".join(f"<p>{p}</p>" for p in body_p)
        prev_link = f"<a href='/docs/topic-{int(topic_id)-1}'>← Previous Topic</a>" if int(topic_id) > 1 else ""
        next_link = f"<a href='/docs/topic-{int(topic_id)+1}'>Next Topic →</a>" if int(topic_id) < 37 else ""

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title} | BaseInt localhost:{PORT}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 40px; background: #f8fafc; color: #1e293b; line-height: 1.7; }}
        .container {{ max-width: 860px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 45px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        h1 {{ color: #1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; font-size: 1.8rem; }}
        p {{ margin-bottom: 1.2rem; text-align: justify; font-size: 1.02rem; }}
        .nav-bar {{ display: flex; justify-content: space-between; margin-bottom: 25px; color: #64748b; font-size: 0.95rem; }}
        .nav-bar a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
        footer {{ margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 20px; font-size: 0.9rem; color: #64748b; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-bar">
            <a href="/docs">☰ All 37 Topics</a>
            <div>{prev_link} &nbsp;&nbsp;|&nbsp;&nbsp; {next_link}</div>
        </div>
        <h1>{title}</h1>
        {p_html}
        <footer>
            Topic {topic_id} of 37 • BaseInt Documentation • <a href="http://localhost:{PORT}">localhost:{PORT}</a>
        </footer>
    </div>
</body>
</html>"""

    def _render_security_page(self) -> str:
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>BaseInt Security Architecture | localhost:{PORT}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 40px; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #fff; border-radius: 12px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        h1 {{ color: #1e3a8a; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
        th, td {{ padding: 12px; border: 1px solid #e2e8f0; text-align: left; }}
        th {{ background: #f1f5f9; color: #0f172a; }}
        .safe {{ color: #15803d; font-weight: bold; }}
        .blocked {{ color: #b91c1c; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/">← Back to Portal</a>
        <h1>BaseInt Multi-Layered Security Architecture</h1>
        <p>BaseInt deploys defense-in-depth protection pairing pre-execution AST parsing with input-stage NeMo Guardrail wrappers.</p>
        <table>
            <tr><th>Threat Category</th><th>Defensive Mechanism</th><th>Target Attack Patterns</th><th>Enforcement Action</th></tr>
            <tr><td>Destructive SQL (DDL)</td><td>sqlparse & sqlglot AST</td><td>DROP TABLE, ALTER, TRUNCATE, CREATE</td><td class="blocked">Hard Block (Pre-Execution)</td></tr>
            <tr><td>Data Modification (DML)</td><td>AST Parser Visitor</td><td>INSERT, UPDATE, DELETE, MERGE</td><td class="blocked">Hard Block (Pre-Execution)</td></tr>
            <tr><td>Logical Tautologies</td><td>NeMo Regex Scanner</td><td>' OR 1=1, ' OR 'a'='a', OR TRUE</td><td class="blocked">Input Rail Rejection</td></tr>
            <tr><td>SQL Comment Injection</td><td>NeMo Comment Filter</td><td>--, /* ... */, # expansions</td><td class="blocked">Input Rail Rejection</td></tr>
            <tr><td>Script & XSS Tags</td><td>NeMo Markup Rail</td><td>&lt;script&gt;, javascript:, &lt;iframe&gt;</td><td class="blocked">Input Rail Rejection</td></tr>
            <tr><td>Read-Only Analytical</td><td>Verified SELECT Engine</td><td>SELECT ... FROM ... GROUP BY ...</td><td class="safe">Permitted with Telemetry</td></tr>
        </table>
    </div>
</body>
</html>"""


def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    server_address = ("0.0.0.0", PORT)
    with socketserver.TCPServer(server_address, BaseIntHTTPHandler) as httpd:
        print(f"BaseInt Portal and Documentation Server running at http://localhost:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    start_server()

