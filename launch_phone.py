"""Explicit local-network backend for physical phone testing, not a public server."""
import ipaddress
import os
import socket
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)
host = os.getenv('RAKIYA_LAN_HOST', '')
if not host:
    choices = socket.gethostbyname_ex(socket.gethostname())[2]
    choices = [a for a in choices if ipaddress.ip_address(a).version == 4 and ipaddress.ip_address(a).is_private and not ipaddress.ip_address(a).is_loopback]
    # Hyper-V/WSL adapters often appear first (172.x). Prefer a typical home
    # Wi-Fi subnet; RAKIYA_LAN_HOST remains the explicit override.
    choices.sort(key=lambda a: 0 if a.startswith('192.168.') else 1 if a.startswith('10.') else 2)
    if not choices:
        raise SystemExit('No Wi-Fi address found. Connect your computer to the same Wi-Fi as your phone, then retry.')
    host = choices[0]
address = ipaddress.ip_address(host)
if address.version != 4 or not address.is_private or address.is_loopback:
    raise SystemExit('RAKIYA_LAN_HOST must be a private local IPv4 address.')
probe = socket.socket()
if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
try:
    probe.bind((host, 8001))
except OSError:
    raise SystemExit('Port 8001 is already occupied. Close the older phone backend window before restarting.')
finally:
    probe.close()
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
os.environ['RAKIYA_ENV'] = 'local'
os.environ['DJANGO_ALLOWED_HOSTS'] = f'127.0.0.1,localhost,{host}'
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'migrate', '--noinput'])
execute_from_command_line(['manage.py', 'seed_examples'])
print(f'\nPHONE SERVER ADDRESS: http://{host}:8001\n'
      'Enter this address in the native Rakiya app.\n'
      'Same trusted Wi-Fi only. Use test credentials: this local connection is HTTP.\n'
      'Keep this window open. Closing it stops the phone backend.\n', flush=True)
execute_from_command_line(['manage.py', 'runserver', f'{host}:8001', '--noreload'])
