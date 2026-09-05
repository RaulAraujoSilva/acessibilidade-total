# Aplicação de documentos acessíveis

Protótipo de pesquisa derivado da skill Acessibilidade Total. Recebe DOCX, PPTX, PDF digital, TXT e Markdown; permite conferir a extração, escolher recursos e gerar saídas para revisão. A skill e os comandos anteriores continuam disponíveis na raiz do repositório.

## Execução local

Requer Python 3.12. Em uma instalação de desenvolvimento:

```sh
python -m venv .venv
python -m pip install -r web/requirements.txt
python web/local.py migrate
python web/local.py runserver 127.0.0.1:8765
```

Ative o ambiente virtual antes de instalar e executar. Em outro terminal com o mesmo ambiente:

```sh
python web/local.py process_pending
```

`local.py` gera as chaves da aplicação em arquivo local ignorado pelo Git e usa SQLite e fila no banco para desenvolvimento. Os e-mails ficam em `web/private-mail/`; abra o link local para confirmar a conta. Essa modalidade **não deve ser exposta à Internet**. A porta padrão é 8765; se alterá-la, configure `SITE_URL` de forma correspondente.

O usuário cadastra sua chave OpenRouter na interface. Não existe chave de API compartilhada no código. A estimativa é aproximada, não um teto financeiro. Imagens e repetição podem alterar o consumo. A geração usa o modelo informado pelo usuário; entrada de imagem exige modelo com capacidade visual.

## Contêineres Linux

Copie `web/.env.example` para `.env` na raiz e preencha as credenciais localmente. Gere `DJANGO_SECRET_KEY` e uma chave Fernet com um gerador criptográfico; mantenha cópia segura da chave Fernet, pois perdê-la impede decifrar as chaves dos usuários. A senha de `DATABASE_URL` deve coincidir com `POSTGRES_PASSWORD`. Configure SMTP, domínio HTTPS e origem CSRF antes de exposição pública.

```sh
docker compose build
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py collectstatic --noinput
docker compose up -d
```

Web e workers precisam enxergar o mesmo volume privado de documentos. O Compose modela isso com `documents:/data`. Para arquivos estáticos, execute `collectstatic` no build/na inicialização da imagem usada pelo servidor, pois o comando em contêiner descartável não persiste `/app/staticfiles`. O script de entrada da imagem já faz essa coleta. Redis usa persistência AOF; limite de concorrência inicial é um processo por fila.

Os estados e etapas são persistidos no banco; mensagens Celery levam apenas os IDs do documento e da execução. O identificador da execução bloqueia publicação após cancelamento. Repetições transitórias usam espera progressiva. O comando `recover_jobs` republica trabalhos aguardando e retoma leases vencidos; execute sob supervisão ou agendamento da infraestrutura. Cancelamento interrompe entre etapas, não desfaz uma chamada já enviada ao provedor.

## Exportação e limites

LibreOffice no worker Linux exporta PDF marcado. O sistema relata presença de texto e pode executar veraPDF se instalado; o protótipo não oferece certificação automática. DOCX contém títulos, tabelas nativas e descrições; HTML oferece alternativa semântica. O PPTX é reconstruído em modelo próprio e submetido ao auditor da skill quando disponível.

Não há OCR. Tabelas complexas, equações, notas, cabeçalhos e objetos flutuantes podem precisar de correção na origem. O PDF digital pode perder estrutura de tabela na extração. Cores de figuras originais não são corrigidas automaticamente. Textos alternativos gerados e simplificações exigem revisão contextual. O relatório separa alterações, perdas numéricas e equivalência semântica não verificada.

## Libras

O adaptador `studio/libras.py` usa player Linux diretamente, glosa por bloco e ffmpeg. Não usa seleção de texto, screenshots ou gravação do navegador. Configure `VLIBRAS_RENDERER`, `VLIBRAS_BUNDLES` e `VLIBRAS_BUNDLES_VERSION` com recursos instalados legalmente no worker. Xvfb e ffmpeg estão na imagem; player, avatares e sinais não são redistribuídos neste repositório.

A prova local com a imagem oficial `vlibras/vlibras-video-core:3.4.1` produziu 289 quadros a 25 fps em 22,94 segundos de renderização, para um vídeo de 11,56 segundos. É uma prova curta, não benchmark de produção ou validação linguística. `research/libras.md` registra procedência e limites. Sem o motor, a aplicação informa indisponibilidade e permite anexar vídeo revisado, sem considerar isso solução da geração automática.

## Segurança e infraestrutura

Chaves OpenRouter cifradas por Fernet com segredo separado do banco; consultas e downloads limitados ao proprietário; arquivos fora da pasta estática; limites de tamanho e expansão de ZIP; senhas com hash Django e confirmação de e-mail. Não registrar headers de autorização ou corpos de documentos em logs de produção. Backups, retenção, quotas de disco e monitoramento precisam ser configurados pelo operador antes de uso público.

Railway é o alvo considerado, seguindo sua [documentação Django](https://docs.railway.com/guides/django). A implantação está pendente: a credencial consultada não listou projetos acessíveis, não foi confirmado crédito e não se identificou SMTP existente. Não foram contratados planos. **O Compose não é um modelo Railway pronto**: volumes locais não devem ser presumidos compartilhados entre serviços Railway. É necessário provisionamento existente com armazenamento comum ou implementar armazenamento de objetos antes de separar serviços gerenciados.

## Verificação

```sh
python web/local.py test studio
```

Dezenove testes passaram no ambiente local, além de um ensaio real Celery/Redis e navegação de cadastro, confirmação e entrada. O corpus contém seis arquivos sintéticos e 36 medições; os resultados e limitações estão em `research/`. Nenhuma avaliação humana independente de Libras, compreensão ou preferência foi realizada. Testes em PostgreSQL, carga concorrente e implantação Docker ainda devem complementar a verificação local.
