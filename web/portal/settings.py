import os
from pathlib import Path
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR=Path(__file__).resolve().parent.parent
DEBUG=os.environ.get('DEBUG','0')=='1'
SECRET_KEY=os.environ.get('DJANGO_SECRET_KEY','')
if not SECRET_KEY:
    if not DEBUG: raise ImproperlyConfigured('Configure DJANGO_SECRET_KEY fora do repositório.')
    SECRET_KEY='development-only-not-for-public-hosting'
ALLOWED_HOSTS=os.environ.get('ALLOWED_HOSTS','localhost,127.0.0.1,testserver').split(',')
CSRF_TRUSTED_ORIGINS=[x for x in os.environ.get('CSRF_TRUSTED_ORIGINS','').split(',') if x]
INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','studio']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='portal.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='portal.wsgi.application'
DATABASES={'default':dj_database_url.config(default='sqlite:///'+str(BASE_DIR/'local.sqlite3'),conn_max_age=60)}
LANGUAGE_CODE='pt-br';TIME_ZONE='America/Sao_Paulo';USE_I18N=True;USE_TZ=True
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
STATIC_URL='/static/';STATIC_ROOT=BASE_DIR/'staticfiles';STATICFILES_DIRS=[BASE_DIR/'static']
MEDIA_ROOT=Path(os.environ.get('PRIVATE_MEDIA_ROOT',str(BASE_DIR/'private-media')))
LOGIN_URL='/conta/entrar/';LOGIN_REDIRECT_URL='/documentos/';LOGOUT_REDIRECT_URL='/'
AUTH_USER_MODEL='studio.User'
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':12}},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
EMAIL_BACKEND=os.environ.get('EMAIL_BACKEND','django.core.mail.backends.filebased.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_FILE_PATH=BASE_DIR/'private-mail'
EMAIL_HOST=os.environ.get('EMAIL_HOST','');EMAIL_PORT=int(os.environ.get('EMAIL_PORT','587'))
EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER','');EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD','')
EMAIL_USE_TLS=os.environ.get('EMAIL_USE_TLS','1')=='1';EMAIL_TIMEOUT=15
DEFAULT_FROM_EMAIL=os.environ.get('DEFAULT_FROM_EMAIL','acessibilidade@localhost')
SITE_URL=os.environ.get('SITE_URL','http://127.0.0.1:8765').rstrip('/')
FERNET_KEY=os.environ.get('FERNET_KEY','')
CELERY_BROKER_URL=os.environ.get('REDIS_URL','redis://localhost:6379/0')
CELERY_TASK_ACKS_LATE=True;CELERY_TASK_REJECT_ON_WORKER_LOST=True
CELERY_WORKER_PREFETCH_MULTIPLIER=1
CELERY_TASK_DEFAULT_QUEUE='documents'
CELERY_TASK_ROUTES={'studio.tasks.render_libras':{'queue':'libras'}}
CELERY_BROKER_TRANSPORT_OPTIONS={'visibility_timeout':7200}
CELERY_TASK_TIME_LIMIT=6600
DISPATCH_MODE=os.environ.get('DISPATCH_MODE','celery')
if DISPATCH_MODE=='database' and not DEBUG:raise ImproperlyConfigured('Fila local permitida somente em desenvolvimento.')
SESSION_COOKIE_HTTPONLY=True;SESSION_COOKIE_SECURE=not DEBUG
CSRF_COOKIE_SECURE=not DEBUG;SECURE_SSL_REDIRECT=not DEBUG
SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
SECURE_HSTS_SECONDS=31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS=True;SECURE_HSTS_PRELOAD=True
DATA_UPLOAD_MAX_MEMORY_SIZE=55*1024*1024
FILE_UPLOAD_MAX_MEMORY_SIZE=2*1024*1024
MAX_UPLOAD_BYTES=50*1024*1024
