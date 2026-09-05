"""Recuperação periódica de etapas interrompidas, sem dados na mensagem da fila."""
import os
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
import django
django.setup()
from django.core.management import call_command

while True:
    try:
        call_command('recover_jobs')
    except Exception:
        print('Recuperação indisponível; nova tentativa em 60 segundos.', flush=True)
    time.sleep(60)
