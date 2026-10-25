"""Минимальный клиент Chrome DevTools Protocol (websocket-client).

Используется скриптами замеров: открывает страницу стенда во вкладке
headless Chrome, выполняет JavaScript (с await) и снимает скриншоты.
"""
import base64
import json
import time
import urllib.request

import websocket


class Tab:
    def __init__(self, port=9333, url='about:blank'):
        req = urllib.request.Request(f'http://127.0.0.1:{port}/json/new?{url}', method='PUT')
        info = json.load(urllib.request.urlopen(req))
        self.id = info['id']
        self.port = port
        self.ws = websocket.create_connection(info['webSocketDebuggerUrl'], timeout=600)
        self.n = 0
        self.console = []

    def call(self, method, **params):
        self.n += 1
        mid = self.n
        self.ws.send(json.dumps({'id': mid, 'method': method, 'params': params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get('method') == 'Runtime.consoleAPICalled':
                args = msg['params']['args']
                self.console.append(' '.join(str(a.get('value', a.get('description', ''))) for a in args))
            if msg.get('method') == 'Page.javascriptDialogOpening':
                self.console.append('DIALOG: ' + msg['params']['message'])
                self.n += 1
                self.ws.send(json.dumps({'id': self.n, 'method': 'Page.handleJavaScriptDialog',
                                         'params': {'accept': True}}))
            if msg.get('id') == mid:
                if 'error' in msg:
                    raise RuntimeError(msg['error'])
                return msg.get('result', {})

    def eval(self, expr):
        r = self.call('Runtime.evaluate', expression=expr, awaitPromise=True,
                      returnByValue=True, timeout=600000)
        if 'exceptionDetails' in r:
            raise RuntimeError(r['exceptionDetails'].get('exception', {}).get('description')
                               or r['exceptionDetails'])
        return r['result'].get('value')

    def goto(self, url, wait=1.5):
        self.call('Network.enable')
        self.call('Network.setCacheDisabled', cacheDisabled=True)
        self.call('Page.enable')
        self.call('Runtime.enable')
        self.call('Page.navigate', url=url)
        time.sleep(wait)

    def set_viewport(self, w, h):
        self.call('Emulation.setDeviceMetricsOverride', width=w, height=h,
                  deviceScaleFactor=1, mobile=False)

    def screenshot(self, path, full=True):
        params = {'format': 'png'}
        if full:
            m = self.call('Page.getLayoutMetrics')['cssContentSize']
            params['clip'] = {'x': 0, 'y': 0, 'width': m['width'], 'height': m['height'], 'scale': 1}
            params['captureBeyondViewport'] = True
        data = self.call('Page.captureScreenshot', **params)['data']
        with open(path, 'wb') as f:
            f.write(base64.b64decode(data))

    def close(self):
        self.ws.close()
        urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/close/{self.id}')
