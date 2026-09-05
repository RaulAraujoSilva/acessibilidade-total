"""Adaptador de renderização direta. Não recorre a captura de navegador."""
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
import requests

class LibrasUnavailable(Exception):pass

def render(text,out,avatar='icaro',fps=25):
    renderer=os.environ.get('VLIBRAS_RENDERER','');bundles=os.environ.get('VLIBRAS_BUNDLES','')
    if not renderer or not Path(renderer).is_file() or not Path(bundles).is_dir():
        raise LibrasUnavailable('Renderizador VLibras e bundles não disponíveis. Anexe vídeo revisado; geração automática permanece pendente.')
    wsl=os.environ.get('VLIBRAS_WSL_DISTRO','') if os.name=='nt' else ''
    prefix=['wsl','-d',wsl,'--exec'] if wsl else []
    def runtime_path(path):
        p=Path(path).resolve()
        return '/mnt/'+p.drive[0].lower()+p.as_posix()[2:] if wsl else str(p)
    ffmpeg='ffmpeg' if wsl else shutil.which('ffmpeg');ffprobe='ffprobe' if wsl else shutil.which('ffprobe');xvfb='xvfb-run' if wsl else shutil.which('xvfb-run')
    if not all([ffmpeg,ffprobe,xvfb]):raise LibrasUnavailable('ffmpeg, ffprobe e Xvfb são necessários no worker Linux.')
    if len(text)>5000:raise LibrasUnavailable('Bloco de Libras excede 5000 caracteres; divida o conteúdo sem omitir informação.')
    start=time.perf_counter()
    identity={'text':text,'avatar':avatar,'fps':fps,'renderer_sha256':hashlib.sha256(Path(renderer).read_bytes()).hexdigest(),'bundles_version':os.environ.get('VLIBRAS_BUNDLES_VERSION','não informada')}
    key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    target=Path(out)/key;target.mkdir(parents=True,exist_ok=True)
    if (target/'manifest.json').exists() and (target/'libras.mp4').exists():return json.loads((target/'manifest.json').read_text(encoding='utf-8'))
    try:
        response=requests.post(os.environ.get('VLIBRAS_TRANSLATE_URL','https://traducao2.vlibras.gov.br/translate'),json={'text':text},timeout=40)
        response.raise_for_status()
        try:
            data=response.json();gloss=data if isinstance(data,str) else data.get('gloss') or data.get('glosa') or data.get('translation')
        except ValueError:gloss=response.text
        if not isinstance(gloss,str) or not gloss.strip():raise ValueError('glosa vazia')
    except (requests.RequestException,ValueError):raise LibrasUnavailable('Serviço de glosa indisponível ou resposta inválida.') from None
    glosa=target/'glosa.txt';glosa.write_text('0#'+gloss.strip()+'\n',encoding='utf-8')
    frames=target/'frames';frames.mkdir(exist_ok=True)
    # Uma tentativa incompleta não pode deixar quadros extras no vídeo seguinte.
    for old_frame in frames.glob('*.jpg'):old_frame.unlink()
    command=prefix+[xvfb,'-a',runtime_path(renderer),'--id',key,'--glosapath',runtime_path(glosa),'--videopath',runtime_path(frames),'--width','720','--height','900','--speed','150','--framerate',str(fps),'--avatar',avatar,'--subtitle','off','--bundlespath',runtime_path(bundles)]
    try:
        run=subprocess.run(command,capture_output=True,timeout=600)
        (target/'renderer.log').write_bytes(run.stdout+run.stderr)
        if run.returncode or not list(frames.glob('*.jpg')):raise LibrasUnavailable('Renderizador não produziu quadros válidos; consultar relatório técnico.')
        subprocess.run(prefix+[ffmpeg,'-y','-framerate',str(fps),'-pattern_type','glob','-i',runtime_path(frames/'*.jpg'),'-pix_fmt','yuv420p',runtime_path(target/'libras.mp4')],check=True,capture_output=True,timeout=180)
        probe=subprocess.run(prefix+[ffprobe,'-v','quiet','-print_format','json','-show_streams','-show_format',runtime_path(target/'libras.mp4')],check=True,capture_output=True,text=True,timeout=30)
    except (subprocess.SubprocessError,OSError):raise LibrasUnavailable('Falha ou tempo limite na renderização de Libras.') from None
    report={'cache_key':key,'video':str(target/'libras.mp4'),'elapsed_seconds':time.perf_counter()-start,'probe':json.loads(probe.stdout),'human_review':'pendente','alignment':'bloco completo; sincronização por palavra não medida','missing_signs':'não verificado','identity':identity}
    (target/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report
