param(
    [Parameter(Mandatory = $false)]
    [string]$Root = "D:\Codex",

    [Parameter(Mandatory = $false)]
    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

$repoNames = @(
    "dicom-dose-audit",
    "dicom-privacy-auditor",
    "rad-ai-sentinel",
    "rad-device-watch",
    "rad-followup-auditor",
    "rad-peer-review-analytics",
    "rad-report-lint",
    "radlex-order-harmonizer",
    "radscan-lite",
    "tcia-cohort-forge"
)

$files = @{
    ".github/dependabot.yml" = @'
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
'@
    ".github/workflows/codeql.yml" = @'
name: "CodeQL"

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
  schedule:
    - cron: "0 0 * * 1"

jobs:
  analyze:
    name: Analyze Python
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      packages: read
      actions: read
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/analyze@v3
'@
    ".github/workflows/dependency-review.yml" = @'
name: "Dependency Review"

on:
  pull_request:

permissions:
  contents: read
  pull-requests: write

jobs:
  dependency-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4
'@
    ".github/ISSUE_TEMPLATE/bug_report.yml" = @'
name: Bug Report
description: Report a bug or unexpected behavior
labels: ["bug"]
body:
  - type: textarea
    id: description
    attributes:
      label: Description
      description: What happened? What did you expect?
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: Reproduction Steps
      description: Steps, input data, commands to reproduce
  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: OS, Python version, package version
'@
    ".github/ISSUE_TEMPLATE/feature_request.yml" = @'
name: Feature Request
description: Suggest an enhancement
labels: ["enhancement"]
body:
  - type: textarea
    id: problem
    attributes:
      label: Problem / Motivation
      description: What gap or need does this address?
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: Proposed Solution
      description: How would you like it to work?
'@
    ".github/PULL_REQUEST_TEMPLATE.md" = @'
## Description

<!-- What does this PR do? -->

## Related Issue

<!-- Closes #... -->

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Improvement / refactor
- [ ] Documentation
- [ ] Validation / testing

## Checklist

- [ ] Tests pass
- [ ] Lint passes (`ruff check`)
- [ ] Type checks pass (`mypy src`)
- [ ] CHANGELOG.md updated
'@
}

foreach ($repoName in $repoNames) {
    $repo = Join-Path $Root $repoName
    if (-not (Test-Path (Join-Path $repo ".git"))) {
        Write-Host "skip ${repoName}: not a git repo"
        continue
    }

    foreach ($relative in $files.Keys) {
        $target = Join-Path $repo $relative
        if ($relative -eq ".github/workflows/codeql.yml") {
            $workflowDir = Join-Path $repo ".github/workflows"
            $existingCodeql = @()
            if (Test-Path $workflowDir) {
                $existingCodeql = Get-ChildItem -Path $workflowDir -Filter "*.yml" |
                    Where-Object {
                        (Get-Content -Raw $_.FullName) -match "github/codeql-action"
                    }
            }
            if ($existingCodeql.Count -gt 0 -and -not $Overwrite) {
                Write-Host "keep $repoName/codeql: existing CodeQL workflow"
                continue
            }
        }
        if ((Test-Path $target) -and -not $Overwrite) {
            Write-Host "keep $repoName/$relative"
            continue
        }
        $parent = Split-Path -Parent $target
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
        Set-Content -Path $target -Value $files[$relative] -Encoding UTF8
        Write-Host "write $repoName/$relative"
    }
}
