"""User-run launcher: prepare local data, wait for HTTP readiness, open browser."""
import os
import socket
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from django.core.management import execute_from_command_line

URL = 'http://127.0.0.1:8000/'

def open_when_ready():
    # Local traffic should never be sent to a system HTTP proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for _ in range(60):
        try:
            with opener.open(URL, timeout=1) as response:
                if response.status == 200 and b'Rakiya' in response.read():
                    print('\nRakiya is ready. Opening your browser.\n')
                    webbrowser.open(URL)
                    return
        except OSError:
            pass
        time.sleep(1)
    print('\nThe preview has not responded. Please share the messages in this window.\n')

if __name__ == '__main__':
    # Windows permits competing SO_REUSEADDR listeners. Never start another
    # development server on an occupied port, even if its HTTP check times out.
    probe = socket.socket()
    if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    try:
        probe.bind(('127.0.0.1', 8000))
    except OSError:
        probe.close()
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(URL, timeout=3) as response:
                if response.status != 200 or b'Rakiya' not in response.read():
                    raise OSError('Another app is using port 8000.')
            print('Rakiya is already running. Opening the existing preview.')
            webbrowser.open(URL)
            raise SystemExit(0)
        except OSError:
            print('Port 8000 is occupied but is not responding as Rakiya.\n'
                  'Close older Rakiya preview windows, then try again.\n'
                  'No duplicate server was started.')
            raise SystemExit(1)
    finally:
        probe.close()
    print('Starting Rakiya. Keep this window open while using the app.\n')
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    execute_from_command_line(['manage.py', 'seed_examples'])
    threading.Thread(target=open_when_ready, daemon=True).start()
    try:
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--noreload'])
    except KeyboardInterrupt:
        print('\nRakiya stopped.')
