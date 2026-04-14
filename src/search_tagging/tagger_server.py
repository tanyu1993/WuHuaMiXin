"""轻量状态打标服务器"""
import http.server, json, os, sys

_DIR = os.path.dirname(os.path.abspath(__file__))
# 重构后新架构：向上2层到达项目根
PROJECT = os.path.normpath(os.path.join(_DIR, '..', '..'))

SSOT = os.path.join(PROJECT, "data", "status_library_ssot.json")
STATUS_JS = os.path.join(_DIR, "status_data.js")
HTML = os.path.join(_DIR, "status_tagger_ui.html")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/status_tagger':
            self.send_file(HTML, 'text/html')
        elif self.path == '/status_data.js':
            self.send_file(STATUS_JS, 'application/javascript')
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/verify_status':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            name = body.get('name')
            with open(SSOT, 'r', encoding='utf-8-sig') as f:
                db = json.load(f)
            if name not in db:
                self.send_json({"error": "not found"}, 404)
                return
            for k in ('verified', 'tags', 'cat', 'desc'):
                if k in body:
                    db[name][k] = body[k]
            with open(SSOT, 'w', encoding='utf-8-sig') as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            # sync js
            lst = []
            for k, v in db.items():
                if k in ('version', 'tags'): continue
                if 'name' not in v: v['name'] = k
                lst.append(v)
            with open(STATUS_JS, 'w', encoding='utf-8') as f:
                f.write(f"const STATUS_DATA = {json.dumps(lst, ensure_ascii=False, indent=2)};")
            self.send_json({"ok": True})
        else:
            self.send_error(404)

    def send_file(self, path, ctype):
        with open(path, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', ctype + '; charset=utf-8')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        pass  # quiet

if __name__ == '__main__':
    port = 8899
    srv = http.server.HTTPServer(('127.0.0.1', port), Handler)
    print(f"Status Tagger running on http://127.0.0.1:{port}")
    srv.serve_forever()
