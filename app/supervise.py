"""Run the browser surfaces automatically in each guest's sandbox container."""
import fcntl
import json
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/opt/preflight")
RUN = Path("/run/preflight")
RUN.mkdir(parents=True, exist_ok=True)
lock = (RUN / "supervisor.lock").open("w")
try:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    sys.exit(0)
workspace = Path("/root/preflight")
workspace.mkdir(parents=True, exist_ok=True)
(workspace / "README.md").write_text(
    "# Hello, space explorer!\n\nYour code editor has landed. Ziggy approves.\n\n"
    "You do not need to type or change anything.\n"
    "Return to Launchpad and choose **Yes, editor’s here**.\n"
)
(workspace / "hello_temporal.py").write_text(
    '# Your workshop code will appear in an editor like this.\n'
    '# There is nothing to run during pre-flight.\n\n'
    'message = "Hello from Temporal. Ready when you are!"\nprint(message)\n'
)
settings = Path("/root/.local/share/code-server/User/settings.json")
settings.parent.mkdir(parents=True, exist_ok=True)
settings.write_text(json.dumps({
    "workbench.colorTheme": "Default Dark+", "workbench.startupEditor": "readme",
    "workbench.tips.enabled": False, "security.workspace.trust.enabled": False,
    "telemetry.telemetryLevel": "off", "update.mode": "none", "editor.fontSize": 15,
    "window.menuBarVisibility": "compact",
}))
commands = {
    "temporal": ["temporal", "--disable-config-file", "server", "start-dev", "--ip", "0.0.0.0", "--ui-ip", "0.0.0.0", "--ui-port", "8233", "--ui-disable-news-fetch", "--db-filename", str(RUN / "temporal.db"), "--log-level", "warn"],
    "editor": ["code-server", "--bind-addr", "0.0.0.0:8080", "--auth", "none", "--disable-telemetry", "--disable-update-check", str(workspace)],
    "launchpad": [sys.executable, str(ROOT / "server.py")],
}
children = []
stopping = False


def stop(*_):
    global stopping
    stopping = True


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
try:
    for name, command in commands.items():
        with (RUN / f"{name}.log").open("a") as log:
            children.append((name, subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)))
    while not stopping:
        for name, child in children:
            if child.poll() is not None:
                raise RuntimeError(f"{name} stopped with exit code {child.returncode}; see /run/preflight/{name}.log")
        time.sleep(0.5)
finally:
    for _, child in children:
        if child.poll() is None:
            child.terminate()
    deadline = time.monotonic() + 8
    for _, child in children:
        try:
            child.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
