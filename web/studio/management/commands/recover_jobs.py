from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from studio.models import Document
from studio.tasks import process_document,render_libras

class Command(BaseCommand):
    help='Republica trabalhos aguardando ou com lease vencido. Não envia conteúdo nem credenciais.'
    def handle(self,*args,**options):
        jobs=Document.objects.filter(Q(status='queued')|Q(status='running',heartbeat__lt=timezone.now()-timedelta(seconds=180)))
        count=0
        for doc in jobs.iterator():
            if doc.run_id:process_document.delay(str(doc.pk),str(doc.run_id));count+=1
        pending=Document.objects.filter(status='review')
        for doc in pending.iterator():
            if doc.run_id and doc.report.get('libras',{}).get('status')=='aguardando worker':
                if doc.stage!='Renderizando Libras' or not doc.heartbeat or doc.heartbeat<timezone.now()-timedelta(seconds=900):
                    render_libras.delay(str(doc.pk),str(doc.run_id));count+=1
        self.stdout.write(f'{count} trabalhos republicados; checkpoints impedem repetir etapas concluídas.')
