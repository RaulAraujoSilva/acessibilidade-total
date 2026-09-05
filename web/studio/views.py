import copy
import json
import shutil
import uuid
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction,IntegrityError
from django.http import FileResponse,HttpResponse,JsonResponse,Http404
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.views.decorators.http import require_POST
from .models import User,Document,ProviderKey
from .forms import SignupForm,LoginForm,KeyForm,UploadForm,OptionsForm,VideoForm
from .security import limited,seal
from .content import extract
from .providers import models,estimate
from .tasks import process_document

def home(request):return render(request,'home.html')

class LoginView(auth_views.LoginView):
    authentication_form=LoginForm;template_name='form.html';extra_context={'title':'Entrar','button':'Entrar'}
    def post(self,request,*args,**kwargs):
        if limited(request,'login'):return HttpResponse('Muitas tentativas. Aguarde 15 minutos.',status=429)
        return super().post(request,*args,**kwargs)

def signup(request):
    form=SignupForm(request.POST or None)
    if request.method=='POST':
        if limited(request,'signup',5):return HttpResponse('Muitas tentativas. Aguarde 15 minutos.',status=429)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user=form.save()
                    uid=urlsafe_base64_encode(force_bytes(user.pk));token=default_token_generator.make_token(user)
                    link=settings.SITE_URL+reverse('activate',args=[uid,token])
                    send_mail('Confirme seu cadastro no Acessibilidade Total','Confirme seu cadastro: '+link,settings.DEFAULT_FROM_EMAIL,[user.email])
            except (OSError,IntegrityError):form.add_error(None,'Não foi possível concluir o cadastro. Verifique a disponibilidade do envio de e-mail.')
            else:return render(request,'notice.html',{'title':'Confira seu e-mail','text':'Enviamos o link de confirmação. Só depois da confirmação sua conta poderá ser usada.'})
    return render(request,'form.html',{'form':form,'title':'Criar conta','button':'Criar conta'})

def activate(request,uid,token):
    try:user=User.objects.get(pk=urlsafe_base64_decode(uid).decode())
    except (ValueError,User.DoesNotExist,UnicodeDecodeError):raise Http404()
    if not default_token_generator.check_token(user,token):return HttpResponse('Link inválido ou expirado.',status=400)
    if request.method=='POST':
        user.is_active=True;user.save();messages.success(request,'Conta confirmada. Você já pode entrar.');return redirect('login')
    return render(request,'form.html',{'title':'Confirmar cadastro','button':'Confirmar meu e-mail'})

@login_required
def key_settings(request):
    form=KeyForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        try:ProviderKey.objects.update_or_create(owner=request.user,defaults={'ciphertext':seal(form.cleaned_data['key'])})
        except Exception:form.add_error(None,'O servidor ainda não está configurado para cifrar chaves.')
        else:messages.success(request,'Chave cifrada e salva.');return redirect('keys')
    return render(request,'form.html',{'title':'Sua chave OpenRouter','form':form,'button':'Salvar chave','has_key':ProviderKey.objects.filter(owner=request.user).exists(),'key_page':True})

@login_required
@require_POST
def delete_key(request):
    ProviderKey.objects.filter(owner=request.user).delete();messages.success(request,'Chave removida.');return redirect('keys')

@login_required
def documents(request):
    return render(request,'documents.html',{'documents':Document.objects.filter(owner=request.user).order_by('-created_at')})

@login_required
def upload(request):
    form=UploadForm(request.POST or None,request.FILES or None)
    if request.method=='POST' and form.is_valid():
        if Document.objects.filter(owner=request.user).count()>=20:form.add_error(None,'Limite inicial de 20 documentos. Exclua documentos antigos para enviar outros.')
        else:
            doc=form.save(False);doc.owner=request.user;doc.original_name=request.FILES['source'].name;doc.save()
            try:doc.content=extract(doc.source.path);doc.save()
            except Exception as e:
                doc.source.delete();doc.delete()
                form.add_error('source',str(e) if isinstance(e,ValueError) else 'Não foi possível extrair o documento. Confira seu formato.')
            else:return redirect('detail',ident=doc.pk)
    return render(request,'form.html',{'form':form,'title':'Preparar um documento','button':'Enviar e conferir extração','upload':True})

def owned(request,ident):return get_object_or_404(Document,pk=ident,owner=request.user)

def locked(request,ident):return get_object_or_404(Document.objects.select_for_update(),pk=ident,owner=request.user)

@login_required
def detail(request,ident):
    doc=owned(request,ident);form=OptionsForm(initial=doc.options or {'pptx':doc.original_name.lower().endswith('.pptx'),'color_safe':True})
    return render(request,'detail.html',{'doc':doc,'form':form,'report_json':json.dumps(doc.report,ensure_ascii=False,indent=2),'video_form':VideoForm()})

@login_required
@require_POST
@transaction.atomic
def prepare(request,ident):
    doc=locked(request,ident);form=OptionsForm(request.POST)
    if doc.status in [Document.Status.RUNNING,Document.Status.QUEUED]:return HttpResponse('Aguarde ou cancele o trabalho atual.',status=409)
    if not form.is_valid():return render(request,'form.html',{'form':form,'title':'Escolher adaptações','button':'Calcular estimativa'},status=400)
    options=form.cleaned_data.copy();model_id=options.pop('model_id','');options.pop('consent')
    est={'usd':0,'note':'Sem chamadas de IA textual.'}
    if options.get('simplify') or options.get('describe'):
        if not ProviderKey.objects.filter(owner=request.user).exists():messages.error(request,'Configure sua chave antes de continuar.');return redirect('keys')
        try:
            model=next(m for m in models() if m['id']==model_id)
            if options.get('describe') and 'image' not in model.get('architecture',{}).get('input_modalities',[]):raise ValueError()
            est=estimate(doc.content,model)
        except Exception:return HttpResponse('Modelo indisponível ou incompatível. Confira o identificador e o suporte a imagens.',status=400)
    doc.options=options;doc.model_id=model_id;doc.estimate=est;doc.status=Document.Status.CREATED;doc.run_id=None;doc.reviewed_at=None;doc.artifacts=[];doc.save()
    return render(request,'confirm.html',{'doc':doc})

