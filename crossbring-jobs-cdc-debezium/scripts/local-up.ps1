param(
  [string]$DbPassword = "crossbringn8n"
)

$ErrorActionPreference = 'Stop'

# Ensure secrets file
$secrets = Join-Path $PSScriptRoot "../connectors/supabase.properties"
if(-not (Test-Path $secrets)){
  "DB_PASSWORD=$DbPassword" | Out-File -Encoding ascii $secrets
  Write-Host "Created secrets file at $secrets"
}

# Provide JOBMODEL_DSN to compose via .env
$jobmodelEnv = Resolve-Path (Join-Path $PSScriptRoot "../crossbring-jobmodel/.env") -ErrorAction SilentlyContinue
if($jobmodelEnv){
  $dsn = (Get-Content $jobmodelEnv | Where-Object { $_ -match '^JOBMODEL_DSN=' } | ForEach-Object { ($_ -split '=',2)[1] })
  if($dsn){
    $composeEnvPath = Join-Path $PSScriptRoot "../.env"
    "JOBMODEL_DSN=$dsn" | Out-File -Encoding ascii $composeEnvPath
    Write-Host "Wrote compose env with JOBMODEL_DSN"
  }
}

docker compose -f "$PSScriptRoot/../docker-compose.yml" up -d

Write-Host "Waiting for Connect endpoints..."
function Wait-Endpoint($url){
  for($i=0;$i -lt 60;$i++){
    try { $r = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2; if($r.StatusCode -ge 200){ return } } catch {}
    Start-Sleep -Seconds 2
  }
  throw "Timeout waiting for $url"
}

Wait-Endpoint "http://localhost:8083/connectors"
Wait-Endpoint "http://localhost:8084/connectors"

Write-Host "Registering JDBC sink (8083)"
Invoke-WebRequest -UseBasicParsing -Uri http://localhost:8083/connectors -Method POST -ContentType 'application/json' -InFile (Join-Path $PSScriptRoot "../connectors/jdbc-sink-stg-jobs.json") | Out-Null

Write-Host "Registering Debezium source (8084)"
Invoke-WebRequest -UseBasicParsing -Uri http://localhost:8084/connectors -Method POST -ContentType 'application/json' -InFile (Join-Path $PSScriptRoot "../connectors/supabase-jobs.json") | Out-Null

Write-Host "Done. Check connectors at http://localhost:8083/connectors and http://localhost:8084/connectors"
