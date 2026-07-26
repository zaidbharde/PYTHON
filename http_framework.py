import socket
import json
import threading
import re
import mimetypes
import traceback
from dataclasses import dataclass, field
from typing import Callable, Any, Optional
from urllib.parse import parse_qs, unquote
from datetime import datetime
from pathlib import Path

@dataclass
class Request:
    method:  str = ""
    path:    str = ""
    version: str = ""
    headers: dict = field(default_factory=dict)
    body:    str = ""
    params:  dict = field(default_factory=dict)
    query:   dict = field(default_factory=dict)

    def json(self) -> dict:
        try: return json.loads(self.body)
        except: return {}

    def get(self, key: str, default=None):
        return self.query.get(key, [default])[0]

@dataclass
class Response:
    status:  int = 200
    headers: dict = field(default_factory=dict)
    body:    str = ""

    STATUS_TEXT = {
        200: "OK", 201: "Created", 204: "No Content",
        301: "Moved Permanently", 302: "Found", 304: "Not Modified",
        400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
        404: "Not Found", 405: "Method Not Allowed",
        422: "Unprocessable Entity", 429: "Too Many Requests",
        500: "Internal Server Error"
    }

    def json(self, data: Any, status: int = 200) -> 'Response':
        self.status = status
        self.body = json.dumps(data, indent=2, default=str)
        self.headers["Content-Type"] = "application/json"
        return self

    def html(self, content: str, status: int = 200) -> 'Response':
        self.status = status
        self.body = content
        self.headers["Content-Type"] = "text/html; charset=utf-8"
        return self

    def redirect(self, url: str, permanent: bool = False) -> 'Response':
        self.status = 301 if permanent else 302
        self.headers["Location"] = url
        return self

    def build(self) -> bytes:
        status_text = self.STATUS_TEXT.get(self.status, "Unknown")
        self.headers.setdefault("Content-Type", "text/plain")
        self.headers["Content-Length"] = str(len(self.body.encode()))
        self.headers["Server"] = "PyMicro/1.0"
        self.headers["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        lines = [f"HTTP/1.1 {self.status} {status_text}"]
        for k, v in self.headers.items():
            lines.append(f"{k}: {v}")
        lines.append("")
        lines.append(self.body)
        return "\r\n".join(lines).encode()

class Router:
    def __init__(self):
        self.routes = []
        self.middleware = []
        self.error_handlers = {}

    def route(self, method: str, pattern: str):
        def decorator(fn):
            regex = re.sub(r':(\w+)', r'(?P<\1>[^/]+)', pattern)
            self.routes.append({
                "method": method.upper(),
                "pattern": pattern,
                "regex": re.compile(f"^{regex}$"),
                "handler": fn
            })
            return fn
        return decorator

    def get(self, p):    return self.route("GET", p)
    def post(self, p):   return self.route("POST", p)
    def put(self, p):    return self.route("PUT", p)
    def delete(self, p): return self.route("DELETE", p)

    def use(self, fn):
        self.middleware.append(fn)
        return fn

    def error(self, status: int):
        def decorator(fn):
            self.error_handlers[status] = fn
            return fn
        return decorator

    def match(self, method: str, path: str):
        for route in self.routes:
            if route["method"] != method:
                continue
            m = route["regex"].match(path)
            if m:
                return route["handler"], m.groupdict()
        return None, {}

class HTTPServer:
    def __init__(self, host="0.0.0.0", port=8080):
        self.host   = host
        self.port   = port
        self.router = Router()
        self.static_dir = None
        self.request_count = 0
        self.start_time = None

    def static(self, directory: str):
        self.static_dir = Path(directory)

    def parse_request(self, raw: str) -> Request:
        req = Request()
        lines = raw.split("\r\n")
        if not lines:
            return req

        parts = lines[0].split(" ", 2)
        if len(parts) >= 2:
            req.method  = parts[0].upper()
            full_path   = parts[1]
            req.version = parts[2] if len(parts) > 2 else "HTTP/1.1"

            if "?" in full_path:
                req.path, qs = full_path.split("?", 1)
                req.query = parse_qs(qs)
            else:
                req.path = full_path

            req.path = unquote(req.path)

        i = 1
        while i < len(lines) and lines[i]:
            if ":" in lines[i]:
                key, val = lines[i].split(":", 1)
                req.headers[key.strip().lower()] = val.strip()
            i += 1

        if i + 1 < len(lines):
            req.body = "\r\n".join(lines[i+1:])

        return req

    def serve_static(self, path: str) -> Optional[Response]:
        if not self.static_dir:
            return None
        file_path = self.static_dir / path.lstrip("/")
        if not file_path.is_file():
            return None
        if not str(file_path.resolve()).startswith(str(self.static_dir.resolve())):
            return None

        mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        content = file_path.read_text()
        resp = Response()
        resp.status = 200
        resp.body = content
        resp.headers["Content-Type"] = mime
        return resp

    def handle_client(self, conn: socket.socket, addr):
        try:
            raw = conn.recv(8192).decode("utf-8", errors="replace")
            if not raw:
                return

            req  = self.parse_request(raw)
            resp = Response()
            self.request_count += 1

            for mw in self.router.middleware:
                result = mw(req, resp)
                if result is False:
                    conn.sendall(resp.build())
                    return

            handler, params = self.router.match(req.method, req.path)
            req.params = params

            if handler:
                handler(req, resp)
            elif self.static_dir:
                static_resp = self.serve_static(req.path)
                if static_resp:
                    resp = static_resp
                else:
                    self.handle_error(404, req, resp)
            else:
                self.handle_error(404, req, resp)

            conn.sendall(resp.build())

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"  [{timestamp}] {addr[0]} {req.method} {req.path} → {resp.status}")

        except Exception as e:
            traceback.print_exc()
            error_resp = Response()
            error_resp.json({"error": str(e)}, 500)
            try:
                conn.sendall(error_resp.build())
            except:
                pass
        finally:
            conn.close()

    def handle_error(self, status: int, req: Request, resp: Response):
        if status in self.router.error_handlers:
            self.router.error_handlers[status](req, resp)
        else:
            resp.json({"error": Response.STATUS_TEXT.get(status, "Error")}, status)

    def run(self):
        self.start_time = datetime.now()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(128)

        print("=" * 50)
        print(f"  HTTP Server running on http://{self.host}:{self.port}")
        print("=" * 50)

        try:
            while True:
                conn, addr = sock.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("\n  Server stopped.")
        finally:
            sock.close()