@login_required
@require_POST
def start(request,ident):
    with transaction.atomic():
        user=User.objects.select_for_update().get(pk=request.user.pk)
        doc=get_object_or_404(Document.objects.select_for_update(),pk=ident,owner=user)
        if doc.status not in [Document.Status.CREATED,Document.Status.FAILED]:return HttpResponse('Este trabalho não pode ser iniciado neste estado.',status=409)
        if not doc.options:return HttpResponse('Confira as opções antes de iniciar.',status=400)
        if Document.objects.filter(owner=user,status__in=['running','queued']).count()>=2:return HttpResponse('Limite de dois trabalhos ativos por conta.',status=429)
        doc.run_id=uuid.uuid4();doc.status=Document.Status.QUEUED;doc.stage='Aguardando processamento';doc.error='';doc.save()
    if settings.DISPATCH_MODE=='celery':
        try:process_document.delay(str(doc.pk),str(doc.run_id))
        except Exception:
            Document.objects.filter(pk=doc.pk,run_id=doc.run_id,status='queued').update(status='failed',error='Fila indisponível. Tente novamente mais tarde.')
    return redirect('detail',ident=doc.pk)

@login_required
def status(request,ident):
    d=owned(request,ident);return JsonResponse({'status':d.status,'label':d.get_status_display(),'stage':d.stage,'error':d.error})

@login_required
@transaction.atomic
def edit_content(request,ident):
    doc=locked(request,ident)
    if doc.status in ['running','queued','review']:return HttpResponse('Cancele o processamento ou a revisão antes de corrigir a origem.',status=409)
    if request.method=='POST':
        content=copy.deepcopy(doc.content);changes=[]
        for b in content['blocks']:
            if b['kind']=='table':continue
            value=request.POST.get(b['id'],b.get('text',''))
            if len(value)>20000:return HttpResponse('Trecho excede 20000 caracteres.',status=400)
            if value!=b.get('text',''):
                changes.append({'block_id':b['id'],'previous':b.get('text',''),'date':timezone.now().isoformat()})
                b['text']=value
                if b['kind']=='image':b['alt']=value
        content.setdefault('corrections',[]).extend(changes)
        doc.content=content;doc.status='created';doc.run_id=None;doc.artifacts=[];doc.options={};doc.save()
        return redirect('detail',ident=ident)
    return render(request,'edit.html',{'doc':doc})

@login_required
@require_POST
def cancel(request,ident):
    doc=owned(request,ident)
    Document.objects.filter(pk=doc.pk,status__in=['queued','running','review']).update(status='cancelled',stage='Cancelado',run_id=None)
    return redirect('detail',ident=ident)

@login_required
@require_POST
@transaction.atomic
def approve(request,ident):
    doc=locked(request,ident)
    if doc.report.get('libras',{}).get('status')=='aguardando worker':return HttpResponse('Aguarde Libras ou cancele.',status=409)
    if request.POST.get('reviewed')!='yes':return HttpResponse('Confirme a revisão do conteúdo e das limitações.',status=400)
    Document.objects.filter(pk=doc.pk,status='review').update(status='done',reviewed_at=timezone.now(),stage='Revisão do autor registrada; não é certificação de acessibilidade')
    return redirect('detail',ident=ident)

@login_required
def download(request,ident,index):
    doc=owned(request,ident)
    if doc.status not in ['review','done'] or index>=len(doc.artifacts):raise Http404()
    root=(settings.MEDIA_ROOT/str(doc.owner_id)/str(doc.pk)/str(doc.run_id)).resolve()
    path=(root/doc.artifacts[index]).resolve()
    if not path.is_relative_to(root) or not path.is_file():raise Http404()
    return FileResponse(path.open('rb'),as_attachment=True,filename=path.name)

@login_required
@require_POST
@transaction.atomic
def attach_video(request,ident):
    doc=locked(request,ident);form=VideoForm(request.POST,request.FILES)
    if doc.status!='review' or not form.is_valid():return HttpResponse('Envie vídeo MP4 revisado durante a etapa de revisão.',status=400)
    block=form.cleaned_data['block_id']
    if block not in {b['id'] for b in doc.content['blocks']}:return HttpResponse('Bloco inexistente.',status=400)
    name=f'revisado-{block}-{uuid.uuid4().hex[:8]}.mp4'
    root=settings.MEDIA_ROOT/str(doc.owner_id)/str(doc.pk)/str(doc.run_id)
    with (root/name).open('wb') as f:
        for chunk in form.cleaned_data['video'].chunks():f.write(chunk)
    doc.artifacts.append(name);doc.report.setdefault('manual_libras',[]).append({'block_id':block,'file':name,'reviewed_by':doc.owner_id,'date':timezone.now().isoformat()});doc.save()
    return redirect('detail',ident=ident)

@login_required
@require_POST
@transaction.atomic
def delete_document(request,ident):
    doc=locked(request,ident)
    if doc.status in ['running','queued','review']:return HttpResponse('Cancele o trabalho antes de excluir.',status=409)
    root=(settings.MEDIA_ROOT/str(doc.owner_id)/str(doc.pk)).resolve()
    if root.is_relative_to(settings.MEDIA_ROOT.resolve()) and root.exists():shutil.rmtree(root)
    doc.delete();return redirect('documents')
