<#
.SYNOPSIS
  Atualiza .gitignore (adiciona .venv, artifacts, .pytest_cache, etc.), remove
  do índice do Git os diretórios listados e faz commits das mudanças.

.NOTES
  - Execute na raiz do repositório.
  - Não reescreve histórico (safe).
  - Antes de rodar verifique que não há trabalho não comitado que você queira preservar.
  - Para executar, abra o PowerShell na pasta do repositório e rode:
      C:\Users\pcbar\IdeaProjects\DesafioQA_MobileBddAppiumPython\scripts\remove_venv_from_repo.ps1 -Push [-Push] [-Branch <branch>] [-BackupGitignore:$true|$false]
#>

param(
  [switch]$Push,                       # Se informado, faz 'git push' ao final (pergunta confirmação)
  [string]$Branch = "",                # Se informado, faz push para essa branch (default: ramo atual)
  [switch]$BackupGitignore = $true     # Faz backup do .gitignore existente
)

function FailIfNoGit {
  if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git não encontrado no PATH. Instale/Configure o Git e tente novamente."
    exit 1
  }
  if (-not (Test-Path ".git")) {
    Write-Error "Pasta .git não encontrada. Execute este script na raiz do repositório."
    exit 1
  }
}

function AddOrAppendGitignore {
  $patterns = @(
    "# Python virtualenv",
    ".venv/",
    "",
    "# VSCode",
    ".vscode/",
    "",
    "# Pytest / artifacts",
    ".pytest_cache/",
    "artifacts/",
    "",
    "# Python compiled",
    "__pycache__/",
    "*.pyc",
    "",
    "# System files",
    ".DS_Store",
    "Thumbs.db",
    "",
    "# Local env / logs",
    ".env",
    "*.log"
  )

  $gitignorePath = ".gitignore"
  if (Test-Path $gitignorePath) {
    if ($BackupGitignore) {
      $stamp = (Get-Date).ToString("yyyyMMdd-HHmmss")
      Copy-Item $gitignorePath "$gitignorePath.bak.$stamp"
      Write-Host "Backup do .gitignore criado: $gitignorePath.bak.$stamp"
    }

    $existing = Get-Content $gitignorePath -Raw
    $toAppend = @()
    foreach ($line in $patterns) {
      if ($line -eq "") { $toAppend += "" ; continue }
      if ($existing -notmatch [regex]::Escape($line)) {
        $toAppend += $line
      }
    }
    if ($toAppend.Count -gt 0) {
      Add-Content -Path $gitignorePath -Value "`n# ---- auto-added by remove_venv_from_repo.ps1 ----"
      Add-Content -Path $gitignorePath -Value ($toAppend -join "`n")
      Write-Host "Entradas relevantes adicionadas ao .gitignore"
    } else {
      Write-Host "Nenhuma entrada nova necessária no .gitignore"
    }
  } else {
    $patterns -join "`n" | Out-File -FilePath $gitignorePath -Encoding UTF8
    Write-Host ".gitignore criado com conteúdo padrão"
  }
}

function GitRemoveCachedPaths {
  $targets = @(".venv", "artifacts", ".pytest_cache", "__pycache__")
  $anyRemoved = $false

  foreach ($t in $targets) {
    # Verifica se há arquivos rastreados sob o caminho
    $tracked = git ls-files --error-unmatch -- "$t" 2>$null
    if ($LASTEXITCODE -eq 0 -or (git ls-files -- "$t" | Select-String "." -Quiet)) {
      Write-Host "Removendo rastreamento de: $t"
      git rm -r --cached --ignore-unmatch "$t" | Write-Output
      $anyRemoved = $true
    } else {
      Write-Host "Nenhum arquivo rastreado encontrado em: $t"
    }
  }

  # Remove arquivos .pyc que possam estar no índice
  Write-Host "Removendo arquivos *.pyc e __pycache__ rastreados (se existirem)"
  git ls-files '*.pyc' > $null 2>&1
  if ($LASTEXITCODE -eq 0) {
    git rm --cached -r --ignore-unmatch '*.pyc' | Write-Output
    $anyRemoved = $true
  }

  return $anyRemoved
}

# Execução
FailIfNoGit

Write-Host "1) Atualizando .gitignore..."
AddOrAppendGitignore

# Commit .gitignore se houve mudança
git add .gitignore
$diffIndex = git diff --cached --name-only
if ($diffIndex -match "\.gitignore") {
  git commit -m "chore: atualizar .gitignore para ignorar .venv, artifacts, caches e arquivos locais"
  Write-Host "Commit do .gitignore realizado."
} else {
  Write-Host "Nenhuma alteração a commitar no .gitignore."
}

Write-Host "2) Removendo do índice (git rm --cached) os diretórios/arquivos indicados..."
$removed = GitRemoveCachedPaths

if ($removed) {
  git commit -m "chore: remover .venv, artifacts e caches do versionamento (mantidos localmente)"
  Write-Host "Commit das remoções realizado."
} else {
  Write-Host "Nada para remover do índice (já não estavam rastreados)."
}

# Mostrar status e arquivos ignorados
Write-Host "`n== git status =="
git status --short
Write-Host "`n== Arquivos atualmente ignorados (exemplos) =="
git ls-files --others --ignored --exclude-standard | Select-Object -First 40 | ForEach-Object { Write-Host $_ }

if ($Push) {
  $branchToPush = $Branch
  if (-not $branchToPush) {
    $branchToPush = (git rev-parse --abbrev-ref HEAD).Trim()
  }
  Write-Host "`nDeseja realmente executar 'git push origin/$branchToPush'? (s/N)"
  $confirm = Read-Host
  if ($confirm -match '^[sS]') {
    git push origin $branchToPush
    Write-Host "Push concluído para origin/$branchToPush"
  } else {
    Write-Host "Push cancelado pelo usuário."
  }
} else {
  Write-Host "`nExecução finalizada. Se quiser enviar as mudanças, rode: git push origin <branch>"
}

Write-Host "´nPronto. Verifique o repositório remoto e peça aos outros colaboradores que façam git pull.`n"
# Fim do script
