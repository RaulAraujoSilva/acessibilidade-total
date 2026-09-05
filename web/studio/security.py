import hashlib
import ipaddress
from datetime import timedelta
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from .models import AccessAttempt

def cipher():
    if not settings.FERNET_KEY: raise ImproperlyConfigured('Chave de cifragem não configurada no servidor.')
    return Fernet(settings.FERNET_KEY.encode())

def seal(value): return cipher().encrypt(value.encode()).decode()
def unseal(value): return cipher().decrypt(value.encode()).decode()

def limited(request,action,maximum=10):
    # Ativar apenas quando o proxy sobrescreve X-Real-IP e a porta web é privada.
    address=request.META.get('REMOTE_ADDR','')
    if settings.TRUST_PROXY_CLIENT_IP:
        try:address=str(ipaddress.ip_address(request.META.get('HTTP_X_REAL_IP','')))
        except ValueError:pass
    raw=action+'|'+address
    key=hashlib.sha256(raw.encode()).hexdigest()
    since=timezone.now()-timedelta(minutes=15)
    if AccessAttempt.objects.filter(key=key,created_at__gte=since).count()>=maximum:return True
    AccessAttempt.objects.create(key=key)
    return False
