# Implantação em VPS

O protótipo público usa uma VPS Ubuntu 24.04 já existente, com Docker Compose, Caddy e HTTPS. Nenhum plano Railway foi contratado ou ampliado. O endereço provisório utiliza DNS sslip.io; um domínio próprio pode substituí-lo alterando `SITE_HOST`, `SITE_URL`, `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`.

O arquivo `compose.vps.yaml` mantém PostgreSQL, Redis, aplicação, recuperação de etapas, worker documental, worker de Libras e núcleo de tradução em serviços separados. Apenas Caddy publica portas (80 e 443). Os arquivos ficam no volume `documents`, compartilhado no mesmo host. Os limites dos contêineres protegem a capacidade da VPS; não são uma medição de consumo.

## Configuração

Instale Docker Engine e Compose pelo repositório oficial ou pelos pacotes da distribuição. Crie em `deploy/`, fora do Git:

- `.env`: variáveis de `web/.env.example`, `DEBUG=0`, URL pública, PostgreSQL, Redis, chave de cifragem e segredo Django independentes. Use `PRIVATE_MEDIA_ROOT=/data` e `TRUST_PROXY_CLIENT_IP=1` somente com o Caddy fornecido e porta web privada.
- `postgres.env`: `POSTGRES_USER=acessibilidade`, `POSTGRES_DB=acessibilidade` e senha aleatória correspondente à URL do banco.
- `proxy.env`: `SITE_HOST` com o domínio que aponta para a VPS.

Para e-mail, configure SMTP ou `EMAIL_BACKEND=studio.mail.GmailBackend` com `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN` e `DEFAULT_FROM_EMAIL` de uma conta Google autorizada para `gmail.send`. Não publique esses arquivos. Restrinja permissões locais a `600` e preserve uma cópia segura da chave de cifragem separada do backup do banco.

O player oficial deve ser instalado privadamente em `deploy/runtime/player`, com seu diretório de dados. Configure `VLIBRAS_RENDERER=/opt/vlibras/VLibras-Video.x86_64`, `VLIBRAS_BUNDLES=/data/vlibras-bundles`, `VLIBRAS_BUNDLES_VERSION=2018.3.1-LINUX` e `VLIBRAS_FETCH_BUNDLES=1`. Código, avatar e sinais têm verificações de licença distintas; este repositório não redistribui esses ativos.

```sh
docker compose -f deploy/compose.vps.yaml build web
docker compose -f deploy/compose.vps.yaml up -d postgres redis gloss
docker compose -f deploy/compose.vps.yaml run --rm web python manage.py migrate --noinput
docker compose -f deploy/compose.vps.yaml run --rm web mkdir -p /data/vlibras-bundles
docker compose -f deploy/compose.vps.yaml up -d --no-build
docker compose -f deploy/compose.vps.yaml exec web python manage.py check --deploy
```

O núcleo `vlibras-translator-text-core:4.2.0` executa a tradução baseada em regras por uma interface HTTP interna. O endpoint público de glosa retornou HTTP 403 a partir desta VPS; a implantação própria usa o código aberto, sem contornar o bloqueio do serviço. O núcleo não é exposto na internet. O download dos bundles continua dependendo do repositório oficial. A tradução e os vídeos exigem revisão linguística.

Após corrigir uma indisponibilidade de infraestrutura, o operador pode retomar somente Libras, preservando saídas documentais e histórico:

```sh
docker compose -f deploy/compose.vps.yaml exec web python manage.py retry_libras ID_DO_DOCUMENTO
```

## Operação e limites

Use `docker compose ... logs --tail 50 SERVICO` para diagnóstico e `restart SERVICO` para reinício. Não use `down -v` em uma instalação com dados: isso exclui os volumes. Os contêineres reiniciam automaticamente e o processo `recovery` procura etapas interrompidas a cada minuto. A política depende dos tempos de lease documentados no núcleo.

A implantação é de pesquisa, em um único host. Não há alta disponibilidade, política automática de backup externo ou ensaio de recuperação de desastre. Preserve backups coordenados do PostgreSQL e dos documentos, com retenção definida pelo operador. Não exponha o Docker socket, banco, Redis ou núcleo de glosa. O envio de e-mail deve ser restrito a mensagens transacionais; o adaptador não cria uma API pública de envio genérico.

Railway continua possível com a imagem da aplicação, PostgreSQL, Redis e armazenamento comum apropriado. Volumes Railway não são compartilhados entre serviços; o `compose.vps.yaml` não pode ser reproduzido literalmente como serviços Railway independentes sem adaptar o armazenamento. Verifique orçamento antes de criar recursos cobrados por uso.

Fontes técnicas: [Docker](https://docs.docker.com/engine/install/ubuntu/), [Caddy](https://caddyserver.com/docs/automatic-https), [núcleo VLibras](https://github.com/spbgovbr-vlibras/vlibras-translator-text-core), [Gmail API](https://developers.google.com/workspace/gmail/api/guides/sending), [volumes Railway](https://docs.railway.com/volumes).
