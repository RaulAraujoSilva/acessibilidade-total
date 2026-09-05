import time
from django.core.management.base import BaseCommand,CommandError
from django.conf import settings
from studio.models import Document
from studio.tasks import execute,LeaseBusy
from studio.providers import TemporaryProviderError

class Command(BaseCommand):
    help='Worker local de demonstração; produção usa Celery com Redis.'
    def add_arguments(self,parser):parser.add_argument('--once',action='store_true')
    def handle(self,*args,**opts):
        if not settings.DEBUG:raise CommandError('Comando exclusivo de desenvolvimento.')
        while True:
            for doc in Document.objects.filter(status='queued').order_by('created_at'):
                try:execute(str(doc.pk),str(doc.run_id))
                except (TemporaryProviderError,LeaseBusy):pass
            if opts['once']:break
            time.sleep(3)
