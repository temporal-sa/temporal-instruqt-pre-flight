#!/usr/bin/env python3
"""Package a static layout preview; does not start any demo processes."""
import base64
import html
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
static = root / 'app/static'
source = (static / 'index.html').read_text()
source = re.sub(r'<script.*?</script>', '', source, flags=re.S)
for sheet in ('assets/css/temporal-theme.css', 'assets/css/temporal-components.css', 'flight.css'):
    path = static / sheet
    css = path.read_text()
    def font(match):
        font_path = path.parent / match[1]
        encoded = base64.b64encode(font_path.read_bytes()).decode()
        return 'url("data:font/woff2;base64,' + encoded + '")'
    css = re.sub(r'url\("([^"]+\.woff2)"\)', font, css)
    target = '/static/flight.css' if sheet == 'flight.css' else '/' + sheet
    source = source.replace('<link rel="stylesheet" href="' + target + '">', '<style>' + css + '</style>')
for image in ('temporal-logo.svg', 'ziggy-peek.png'):
    path = static / 'assets/brand' / image
    mime = 'image/svg+xml' if image.endswith('.svg') else 'image/png'
    data = 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()
    source = source.replace('/assets/brand/' + image, data)
ziggy = (static / 'ziggy.html').read_text()
ziggy = ziggy.replace('<link rel="stylesheet" href="/assets/css/temporal-theme.css">', '<style>' + (static / 'assets/css/temporal-theme.css').read_text() + '</style>')
ziggy = ziggy.replace('/assets/brand/ziggy-peek.png', 'data:image/png;base64,' + base64.b64encode((static / 'assets/brand/ziggy-peek.png').read_bytes()).decode())
source = source.replace('id="ziggy-frame"', 'id="ziggy-frame" srcdoc="' + html.escape(ziggy, quote=True) + '"')
for element, label in (('editor-frame', 'The real editor loads here in the running container.'), ('temporal-frame', 'The real Temporal UI loads here in the running container.')):
    placeholder = '<body style="background:#141414;color:#cacbf9;font:16px/1.6 system-ui;padding:36px"><p>' + label + '</p><p>Container runtime verification is pending.</p></body>'
    source = source.replace('id="' + element + '"', 'id="' + element + '" srcdoc="' + html.escape(placeholder, quote=True) + '"')
source = source.replace('<body>', '<body><div style="padding:12px 32px;background:#262052;color:#f8fafc;font:13px system-ui">Static layout preview · Runtime services are not running · Confirmations are disabled</div>')
target = Path('/private/tmp/temporal-preflight-layout.html')
target.write_text(source)
print(target)
