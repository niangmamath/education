<#
Create MinIO bucket (PowerShell)
Usage: run from repo root or infrastructure/scripts folder:
  .\infrastructure\scripts\create_minio_buckets.ps1

This script mirrors create_minio_buckets.sh behaviour for PowerShell users.
#>
Set-StrictMode -Version Latest

function Load-DotEnv {
    param([string]$Path = '.env')
    if (Test-Path $Path) {
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^[\s#]' -or $_ -match '^[\s]*$') { return }
            $parts = $_ -split '=', 2
            if ($parts.Length -eq 2) {
                $name = $parts[0].Trim()
                $value = $parts[1].Trim()
                if ($name -ne '') { Set-Item -Path Env:$name -Value $value }
            }
        }
    }
}

Load-DotEnv

# Prefer canonical S3 vars, fallback to MINIO_* for compatibility
$S3AccessKey = $Env:S3_ACCESS_KEY
if (-not $S3AccessKey) { $S3AccessKey = $Env:MINIO_ROOT_USER }
if (-not $S3AccessKey) { $S3AccessKey = 'minioadmin' }

$S3Secret = $Env:S3_SECRET_KEY
if (-not $S3Secret) { $S3Secret = $Env:MINIO_ROOT_PASSWORD }
if (-not $S3Secret) { $S3Secret = 'minioadmin' }

$S3Endpoint = $Env:S3_ENDPOINT
if (-not $S3Endpoint) { $S3Endpoint = 'http://minio:9000' }

$S3Bucket = $Env:S3_BUCKET
if (-not $S3Bucket) { $S3Bucket = 'studentconnect' }

# If endpoint points to localhost, use 'minio' hostname for container calls
$DOCKER_S3_ENDPOINT = $S3Endpoint
if ($DOCKER_S3_ENDPOINT -match '://(localhost|127\.0\.0\.1)') {
    $DOCKER_S3_ENDPOINT = $DOCKER_S3_ENDPOINT -replace '://(localhost|127\.0\.0\.1)', '://minio'
}

Write-Output "Detecting Docker network for Compose..."
$raw = & docker network ls --format "{{.Name}}" 2>$null
$networks = @()
if ($raw) { $networks = $raw -split "`n" | ForEach-Object { $_.Trim() } }
$NETWORK = $networks | Where-Object { $_ -match 'studentconnect_local$' } | Select-Object -First 1
if (-not $NETWORK) { $NETWORK = 'studentconnect_local' }
Write-Output "Using network: $NETWORK"

# Compose health URL (call minio container)
try {
    $uri = [System.Uri]$DOCKER_S3_ENDPOINT
    $port = $uri.Port
    $scheme = $uri.Scheme
} catch {
    $scheme = 'http'
    $port = 9000
}
$healthUrl = "$scheme://minio:$port/minio/health/ready"
Write-Output "Waiting for MinIO health endpoint: $healthUrl"

$ready = $false
for ($i=1; $i -le 30; $i++) {
    & docker run --network $NETWORK --rm curlimages/curl:latest -fsS $healthUrl > $null 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Output 'MinIO HTTP endpoint ready'; $ready = $true; break }
    Write-Output "MinIO not ready yet ($i/30), retrying..."; Start-Sleep -Seconds 2
}
if (-not $ready) { Write-Warning 'MinIO health endpoint did not become ready; will attempt creation anyway' }

for ($i=1; $i -le 30; $i++) {
    # Try aws-cli
    & docker run --network $NETWORK --rm -e AWS_ACCESS_KEY_ID=$S3AccessKey -e AWS_SECRET_ACCESS_KEY=$S3Secret -e AWS_REGION=${Env:S3_REGION} amazon/aws-cli s3 --endpoint-url $DOCKER_S3_ENDPOINT mb s3://$S3Bucket > $null 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Output "Bucket created (aws-cli) or already exists"; exit 0 }

    # Fallback to mc
    & docker run --network $NETWORK --rm minio/mc:latest alias set local $DOCKER_S3_ENDPOINT $S3AccessKey $S3Secret > $null 2>&1
    & docker run --network $NETWORK --rm minio/mc:latest mb local/$S3Bucket > $null 2>&1
    if ($LASTEXITCODE -eq 0) { Write-Output "Bucket created or already exists (mc)"; exit 0 }

    Write-Output "MinIO not ready, retrying... ($i)"; Start-Sleep -Seconds 2
}

Write-Output "Final check: does bucket already exist?"
& docker run --network $NETWORK --rm -e AWS_ACCESS_KEY_ID=$S3AccessKey -e AWS_SECRET_ACCESS_KEY=$S3Secret -e AWS_REGION=${Env:S3_REGION} amazon/aws-cli s3 ls --endpoint-url $DOCKER_S3_ENDPOINT 2>$null | Select-String $S3Bucket > $null
if ($LASTEXITCODE -eq 0) { Write-Output 'Bucket already exists'; exit 0 }

& docker run --network $NETWORK --rm minio/mc:latest alias set local $DOCKER_S3_ENDPOINT $S3AccessKey $S3Secret > $null 2>&1
& docker run --network $NETWORK --rm minio/mc:latest ls local 2>$null | Select-String $S3Bucket > $null
if ($LASTEXITCODE -eq 0) { Write-Output 'Bucket already exists (mc)'; exit 0 }

Write-Error 'Failed to create bucket after retries'
exit 1
