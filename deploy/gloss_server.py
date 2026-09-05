"""Adaptador HTTP interno para o núcleo aberto VLibras, sem API de IA textual."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from vlibras_translator import translate

translator = translate.Translator()
neural = os.environ.get('VLIBRAS_NEURAL', '0') == '1'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Conteúdo do usuário não é registrado.

    def do_POST(self):
        if self.path != '/translate':
            self.send_error(404); return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 65536:
                self.send_error(413); return
            payload = json.loads(self.rfile.read(size))
            text = payload.get('text')
            if not isinstance(text, str) or not text.strip() or len(text) > 5000:
                self.send_error(400); return
            gloss = translator.translate(text, neural=neural)
            data = json.dumps({'translation': gloss}, ensure_ascii=False).encode()
        except Exception:
            self.send_error(503, 'Translation unavailable'); return
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers(); self.wfile.write(data)


HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
