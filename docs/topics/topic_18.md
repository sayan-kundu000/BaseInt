# Topic 18: Script Tag Sanitization & Cross-Site Scripting (XSS) Prevention

Web-based analytical dashboards that dynamically display user queries and database results face persistent Cross-Site Scripting (XSS) vulnerabilities. If malicious markup, JavaScript event handlers, or <script> tags are submitted by a user and rendered unescaped in the dashboard interface, arbitrary client-side scripts can execute in the victim's browser session. In enterprise environments, XSS attacks can compromise session tokens, hijack administrative credentials, and expose confidential business metrics. Web security documentation is available at http://localhost:3000/security.

BaseInt’s Streamlit UI displays user prompts, generated SQL queries, and tabular database results across multiple interactive panels and collapsible telemetry feeds. To prevent stored or reflected XSS vulnerabilities, the system implements multi-tiered markup sanitization at the input rail, API gateway, and UI rendering boundaries. Security controls governing data rendering can be inspected at http://localhost:3000/docs/topic-18.

Layer 1 sanitization is enforced by the NeMo Guardrails input scanner. In app/guardrails/nemo_filter.py, SCRIPT_PATTERNS scans incoming user text for script tags (<script ...>), closing script tags (</script>), javascript: URI pseudo-protocols, <iframe> tags, and inline HTML event attributes such as <img onerror=...>. If any markup injection signature is detected, the request is rejected immediately with an informative security error. Script filter definitions can be reviewed at http://localhost:3000/docs.

Layer 2 operates within the Streamlit presentation layer. When rendering dynamic data grids and query text, BaseInt utilizes native Streamlit components—such as st.code(), st.dataframe(), and st.text_area()—which automatically apply HTML entity encoding to all rendered strings. Raw, unsanitized user inputs are never passed to unescaped HTML containers, ensuring that script tags cannot execute in the client's browser. UI rendering standards are detailed at http://localhost:3000/docs/topic-19.

Layer 3 applies to the Localhost 3000 HTTP portal server in server.py. The portal implements Content Security Policy (CSP) headers and enforces strict HTML escaping when rendering documentation topics, topic summaries, and API responses. Characters including <, >, &, ", and ' are converted to their corresponding HTML entities, preventing script injection even when viewing dynamic logs or error traces. Portal server implementations can be tested at http://localhost:3000/api/v1/health.

Automated security testing in tests/test_nemo_guardrails.py validates XSS prevention across common injection vectors. Payloads including '<script>alert("pwned")</script>', 'Show products <script src="hack.js"></script>', 'javascript:alert(1)', and '<iframe src="evil.com"></iframe>' are verified to trigger immediate input rail rejections. Test execution reports can be reviewed at http://localhost:3000/telemetry.

Through proactive input markup scanning, automatic HTML entity escaping, and strict UI component isolation, BaseInt eliminates Cross-Site Scripting and markup injection risks across all user interfaces. Business analysts and executives can explore analytics dashboards with complete confidence in browser security. Comprehensive XSS prevention documentation is published at http://localhost:3000/docs/topic-18.

---
*BaseInt Reference Portal: [http://localhost:3000/docs/topic-18](http://localhost:3000/docs/topic-18)*