app = HTTPServer(port=8080)

users_db = [
    {"id": 1, "name": "Alice",   "email": "alice@test.com",   "role": "admin"},
    {"id": 2, "name": "Bob",     "email": "bob@test.com",     "role": "user"},
    {"id": 3, "name": "Charlie", "email": "charlie@test.com", "role": "user"},
]
next_id = 4

@app.router.use
def logger(req, resp):
    req.headers["x-request-time"] = datetime.now().isoformat()
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["X-Powered-By"] = "PyMicro"

@app.router.get("/")
def index(req, resp):
    resp.html("""
    <h1>PyMicro HTTP Framework</h1>
    <ul>
        <li><a href="/api/users">GET /api/users</a></li>
        <li><a href="/api/stats">GET /api/stats</a></li>
        <li><a href="/health">GET /health</a></li>
    </ul>
    """)

@app.router.get("/health")
def health(req, resp):
    uptime = str(datetime.now() - app.start_time) if app.start_time else "0"
    resp.json({"status": "ok", "uptime": uptime, "requests": app.request_count})

@app.router.get("/api/users")
def get_users(req, resp):
    role = req.get("role")
    filtered = [u for u in users_db if not role or u["role"] == role]
    resp.json({"users": filtered, "count": len(filtered)})

@app.router.get("/api/users/:id")
def get_user(req, resp):
    uid = int(req.params.get("id", 0))
    user = next((u for u in users_db if u["id"] == uid), None)
    if user:
        resp.json(user)
    else:
        resp.json({"error": "User not found"}, 404)

@app.router.post("/api/users")
def create_user(req, resp):
    global next_id
    data = req.json()
    if not data.get("name") or not data.get("email"):
        resp.json({"error": "name and email required"}, 422)
        return
    user = {"id": next_id, "name": data["name"], "email": data["email"], "role": data.get("role", "user")}
    users_db.append(user)
    next_id += 1
    resp.json(user, 201)

@app.router.delete("/api/users/:id")
def delete_user(req, resp):
    uid = int(req.params.get("id", 0))
    user = next((u for u in users_db if u["id"] == uid), None)
    if user:
        users_db.remove(user)
        resp.json({"deleted": uid})
    else:
        resp.json({"error": "User not found"}, 404)

@app.router.get("/api/stats")
def stats(req, resp):
    resp.json({
        "total_users": len(users_db),
        "roles": {r: sum(1 for u in users_db if u["role"] == r) for r in set(u["role"] for u in users_db)},
        "requests_served": app.request_count
    })

@app.router.error(404)
def not_found(req, resp):
    resp.json({"error": "Route not found", "path": req.path}, 404)

if __name__ == "__main__":
    app.run()
