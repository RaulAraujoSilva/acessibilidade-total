from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import User,Document
from .content import SUPPORTED
from pathlib import Path

class SignupForm(UserCreationForm):
    email=forms.EmailField(label='E-mail')
    class Meta:
        model=User;fields=['email','password1','password2']
    def clean_email(self):
        email=self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():raise forms.ValidationError('Não foi possível usar este e-mail. Tente entrar ou recuperar sua senha.')
        return email
    def save(self,commit=True):
        user=super().save(False);user.username=self.cleaned_data['email'];user.email=user.username;user.is_active=False
        if commit:user.save()
        return user

class LoginForm(AuthenticationForm):
    username=forms.EmailField(label='E-mail')
    def clean_username(self):return self.cleaned_data['username'].strip().lower()

class KeyForm(forms.Form):
    key=forms.CharField(label='Chave OpenRouter',widget=forms.PasswordInput,strip=True,max_length=300)
    def clean_key(self):
        key=self.cleaned_data['key']
        if not key.startswith('sk-or-') or len(key)<20:raise forms.ValidationError('Informe uma chave OpenRouter válida.')
        return key

class UploadForm(forms.ModelForm):
    class Meta:
        model=Document;fields=['title','source'];labels={'title':'Título do documento','source':'Arquivo de origem'}
    def clean_source(self):
        file=self.cleaned_data['source']
        if Path(file.name).suffix.lower() not in SUPPORTED:raise forms.ValidationError('Use PPTX, DOCX, PDF digital, TXT ou Markdown.')
        if file.size>50*1024*1024:raise forms.ValidationError('Limite de 50 MB por documento.')
        return file

class OptionsForm(forms.Form):
    contrast=forms.BooleanField(label='Alto contraste',required=False)
    color_safe=forms.BooleanField(label='Conferir informação independente de cor (gráficos exigem revisão)',required=False,initial=True)
    simplify=forms.BooleanField(label='Simplificar a linguagem, preservando informações',required=False)
    describe=forms.BooleanField(label='Gerar descrições de imagens com IA',required=False)
    libras=forms.BooleanField(label='Gerar vídeos em Libras',required=False)
    pptx=forms.BooleanField(label='Gerar também apresentação PowerPoint',required=False)
    model_id=forms.CharField(label='Identificador do modelo OpenRouter',required=False,max_length=200,help_text='Necessário apenas para adaptações com IA. Para imagens, escolha um modelo com entrada visual.')
    consent=forms.BooleanField(label='Conferi a extração e autorizo o envio do conteúdo aos provedores selecionados quando necessário.')
    def clean(self):
        data=super().clean()
        if (data.get('simplify') or data.get('describe')) and not data.get('model_id'):self.add_error('model_id','Informe o modelo para usar IA.')
        return data

class VideoForm(forms.Form):
    block_id=forms.CharField(label='Identificador do bloco',max_length=30)
    video=forms.FileField(label='Vídeo MP4 revisado')
    review=forms.BooleanField(label='Confirmo que este vídeo foi revisado para o conteúdo do bloco indicado.')
    def clean_video(self):
        f=self.cleaned_data['video']
        if Path(f.name).suffix.lower()!='.mp4' or f.size>50*1024*1024:raise forms.ValidationError('Envie MP4 de até 50 MB.')
        header=f.read(16);f.seek(0)
        if b'ftyp' not in header:raise forms.ValidationError('O arquivo não foi reconhecido como MP4.')
        return f
