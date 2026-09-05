from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from studio.models import Document
from studio.tasks import render_libras


class Command(BaseCommand):
    help = 'Reagenda apenas Libras após corrigir a infraestrutura, preservando o histórico da falha.'
    def add_arguments(self, parser):
        parser.add_argument('document_id')

    def handle(self, *args, **options):
        with transaction.atomic():
            doc = Document.objects.select_for_update().get(pk=options['document_id'])
            if doc.status != 'review' or doc.report.get('libras', {}).get('status') != 'indisponível':
                raise CommandError('O documento deve estar em revisão, com Libras indisponível.')
            doc.report.setdefault('libras_attempts', []).append(doc.report['libras'])
            doc.report['libras'] = {'status': 'aguardando worker'}
            doc.stage = 'Aguardando Libras'; doc.heartbeat = None
            doc.save(update_fields=['report', 'stage', 'heartbeat'])
            transaction.on_commit(lambda: render_libras.delay(str(doc.pk), str(doc.run_id)))
        self.stdout.write('Libras reagendada; as saídas documentais serão preservadas.')
