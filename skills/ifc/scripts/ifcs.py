# Fast mode for the `ifc` skill: keeps one IFC model in memory.
# Copy to <project>/.ifc-skills/ifcs.py and run from the project root.
"""python .ifc-skills/ifcs.py open <model.ifc> | exec <script.py> | close"""
import contextlib, hmac, io, json, os, secrets, socket, subprocess, sys, time, traceback
from pathlib import Path
HERE = Path.cwd() / ".ifc-skills"  # the project's scratch folder, wherever this file is
SESSION, LOG, IDLE = HERE / "session.json", HERE / "ifcs.log", 30 * 60

def stamp(path):
    try:
        return [os.stat(path).st_mtime_ns, os.stat(path).st_size]
    except OSError:
        return None

def session():
    try:
        return json.loads(SESSION.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None

def read_line(sock):
    data = b""
    while not data.endswith(b"\n") and (chunk := sock.recv(65536)):
        data += chunk
    return json.loads(data or b"{}")

def request(s, payload, timeout=None):
    try:
        with socket.create_connection(("127.0.0.1", s["port"]), timeout=5) as sock:
            sock.settimeout(timeout)
            sock.sendall((json.dumps({**payload, "token": s["token"]}) + "\n").encode())
            return read_line(sock)
    except (OSError, TypeError, KeyError, ValueError):
        return {"ok": False, "error": "the fast mode server is not reachable"}

def ping(s):
    return bool(s) and request(s, {"op": "ping"}, 5).get("ok") is True

def forget():
    with contextlib.suppress(OSError):  # Windows: a reader may hold it for a moment
        SESSION.unlink(missing_ok=True)

def serve(path):
    import ifcopenshell
    before, start = stamp(path), time.time()
    base = {"model": ifcopenshell.open(path), "IFC_PATH": path}
    base["LOAD_SECONDS"] = round(time.time() - start, 2)
    server, token = socket.create_server(("127.0.0.1", 0)), secrets.token_urlsafe(24)
    server.settimeout(IDLE)
    SESSION.with_suffix(".tmp").write_text(json.dumps({
        "path": path, "stamp": before, "port": server.getsockname()[1], "pid": os.getpid(),
        "token": token, "load_seconds": base["LOAD_SECONDS"]}), encoding="utf-8")
    for _ in range(100):  # Windows refuses to replace a file while someone reads it
        with contextlib.suppress(PermissionError):
            os.replace(SESSION.with_suffix(".tmp"), SESSION)
            break
        time.sleep(0.05)
    while True:
        try:
            conn, _ = server.accept()
        except socket.timeout:
            break
        with conn:
            req, reply = read_line(conn), {"ok": True}
            if not hmac.compare_digest(str(req.get("token", "")), token):
                reply = {"ok": False, "error": "unauthorized"}
            elif req.get("op") == "exec":
                out = io.StringIO()
                try:
                    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                        exec(compile(req["code"], req.get("name", "<script>"), "exec"), dict(base))
                    reply["output"] = out.getvalue()
                except BaseException:
                    reply = {"ok": False, "output": out.getvalue(), "traceback": traceback.format_exc()}
            conn.sendall((json.dumps(reply, default=str) + "\n").encode())
            if req.get("op") == "stop" and reply["ok"]:
                break

def open_model(path):
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        return {"ok": False, "error": f"no such file: {path}"}
    s = session()
    live = ping(s)
    if live and s["path"] == path and s["stamp"] == stamp(path):
        return {"ok": True, "reused": True, "path": path, "load_seconds": s["load_seconds"]}
    changed = bool(s) and s["path"] == path and s["stamp"] != stamp(path)
    if live:
        request(s, {"op": "stop"}, 10)
    forget()
    HERE.mkdir(exist_ok=True)
    if not (HERE / ".gitignore").exists():
        (HERE / ".gitignore").write_text("*\n", encoding="utf-8")
    detach = ({"creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
              if os.name == "nt" else {"start_new_session": True})
    with open(LOG, "w", encoding="utf-8") as log:
        proc = subprocess.Popen([sys.executable, __file__, "serve", path],
                                stdin=subprocess.DEVNULL, stdout=log, stderr=log, **detach)
    while (session() or {}).get("pid") != proc.pid:
        if proc.poll() is not None:
            return {"ok": False, "error": "could not open the model",
                    "log": LOG.read_text(encoding="utf-8", errors="replace")[-2000:]}
        time.sleep(0.2)
    report = {"ok": True, "reused": False, "path": path, "load_seconds": session()["load_seconds"]}
    return {**report, "reloaded": True, "reason": "the file changed on disk"} if changed else report

def run(script):
    s = session()
    if s and (s["stamp"] != stamp(s["path"]) or not ping(s)):  # changed, or idle and gone
        print(json.dumps(report := open_model(s["path"])), file=sys.stderr)
        s = session() if report["ok"] else None
    reply = request(s, {"op": "exec", "code": Path(script).read_text(encoding="utf-8-sig"),
                        "name": script}) if s else {"ok": False, "error": "no model is open"}
    sys.stdout.write(reply.get("output", ""))
    if not reply.get("ok"):
        print(json.dumps({**reply, "output": None, "fix": "python .ifc-skills/ifcs.py open <model.ifc>"
                          if "traceback" not in reply else None}), file=sys.stderr)
    return 0 if reply.get("ok") else 1

def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    command, arg = (sys.argv[1:] + ["", ""])[:2]
    if command in ("serve", "exec"):
        return serve(arg) or 0 if command == "serve" else run(arg)
    if command == "open":
        report = open_model(arg)
    elif command == "close":
        s = session()
        report = {"ok": True, "closed": (s or {}).get("path"), "stopped": request(s, {"op": "stop"}, 10)["ok"]}
        forget()
    else:
        report = {"ok": False, "error": __doc__}
    print(json.dumps(report))
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
