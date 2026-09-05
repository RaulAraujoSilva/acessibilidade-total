"""Inicialização local. Secrets gerados no primeiro uso, sem imprimir valores."""
import os,sys,json,secrets
from pathlib import Path
from cryptography.fernet import Fernet
root=Path(__file__).resolve().parent;config=root/'.local-config.json'
if not config.exists():
    config.write_text(json.dumps({'DJANGO_SECRET_KEY':secrets.token_urlsafe(48),'FERNET_KEY':Fernet.generate_key().decode()}),encoding='utf-8');config.chmod(0o600)
for key,value in json.loads(config.read_text(encoding='utf-8')).items():os.environ.setdefault(key,value)
os.environ.update(DEBUG='1',DISPATCH_MODE='database',DJANGO_SETTINGS_MODULE='portal.settings')
from django.core.management import execute_from_command_line
execute_from_command_line([str(root/'manage.py'),*sys.argv[1:]])
