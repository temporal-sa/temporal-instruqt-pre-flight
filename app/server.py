"""A visual readiness check. Instruqt supplies one container per guest."""

import asyncio
import json
import os
import secrets
import sqlite3
import time
from pathlib import Path

from aiohttp import WSMsgType, web

ROOT = Path(__file__).parent
CHECKS = {
    "ziggy": "Ziggy in the browser",
    "editor": "Code editor",
    "terminal": "Live terminal output",
    "temporal": "Temporal UI",
}
DB_KEY = web.AppKey("database", sqlite3.Connection)


def read_session(db, token):
    row = db.execute("SELECT data FROM sessions WHERE token = ?", (token,)).fetchone()
    if not row:
        raise web.HTTPNotFound(text="This flight has expired. Reload Launchpad.")
    return json.loads(row[0])


def save_session(db, token, data):
    data["revision"] = data.get("revision", 0) + 1
    db.execute("INSERT OR REPLACE INTO sessions VALUES (?, ?)", (token, json.dumps(data)))
    db.commit()


def view(data):
    return {
        "checks": data["checks"],
        "connection": time.time() - data.get("last_echo", 0) < 15,
        "completed_at": data.get("completed_at"),
        "reference": data["reference"],
        "revision": data.get("revision", 0),
    }


def maybe_complete(data):
    if all(value == "yes" for value in data["checks"].values()) and view(data)["connection"]:
        data.setdefault("completed_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    elif not all(value == "yes" for value in data["checks"].values()):
        data.pop("completed_at", None)


async def session(request):
    db = request.app[DB_KEY]
    token = request.headers.get("X-Flight-Session")
    if token:
        data = read_session(db, token)
    else:
        # No cookies, local files, account details, or permissions are required.
        token = secrets.token_urlsafe(32)
        data = {
            "reference": secrets.token_hex(4).upper(),
            "checks": {key: "unset" for key in CHECKS},
            "last_echo": 0,
        }
        save_session(db, token, data)
    return web.json_response({"session": token, **view(data)})


async def confirm(request):
    token = request.headers.get("X-Flight-Session", "")
    db = request.app[DB_KEY]
    try:
        body = await request.json()
    except (ValueError, UnicodeError):
        raise web.HTTPBadRequest(text="Choose a response for this check.")
    if not isinstance(body, dict) or not isinstance(body.get("check"), str) or not isinstance(body.get("value"), str) or body["check"] not in CHECKS or body["value"] not in {"yes", "issue", "unset"}:
        raise web.HTTPBadRequest(text="Choose a response for this check.")
    # Read after awaiting the body, so concurrent answers cannot overwrite one another.
    data = read_session(db, token)
    data["checks"][body["check"]] = body["value"]
    maybe_complete(data)
    save_session(db, token, data)
    return web.json_response(view(data))


async def socket(request):
    ws = web.WebSocketResponse(heartbeat=10, max_msg_size=1024)
    await ws.prepare(request)
    token = None
    try:
        async for message in ws:
            if message.type != WSMsgType.TEXT:
                continue
            try:
                payload = json.loads(message.data)
                if not isinstance(payload, dict):
                    raise ValueError("Expected an object")
                if token is None:
                    token = payload.get("session", "")
                    if not isinstance(token, str):
                        raise ValueError("Invalid session")
                data = read_session(request.app[DB_KEY], token)
            except (ValueError, web.HTTPException):
                await ws.close(code=1008, message=b"Reload Launchpad to start a flight.")
                break
            # The browser must echo our nonce: this proves a round trip, not just an upgrade.
            if payload.get("echo") == data.get("nonce") and data.get("nonce"):
                data["last_echo"] = time.time()
                maybe_complete(data)
            data["nonce"] = secrets.token_hex(12)
            save_session(request.app[DB_KEY], token, data)
            await ws.send_json({"nonce": data["nonce"], **view(data)})
    finally:
        await ws.close()
    return ws


async def completion(request):
    # Sandbox-side endpoint used by the Instruqt check script. No synthetic solve path.
    rows = request.app[DB_KEY].execute("SELECT data FROM sessions").fetchall()
    complete = any(json.loads(row[0]).get("completed_at") for row in rows)
    return web.json_response({"complete": complete}, status=200 if complete else 409)


async def report(request):
    data = read_session(request.app[DB_KEY], request.headers.get("X-Flight-Session", ""))
    lines = [
        "Temporal Instruqt pre-flight check",
        f"Reference: {data['reference']}",
        f"Result: {'ALL CHECKS PASSED' if data.get('completed_at') else 'NEEDS ATTENTION / INCOMPLETE'}",
        f"Completed (UTC): {data.get('completed_at', 'Not completed')}",
        "",
        "Your answers:",
    ]
    for key, title in CHECKS.items():
        lines.append(f"- {title}: {data['checks'][key]}")
    lines += [
        "",
        f"Browser WebSocket round trip observed: {'yes' if data.get('last_echo') else 'no'}",
        "This is a point-in-time visual check for this browser, laptop and network.",
        "Typing, editing, clipboard access, long-lived sessions, LLMs and webinar services were not tested.",
        "",
        "If blocked, send this report and the affected tab name to your webinar organizer.",
        "Ask IT to review https://docs.instruqt.com/reference/platform/third-party-network-access",
        "If you cannot access the content, join the webinar from a personal machine rather than a work machine.",
    ]
    return web.Response(text="\n".join(lines), content_type="text/plain")


async def index(request):
    return web.FileResponse(ROOT / "static" / "index.html")


async def ziggy(request):
    return web.FileResponse(ROOT / "static" / "ziggy.html")


@web.middleware
async def no_cache(request, handler):
    response = await handler(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


def make_app(db_path=None):
    app = web.Application(client_max_size=4096, middlewares=[no_cache])
    path = db_path or os.environ.get("PREFLIGHT_DB", "/run/preflight/results.sqlite")
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, data TEXT NOT NULL)")
    app[DB_KEY] = db
    app.router.add_get("/", index)
    app.router.add_get("/ziggy", ziggy)
    async def health(_):
        return web.json_response({"status": "ok"})

    app.router.add_get("/healthz", health)
    app.router.add_post("/api/session", session)
    app.router.add_post("/api/confirm", confirm)
    app.router.add_get("/api/report", report)
    app.router.add_get("/api/completion", completion)
    app.router.add_get("/ws", socket)
    app.router.add_static("/assets", ROOT / "static" / "assets")
    app.router.add_static("/static", ROOT / "static", show_index=False)

    async def close_db(_):
        db.close()

    app.on_cleanup.append(close_db)
    return app


async def main():
    runner = web.AppRunner(make_app(), access_log=None)
    await runner.setup()
    # Match all three ordinary web-app ports in the webinar, as well as its editor and UI.
    for port in (5000, 8090, 8092):
        await web.TCPSite(runner, "0.0.0.0", port).start()
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
