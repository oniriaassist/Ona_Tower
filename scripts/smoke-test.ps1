$ErrorActionPreference = "Stop"

$Backend = "http://127.0.0.1:8400"
$Frontend = "http://127.0.0.1:3010"

Write-Host "ONA Towers local smoke test" -ForegroundColor Cyan
Write-Host ""

$health = Invoke-RestMethod "$Backend/health"
if ($health.status -ne "ok") {
    throw "Backend health check did not return status=ok."
}
Write-Host "[PASS] Backend health: $Backend/health" -ForegroundColor Green

$root = Invoke-RestMethod "$Backend/"
if ($root.status -ne "ok") {
    throw "Backend root did not return status=ok."
}
Write-Host "[PASS] Backend root: $Backend/" -ForegroundColor Green

$residences = Invoke-RestMethod "$Backend/api/residences"
$expected = @{
    "2-bedroom" = 202
    "3-bedroom" = 236
    "penthouse-3bed" = 419
    "penthouse-4bed" = 487
}

foreach ($slug in $expected.Keys) {
    $item = $residences | Where-Object { $_.slug -eq $slug } | Select-Object -First 1
    if (-not $item) {
        throw "Missing residence from API: $slug"
    }
    if ([double]$item.size_m2 -ne [double]$expected[$slug]) {
        throw "Residence $slug has size_m2=$($item.size_m2); expected $($expected[$slug]). Run .\scripts\migrate-database.ps1 again."
    }
}
Write-Host "[PASS] Residence API uses corrected project data" -ForegroundColor Green

$home = Invoke-WebRequest "$Frontend/"
if ($home.StatusCode -ne 200) {
    throw "Frontend homepage returned HTTP $($home.StatusCode)."
}
Write-Host "[PASS] Frontend homepage: $Frontend/" -ForegroundColor Green

$admin = Invoke-WebRequest "$Frontend/admin"
if ($admin.StatusCode -ne 200) {
    throw "Admin route returned HTTP $($admin.StatusCode)."
}
Write-Host "[PASS] Admin route: $Frontend/admin" -ForegroundColor Green

$proxiedHealth = Invoke-RestMethod "$Frontend/health"
if ($proxiedHealth.status -ne "ok") {
    throw "Vite -> FastAPI health proxy failed."
}
Write-Host "[PASS] Frontend proxy -> backend" -ForegroundColor Green

$proxiedResidences = Invoke-RestMethod "$Frontend/api/residences"
if ($proxiedResidences.Count -lt 4) {
    throw "Frontend /api proxy did not return the expected residence collection."
}
Write-Host "[PASS] Frontend /api proxy" -ForegroundColor Green

Write-Host ""
Write-Host "ALL LOCAL CHECKS PASSED" -ForegroundColor Cyan
Write-Host "Homepage: $Frontend/"
Write-Host "Admin:    $Frontend/admin"
Write-Host "API docs: $Backend/docs"
