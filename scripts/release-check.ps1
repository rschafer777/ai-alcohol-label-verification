$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$validationRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("labelverify-release-" + [guid]::NewGuid().ToString("N"))

New-Item -ItemType Directory -Path $validationRoot | Out-Null
Push-Location $projectRoot
try {
    & (Join-Path $PSScriptRoot "check.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Code quality gate failed." }

    uv run python scripts/validate_product_corpus.py --output (Join-Path $validationRoot "product-corpus.json") --build-id local-release
    if ($LASTEXITCODE -ne 0) { throw "Governed product corpus failed." }

    uv run python scripts/run_performance_validation.py --output (Join-Path $validationRoot "performance.json")
    if ($LASTEXITCODE -ne 0) { throw "Warm and cold performance validation failed." }

    uv run python scripts/run_batch_performance_validation.py --count 20 --output (Join-Path $validationRoot "batch-performance.json")
    if ($LASTEXITCODE -ne 0) { throw "Sequential batch performance validation failed." }

    $testImageCount = @(Get-ChildItem tests/Test_Images -File -ErrorAction SilentlyContinue | Where-Object Extension -In '.jpg', '.jpeg', '.png', '.webp').Count
    if ($testImageCount -ge 50) {
        uv run python scripts/validate_test_images.py --json-output (Join-Path $validationRoot "test-images.json") --report-output (Join-Path $validationRoot "test-images.md")
        if ($LASTEXITCODE -ne 0) { throw "Governed 50-image validation failed." }
    }
    else {
        Write-Output "Governed raw-image validation skipped because public redistribution images are not installed."
    }

    uv run pip-audit --format json --output (Join-Path $validationRoot "pip-audit.json")
    if ($LASTEXITCODE -ne 0) { throw "Python dependency audit failed." }

    Push-Location (Join-Path $projectRoot "frontend")
    try {
        npm audit --omit=dev --audit-level=high
        if ($LASTEXITCODE -ne 0) { throw "Frontend production dependency audit failed." }
    }
    finally {
        Pop-Location
    }

    uv run python scripts/validate_release_manifest.py
    if ($LASTEXITCODE -ne 0) { throw "Release manifest validation failed." }

    Write-Output "LABELVERIFY_RELEASE_GATE=PASS"
    Write-Output "Temporary evidence: $validationRoot"
    $global:LASTEXITCODE = 0
}
finally {
    Pop-Location
}
