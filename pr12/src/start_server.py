# Листинг 12.2 методички (локальный HTTP-сервер для стенда WebGPU).
# Дополнено: порт можно передать первым аргументом, ключ --no-browser
# отключает автоматическое открытие браузера (нужно для запуска в фоне).
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os
import sys
import webbrowser

HOST = 'localhost'
PORT = 8000

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if args:
        PORT = int(args[0])
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    url = f'http://{HOST}:{PORT}'
    print(f'Serving at {url}', flush=True)
    if '--no-browser' not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    server = ThreadingHTTPServer((HOST, PORT), SimpleHTTPRequestHandler)
    server.serve_forever()
