import uuid
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

class User(AbstractUser):
    email=models.EmailField(unique=True)

def upload_path(instance, filename):
    from pathlib import Path
    return f'{instance.owner_id}/{instance.pk}/source{Path(filename).suffix.lower()}'

class ProviderKey(models.Model):
    owner=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ciphertext=models.TextField()
    updated_at=models.DateTimeField(auto_now=True)

class Document(models.Model):
    class Status(models.TextChoices):
        CREATED='created','Criado'
        QUEUED='queued','Aguardando'
        RUNNING='running','Processando'
        REVIEW='review','Aguardando revisão'
        DONE='done','Concluído'
        FAILED='failed','Falhou'
        CANCELLED='cancelled','Cancelado'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    source=models.FileField(upload_to=upload_path)
    original_name=models.CharField(max_length=255)
    content=models.JSONField(default=dict)
    options=models.JSONField(default=dict)
    status=models.CharField(max_length=12,choices=Status.choices,default=Status.CREATED)
    stage=models.CharField(max_length=80,default='Recebido')
    report=models.JSONField(default=dict)
    artifacts=models.JSONField(default=list)
    usage=models.JSONField(default=dict)
    estimate=models.JSONField(default=dict)
    model_id=models.CharField(max_length=200,blank=True)
    error=models.TextField(blank=True)
    task_id=models.CharField(max_length=100,blank=True)
    run_id=models.UUIDField(null=True,blank=True)
    heartbeat=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    reviewed_at=models.DateTimeField(null=True,blank=True)

class StageResult(models.Model):
    document=models.ForeignKey(Document,on_delete=models.CASCADE)
    fingerprint=models.CharField(max_length=64)
    name=models.CharField(max_length=100)
    result=models.JSONField(default=dict)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['document','fingerprint','name'],name='unique_document_stage')]

class AccessAttempt(models.Model):
    key=models.CharField(max_length=64,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True,db_index=True)
