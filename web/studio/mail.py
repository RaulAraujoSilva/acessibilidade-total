"""Envio transacional pela conta Google autorizada pelo administrador."""
import base64
import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class GmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        try:
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={'grant_type': 'refresh_token',
                      'client_id': settings.GMAIL_CLIENT_ID,
                      'client_secret': settings.GMAIL_CLIENT_SECRET,
                      'refresh_token': settings.GMAIL_REFRESH_TOKEN},
                timeout=settings.EMAIL_TIMEOUT,
            )
            response.raise_for_status()
            token = response.json()['access_token']
            sent = 0
            for message in email_messages:
                raw = base64.urlsafe_b64encode(message.message().as_bytes()).decode('ascii')
                result = requests.post(
                    'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
                    headers={'Authorization': 'Bearer ' + token},
                    json={'raw': raw}, timeout=settings.EMAIL_TIMEOUT,
                )
                result.raise_for_status()
                sent += 1
            return sent
        except (requests.RequestException, KeyError, ValueError):
            if self.fail_silently:
                return 0
            # Não repassar respostas do provedor ou tokens para logs e páginas.
            raise OSError('Serviço de envio de e-mail indisponível.') from None
