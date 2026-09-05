"""Coleta arquivos estáticos no contêiner que atenderá a aplicação."""
import os,subprocess,sys
subprocess.run([sys.executable,'manage.py','collectstatic','--noinput'],check=True)
os.execvp('gunicorn',['gunicorn','portal.wsgi:application','--bind','0.0.0.0:'+os.environ.get('PORT','8000'),'--workers','2','--timeout','60'])
