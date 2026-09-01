param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$errors = [System.Collections.Generic.List[string]]::new()

function Expected-Ids([string]$Prefix, [int]$Start, [int]$End) {
    $Start..$End | ForEach-Object { '{0}-{1:D3}' -f $Prefix, $_ }
}

function Compare-Ids([string]$Label, [string[]]$Actual, [string[]]$Expected) {
    $actualUnique = @($Actual | Sort-Object -Unique)
    $duplicates = @($Actual | Group-Object | Where-Object Count -gt 1 | ForEach-Object Name)
    $missing = @($Expected | Where-Object { $_ -notin $actualUnique })
    $extra = @($actualUnique | Where-Object { $_ -notin $Expected })
    if ($duplicates) { $errors.Add("$Label duplicate IDs: $($duplicates -join ', ')") }
    if ($missing) { $errors.Add("$Label missing IDs: $($missing -join ', ')") }
    if ($extra) { $errors.Add("$Label extra IDs: $($extra -join ', ')") }
}

function Expand-CitedIds([string]$Value, [string]$Prefix) {
    $ids = [System.Collections.Generic.List[string]]::new()
    foreach ($match in [regex]::Matches($Value, "${Prefix}-(\d{3})\s+through\s+${Prefix}-(\d{3})")) {
        [int]$start = $match.Groups[1].Value
        [int]$end = $match.Groups[2].Value
        foreach ($id in (Expected-Ids $Prefix $start $end)) { $ids.Add($id) }
    }
    $withoutRanges = [regex]::Replace($Value, "${Prefix}-(\d{3})\s+through\s+${Prefix}-(\d{3})", '')
    foreach ($match in [regex]::Matches($withoutRanges, "${Prefix}-\d{3}")) { $ids.Add($match.Value) }
    @($ids | Sort-Object -Unique)
}

$sourcePath = Join-Path $ProjectRoot 'docs/baird/SOURCE_COVERAGE.csv'
$matrixPath = Join-Path $ProjectRoot 'docs/baird/BAIRD_CONTROL_HANDOFF_MATRIX.md'
$citationPath = Join-Path $ProjectRoot 'docs/baird/CONTROL_EVIDENCE_CITATIONS.csv'
$fixturePath = Join-Path $ProjectRoot 'docs/baird/evidence/FIXTURE_ALLOCATION.md'

$sources = @(Import-Csv $sourcePath)
if ($sources.Count -ne 58) { $errors.Add("SOURCE_COVERAGE row count is $($sources.Count), expected 58") }
$requiredColumns = @('source_id','disposition','baird_control','i2r_requirement','component_integration','acceptance_test','stop_gate','owner')
foreach ($row in $sources) {
    foreach ($column in $requiredColumns) {
        if ([string]::IsNullOrWhiteSpace($row.$column)) { $errors.Add("$($row.source_id) has blank $column") }
    }
}
Compare-Ids 'Source IDs' @($sources.source_id) (Expected-Ids 'SRC' 1 58)
Compare-Ids 'Source requirement IDs' @($sources.i2r_requirement) (Expected-Ids 'R' 39 96)
$sourceTests = @($sources.acceptance_test | ForEach-Object { ([regex]::Match($_, 'T-\d{3}')).Value })
Compare-Ids 'Source test IDs' $sourceTests (Expected-Ids 'T' 39 96)

$matrixRows = @(Get-Content $matrixPath | Where-Object { $_ -match '^\| `(ADR|BG|THR)-\d{3}`' })
$matrixControls = @($matrixRows | ForEach-Object { ([regex]::Match($_, '(ADR|BG|THR)-\d{3}')).Value })
Compare-Ids 'ADR controls' @($matrixControls | Where-Object { $_ -like 'ADR-*' }) (Expected-Ids 'ADR' 1 12)
Compare-Ids 'BG controls' @($matrixControls | Where-Object { $_ -like 'BG-*' }) (Expected-Ids 'BG' 1 8)
Compare-Ids 'THR controls' @($matrixControls | Where-Object { $_ -like 'THR-*' }) (Expected-Ids 'THR' 1 18)
$matrixRequirements = @($matrixRows | ForEach-Object { ([regex]::Match($_, '(?<![A-Z])R-\d{3}')).Value })
$matrixTests = @($matrixRows | ForEach-Object { ([regex]::Match($_, 'T-\d{3}')).Value })
Compare-Ids 'Control requirement IDs' $matrixRequirements (Expected-Ids 'R' 1 38)
Compare-Ids 'Control test IDs' $matrixTests (Expected-Ids 'T' 1 38)

$allRequirements = (Expected-Ids 'R' 1 96)
$allTests = (Expected-Ids 'T' 1 96)
$citations = @(Import-Csv $citationPath)
foreach ($citation in $citations) {
    if ([string]::IsNullOrWhiteSpace($citation.finding_id) -or [string]::IsNullOrWhiteSpace($citation.proof_relation)) {
        $errors.Add('A control evidence citation lacks finding_id or proof_relation')
        continue
    }
    foreach ($id in (Expand-CitedIds $citation.requirement_ids 'R')) {
        if ($id -notin $allRequirements) { $errors.Add("$($citation.finding_id) cites unknown $id") }
    }
    foreach ($id in (Expand-CitedIds $citation.test_ids 'T')) {
        if ($id -notin $allTests) { $errors.Add("$($citation.finding_id) cites unknown $id") }
    }
}

$fixtureIds = [regex]::Matches((Get-Content -Raw $fixturePath), 'FX-\d{3}') | ForEach-Object Value | Sort-Object -Unique
Compare-Ids 'Fixture allocation IDs' @($fixtureIds) (Expected-Ids 'FX' 1 30)

$scanRoots = @('README.md','AGENTS.md','docs','research','scripts') | ForEach-Object { Join-Path $ProjectRoot $_ }
$dashMatches = @(& rg -n --pcre2 '[\x{2010}-\x{2015}]' @scanRoots 2>$null)
if ($dashMatches) { $errors.Add("Prohibited Unicode dash matches: $($dashMatches.Count)") }

if ($errors.Count) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output 'BAIRD_TRACEABILITY_VALID=True'
Write-Output 'SOURCE_ROWS=58'
Write-Output 'CONTROL_IDS=ADR12,BG8,THR18'
Write-Output 'REQUIREMENT_IDS=R001-R096'
Write-Output 'TEST_IDS=T001-T096'
Write-Output 'FIXTURE_IDS=FX001-FX030'
Write-Output 'PROHIBITED_UNICODE_DASHES=0'
