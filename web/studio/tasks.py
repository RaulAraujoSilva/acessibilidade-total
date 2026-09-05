import copy
import json
import uuid
import shutil
from datetime import timedelta
from pathlib import Path
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import Document,ProviderKey,StageResult
from .content import fingerprint,compare
from .providers import adapt_block,ProviderError,TemporaryProviderError
from .security import unseal
from .exporters import export_all
from .libras import render,LibrasUnavailable

class Cancelled(Exception):pass
class LeaseBusy(Exception):pass

def alive(ident,run):
    if not Document.objects.filter(pk=ident,run_id=run,status=Document.Status.RUNNING).update(heartbeat=timezone.now()):raise Cancelled()

def execute(ident,run):
    with transaction.atomic():
        doc=Document.objects.select_for_update().get(pk=ident)
        if str(doc.run_id)!=str(run) or doc.status not in [Document.Status.QUEUED,Document.Status.RUNNING]:return
        if doc.status==Document.Status.RUNNING and doc.heartbeat and doc.heartbeat>timezone.now()-timedelta(seconds=180):raise LeaseBusy()
        doc.status=Document.Status.RUNNING;doc.heartbeat=timezone.now();doc.stage='Adaptando conteúdo';doc.save()
    try:
        original=doc.content;content=copy.deepcopy(original)
        config={'content':original,'options':doc.options,'model':doc.model_id,'prompt_version':1}
        fp=fingerprint(config);usage=[]
        key=None
        if doc.options.get('simplify') or doc.options.get('describe'):
            record=ProviderKey.objects.filter(owner=doc.owner).first()
            if not record:raise ProviderError('Configure sua chave OpenRouter antes de usar IA.')
            key=unseal(record.ciphertext)
        context=' '.join(b.get('text','') for b in original['blocks'] if b['kind']=='heading')[:2000]
        for i,b in enumerate(content['blocks']):
            alive(ident,run)
            needed=(doc.options.get('simplify') and b['kind'] in ['heading','paragraph']) or (doc.options.get('describe') and b['kind']=='image')
            if not needed:continue
            cached=StageResult.objects.filter(document=doc,fingerprint=fp,name=b['id']).first()
            if cached:result=cached.result
            else:
                adapted,u=adapt_block(b,key,doc.model_id,doc.options.get('simplify'),doc.options.get('describe'),context)
                alive(ident,run)
                result={'block':adapted,'usage':u}
                StageResult.objects.get_or_create(document=doc,fingerprint=fp,name=b['id'],defaults={'result':result})
            content['blocks'][i]=result['block'];usage.append({**result['usage'],'cache_hit':bool(cached)})
            Document.objects.filter(pk=ident,run_id=run,status=Document.Status.RUNNING).update(stage=f'Adaptando bloco {i+1} de {len(content["blocks"])}')
        alive(ident,run)
        out=settings.MEDIA_ROOT/str(doc.owner_id)/str(doc.pk)/str(run)
        files,report=export_all(content,out,doc.title,doc.options)
        report['comparison']=compare(original,content)
        report['warnings']=content.get('warnings',[])
        report['libras']={'status':'aguardando worker' if doc.options.get('libras') else 'não solicitada'}
        (out/'content.json').write_text(json.dumps(content,ensure_ascii=False,indent=2),encoding='utf-8')
        files.append('content.json')
        (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');files.append('report.json')
        alive(ident,run)
        Document.objects.filter(pk=ident,run_id=run,status=Document.Status.RUNNING).update(status=Document.Status.REVIEW,stage='Confira conteúdo e relatório',report=report,artifacts=files,usage={'calls':usage,'model':doc.model_id,'prompt_version':1},error='')
        if doc.options.get('libras'):
            if settings.DISPATCH_MODE=='database':render_libras.apply(args=[str(ident),str(run)])
            else:render_libras.delay(str(ident),str(run))
    except Cancelled:
        stale=(settings.MEDIA_ROOT/str(doc.owner_id)/str(doc.pk)/str(run)).resolve()
        if stale.is_relative_to(settings.MEDIA_ROOT.resolve()) and stale.exists():shutil.rmtree(stale)
        return
    except TemporaryProviderError:
        Document.objects.filter(pk=ident,run_id=run,status=Document.Status.RUNNING).update(status=Document.Status.QUEUED,stage='Aguardando nova tentativa')
        raise
    except (ProviderError,ValueError,OSError) as e:
        Document.objects.filter(pk=ident,run_id=run,status=Document.Status.RUNNING).update(status=Document.Status.FAILED,error=str(e)[:300],stage='Requer atenção')
    except Exception:
        Document.objects.filter(pk=ident,run_id=run,status=Document.Status.RUNNING).update(status=Document.Status.FAILED,error='Falha interna de processamento. As etapas concluídas foram preservadas.',stage='Requer atenção')
        raise

@shared_task(bind=True,max_retries=5)
def process_document(self,ident,run):
    try:execute(ident,run)
    except (TemporaryProviderError,LeaseBusy) as exc:
        if self.request.retries>=5:
            Document.objects.filter(pk=ident,run_id=run,status=Document.Status.QUEUED).update(status=Document.Status.FAILED,error='Limite de tentativas alcançado. Retome após verificar o provedor.')
            return
        raise self.retry(exc=exc,countdown=60 if isinstance(exc,LeaseBusy) else min(300,15*2**self.request.retries))

@shared_task(bind=True,max_retries=5)
def render_libras(self,ident,run):
    with transaction.atomic():
        doc=Document.objects.select_for_update().filter(pk=ident,run_id=run,status=Document.Status.REVIEW).first()
        if not doc or doc.report.get('libras',{}).get('status')!='aguardando worker':return
        if doc.stage=='Renderizando Libras' and doc.heartbeat and doc.heartbeat>timezone.now()-timedelta(seconds=900):return
        doc.stage='Renderizando Libras';doc.heartbeat=timezone.now();doc.save(update_fields=['stage','heartbeat'])
    out=settings.MEDIA_ROOT/str(doc.owner_id)/str(doc.pk)/str(run)
    content=json.loads((out/'content.json').read_text(encoding='utf-8'))
    manifests=[];files=[];error=''
    for b in content['blocks']:
        if not Document.objects.filter(pk=ident,run_id=run,status=Document.Status.REVIEW).update(heartbeat=timezone.now()):return
        text=b.get('text','')
        if b['kind']=='table':text='; '.join(', '.join(row) for row in b['rows'])
        if not text:continue
        try:
            result=render(text,out/'libras');result['block_id']=b['id'];manifests.append(result)
            files.append(str(Path(result['video']).relative_to(out)))
        except LibrasUnavailable as e:error=str(e);break
    with transaction.atomic():
        current=Document.objects.select_for_update().filter(pk=ident,run_id=run,status=Document.Status.REVIEW).first()
        if not current:return
        report=current.report
        report['libras']={'status':'indisponível' if error else 'gerado; revisão linguística pendente','error':error,'blocks':manifests}
        current.report=report;current.stage='Confira conteúdo e relatório';current.artifacts=list(dict.fromkeys(current.artifacts+files));current.save()
        (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
