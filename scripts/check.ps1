$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

Push-Location $projectRoot
try {
    uv run ruff check backend tests scripts ops
    if ($LASTEXITCODE -ne 0) { throw "Python lint failed." }
    uv run mypy
    if ($LASTEXITCODE -ne 0) { throw "Python strict typing failed." }
    uv run pytest
    if ($LASTEXITCODE -ne 0) { throw "Python tests failed." }

    Push-Location (Join-Path $projectRoot "frontend")
    try {
        npm run lint
        if ($LASTEXITCODE -ne 0) { throw "Frontend lint failed." }
        npm run typecheck
        if ($LASTEXITCODE -ne 0) { throw "Frontend strict typing failed." }
        npm run test
        if ($LASTEXITCODE -ne 0) { throw "Frontend tests failed." }
        npm run build
        if ($LASTEXITCODE -ne 0) { throw "Frontend production build failed." }
        npm run test:e2e
        if ($LASTEXITCODE -ne 0) { throw "Frontend browser and accessibility tests failed." }
    }
    finally {
        Pop-Location
    }

    $dashMatches = rg -n -P "[\x{2010}-\x{2015}]" . `
        -g "!.venv/**" `
        -g "!frontend/node_modules/**" `
        -g "!research/**" `
        -g "!*.sha256"
    if ($LASTEXITCODE -eq 0) {
        $dashMatches
        throw "Prohibited Unicode dash characters found."
    }
    if ($LASTEXITCODE -ne 1) {
        throw "Unicode scan failed to execute."
    }

    $global:LASTEXITCODE = 0
}
finally {
    Pop-Location
}
