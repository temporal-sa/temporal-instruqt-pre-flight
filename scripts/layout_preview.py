#!/usr/bin/env python3
"""Package a layout preview with decorative motion, without starting demo services."""
import base64
import html
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
static = root / 'app/static'


def asset_path(url):
    return static / (url.removeprefix('/static/') if url.startswith('/static/') else url.lstrip('/'))


def bundle(name):
    source = (static / name).read_text()
    scripts = []

    def script(match):
        path = asset_path(match[1])
        if path.name != 'flight.js':
            scripts.append(path.read_text())
        return ''

    source = re.sub(r'<script src="([^"]+)"[^>]*></script>', script, source)

    def sheet(match):
        path = asset_path(match[1])
        css = path.read_text()

        def font(match):
            encoded = base64.b64encode((path.parent / match[1]).read_bytes()).decode()
            return 'url("data:font/woff2;base64,' + encoded + '")'

        return '<style>' + re.sub(r'url\("([^"]+\.woff2)"\)', font, css) + '</style>'

    source = re.sub(r'<link rel="stylesheet" href="([^"]+)">', sheet, source)
    for match in set(re.findall(r'/assets/brand/[^" ]+', source)):
        path = asset_path(match)
        mime = 'image/svg+xml' if path.suffix == '.svg' else 'image/png'
        source = source.replace(match, 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode())
    return source.replace('</body>', ''.join('<script>' + script + '</script>' for script in scripts) + '</body>')


source = bundle('index.html')
source = source.replace('id="ziggy-frame"', 'id="ziggy-frame" srcdoc="' + html.escape(bundle('ziggy.html'), quote=True) + '"')
for element, label in (('editor-frame', 'The real editor loads here in the running container.'), ('temporal-frame', 'The real Temporal UI loads here in the running container.')):
    placeholder = '<body style="background:#141414;color:#cacbf9;font:16px/1.6 system-ui;padding:36px"><p>' + label + '</p><p>Container runtime verification is pending.</p></body>'
    source = source.replace('id="' + element + '"', 'id="' + element + '" srcdoc="' + html.escape(placeholder, quote=True) + '"')
source = source.replace('<body>', '<body><div style="position:relative;z-index:1;padding:12px 32px;background:#262052;color:#f8fafc;font:13px system-ui">Layout preview · Runtime services are not running · Confirmations are disabled</div>')
target = Path('/private/tmp/temporal-preflight-layout.html')
target.write_text(source)
print(target)
