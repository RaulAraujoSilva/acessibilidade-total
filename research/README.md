# Pesquisa e reprodução

Ensaio exploratório realizado em 5 de setembro de 2026. Os seis documentos de `corpus/` são sintéticos e redistribuíveis sob a licença MIT do projeto. PDFs de artigos, normas licenciadas, documentos de usuários, vídeos e assets de terceiros não estão neste repositório. As referências apontam para as fontes originais; a matriz distingue fontes com leitura integral e registros pendentes.

## Reproduzir

Instale `research/requirements.txt` em Python 3.12 e configure `OPENROUTER_API_KEY` no ambiente, sem incluí-la em comandos salvos ou no Git. Instale LibreOffice para exportação PDF. Em Windows, o exportador também aceita `LIBREOFFICE_WSL_DISTRO` com uma distribuição que tenha LibreOffice instalado.

```sh
python research/evaluate.py
python research/audit.py
```

O primeiro comando faz chamadas reais cobradas pelo OpenRouter, usando `openai/gpt-4.1-mini`, temperatura zero e prompt versão 1. Consulta os preços disponíveis e interrompe novas chamadas após ultrapassar US$ 0,50 de consumo informado; isso não é um teto garantido por transação ou por saldo. Resultados são gravados em `research/evaluation-output/`, ignorado pelo Git. Execuções já existentes são retomadas. Para novo ensaio frio, mova esse diretório para outro local antes de executar; não misture resultados de versões distintas.

`results/` preserva as 36 medições observadas, o texto extraído das saídas e verificações estruturais. O total registrado foi US$ 0,01220472, com 84 chamadas. Os tempos dependem do ambiente, rede e provedor. O serviço pode atualizar o modelo; temperatura zero não garante reprodução textual idêntica.

## Desenho e limites

São dois cenários em DOCX, PPTX e PDF, três estratégias e duas repetições. A apresentação única exporta uma visão integral; as outras exportam a integral e uma adaptação com simplificação e descrição de imagens. A estratégia especializada regenera nas duas repetições; a base adaptável reaproveita cache na segunda. Essa política é deliberada: a diferença mede o trabalho executado e o reaproveitamento, **não uma superioridade intrínseca da arquitetura**. Versões especializadas também poderiam usar cache. O ensaio não controla tarefas equivalentes entre todos os braços.

A auditoria verifica números previamente definidos e releitura de texto do DOCX entregue. Não prova equivalência semântica. Presença de marcação e árvore de estrutura nos 36 PDFs não significa aprovação em PDF/UA ou WCAG. As tabelas dos PDFs de entrada não são reconstruídas semanticamente pelo importador. Não houve teste com pessoas cegas, surdas ou com deficiência cognitiva.

Os tempos preservados correspondem à execução original. Depois dela, ajustes na exportação PPTX corrigiram idioma e apresentação de tabelas; seis saídas foram auditadas novamente. O exemplo P1 único passou de sete erros para zero, mantendo avisos e itens não verificados. Não se substituíram tempos antigos por estimativas do código modificado.

O ensaio de atualização altera 30 para 45 dias e detecta que uma saída antiga está desatualizada. Não mede propagação completa de atualizações. Os 19 testes da aplicação cobrem falhas e isolamento local, incluindo lease e recuperação de Libras; um ensaio adicional executou Celery e Redis reais com SQLite. PostgreSQL, carga, memória e revisão humana continuam pendentes.

Veja [Libras](libras.md), [protocolo](protocolo.md), [buscas](registro-buscas.md), [matriz](matriz-evidencias.md) e [roteiro de revisão externa](roteiro-revisao-externa.md).
