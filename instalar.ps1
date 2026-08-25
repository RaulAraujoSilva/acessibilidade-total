<#
.SINOPSE
    Prepara o ambiente da skill acessibilidade-total no Windows.

.DESCRICAO
    Cria um ambiente Python isolado dentro da propria pasta (.venv), instala as
    bibliotecas e, se voce quiser, instala as ferramentas de auditoria pelo
    winget. Nada de sistema e instalado sem voce confirmar.

.EXEMPLO
    .\instalar.ps1                    # bibliotecas Python, e pergunta o resto
    .\instalar.ps1 -SomenteAuditor    # o minimo para auditar um .pptx
    .\instalar.ps1 -Tudo -SemPerguntar
#>
[CmdletBinding()]
param(
    [switch]$SomenteAuditor,
    [switch]$Tudo,
    [switch]$SemPerguntar
)

$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $raiz

function Titulo($t) {
    Write-Host ""
    Write-Host ("=" * 74) -ForegroundColor Cyan
    Write-Host " $t" -ForegroundColor Cyan
    Write-Host ("=" * 74) -ForegroundColor Cyan
}
function Passo($t) { Write-Host "  -> $t" -ForegroundColor White }
function Ok($t)    { Write-Host "  [ok] $t" -ForegroundColor Green }
function Aviso($t) { Write-Host "  [!]  $t" -ForegroundColor Yellow }
function Erro($t)  { Write-Host "  [x]  $t" -ForegroundColor Red }

function Confirmar($pergunta) {
    if ($SemPerguntar) { return $Tudo.IsPresent }
    $r = Read-Host "$pergunta [s/N]"
    return ($r -match '^[sSyY]')
}

Titulo "acessibilidade-total - instalacao"

# ---------------------------------------------------------------- Python ---
Passo "Procurando o Python..."
$python = $null
foreach ($cmd in @('py -3', 'python', 'python3')) {
    try {
        $exe, $arg = $cmd.Split(' ', 2)
        $v = & $exe $arg --version 2>&1
        if ($LASTEXITCODE -eq 0) { $python = $cmd; break }
    } catch { }
}

if (-not $python) {
    Erro "Python nao encontrado."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        if (Confirmar "    Instalar o Python 3.12 agora pelo winget?") {
            winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
            Aviso "Feche e reabra o terminal e rode este script de novo."
        }
    } else {
        Aviso "Baixe em https://www.python.org/downloads/ e marque 'Add to PATH'."
    }
    exit 1
}
Ok "Python encontrado ($python)"

# ------------------------------------------------------------------ venv ---
$venv = Join-Path $raiz '.venv'
if (-not (Test-Path $venv)) {
    Passo "Criando o ambiente isolado em .venv (nao mexe no Python do sistema)..."
    $exe, $arg = $python.Split(' ', 2)
    if ($arg) { & $exe $arg -m venv $venv } else { & $exe -m venv $venv }
}
$pip = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $pip)) { Erro "Falha ao criar o .venv."; exit 1 }
Ok "Ambiente isolado pronto"

# ------------------------------------------------------------ bibliotecas ---
Passo "Instalando as bibliotecas Python..."
& $pip -m pip install --upgrade pip --quiet
if ($SomenteAuditor) {
    & $pip -m pip install "python-pptx>=1.0.2" --quiet
    Ok "Instalado o minimo para auditar (python-pptx)"
} else {
    & $pip -m pip install -r (Join-Path $raiz 'requirements.txt') --quiet
    Ok "Bibliotecas instaladas"
}

# ------------------------------------------------- navegador do Playwright ---
if (-not $SomenteAuditor) {
    if ($Tudo -or (Confirmar "  Baixar o Chromium do Playwright (~130 MB, so para a janela de Libras)?")) {
        Passo "Baixando o Chromium..."
        & $pip -m playwright install chromium
        Ok "Chromium instalado"
    }
}

# -------------------------------------------------- ferramentas de sistema ---
if (-not $SomenteAuditor) {
    Titulo "Ferramentas de auditoria (opcionais)"
    Write-Host @"
  Nenhuma delas e necessaria para CRIAR a apresentacao nem para rodar a
  auditoria automatica. Cada uma cobre um pedaco a mais:

    PAC          confere o PDF exportado pelo Protocolo Matterhorn
    CCA          conta-gotas de contraste, para os casos que o auditor
                 marca como indeterminado (texto sobre foto)
    veraPDF      valida o PDF contra a ISO 14289 - via Docker, sem Java
    NVDA         leitor de tela. OPCIONAL e usado so como INSTRUMENTO DE
                 MEDIDA: e a evidencia da regra K03. Voce nao precisa
                 ouvir nada - NVDA+S silencia e o Speech Viewer mostra em
                 texto, na tela, tudo o que seria falado.
"@ -ForegroundColor Gray

    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Aviso "winget nao encontrado; instale as ferramentas manualmente."
    } else {
        $pacotes = @(
            @{ Id = 'axes4.PAC';  Nome = 'PAC (PDF Accessibility Checker)' },
            @{ Id = 'TPGi.CCAe';  Nome = 'Colour Contrast Analyser' }
        )
        foreach ($p in $pacotes) {
            if ($Tudo -or (Confirmar "  Instalar $($p.Nome)?")) {
                Passo "Instalando $($p.Nome)..."
                winget install --id $p.Id -e --accept-source-agreements --accept-package-agreements
            }
        }

        Write-Host ""
        Aviso "O NVDA e um leitor de tela: ao abrir, ele fala em voz alta e passa"
        Aviso "a controlar a navegacao pelo teclado. Para sair: Insert+Q."
        if ($Tudo -or (Confirmar "  Instalar o NVDA mesmo assim?")) {
            winget install --id NVAccess.NVDA -e --accept-source-agreements --accept-package-agreements
            Write-Host ""
            Aviso "Para usar como instrumento de medida, sem audio:"
            Write-Host "    1. Abra o NVDA e pressione NVDA+S ate ouvir/ver 'sem fala'" -ForegroundColor Gray
            Write-Host "    2. Menu do NVDA > Ferramentas > Visualizador de Fala" -ForegroundColor Gray
            Write-Host "    3. Para gravar em arquivo, instale o complemento Speech Logger" -ForegroundColor Gray
            Write-Host "       em https://addons.nvda-project.org/addons/speechLogger.en.html" -ForegroundColor Gray
        }
    }

    if (Get-Command docker -ErrorAction SilentlyContinue) {
        if ($Tudo -or (Confirmar "  Baixar a imagem Docker do veraPDF (~500 MB, dispensa Java)?")) {
            Passo "Baixando verapdf/cli..."
            docker pull verapdf/cli
        }
    } else {
        Aviso "Docker ausente: o veraPDF ficara indisponivel (regra L07 nao verificada)."
    }
}

# ------------------------------------------------------------- verificacao ---
Titulo "Verificando o que ficou instalado"
& $pip (Join-Path $raiz 'scripts\verificar_ambiente.py')

Titulo "Pronto"
Write-Host @"
  Para auditar uma apresentacao:

      .\auditar.bat caminho\do\arquivo.pptx

  ou arraste o .pptx para cima do auditar.bat.

  Para ver o que um leitor de tela anunciaria:

      .venv\Scripts\python.exe scripts\simular_leitura.py arquivo.pptx
"@ -ForegroundColor Gray
Write-Host ""
