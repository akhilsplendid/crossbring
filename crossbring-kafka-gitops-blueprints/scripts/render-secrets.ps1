$ErrorActionPreference = 'Stop'
$envPath = Resolve-Path (Join-Path $PSScriptRoot "../crossbring-jobmodel/.env") -ErrorAction SilentlyContinue
$dsn = ''
if($envPath){
  $line = Get-Content $envPath | Where-Object { $_ -match '^JOBMODEL_DSN=' } | Select-Object -First 1
  if($line){ $dsn = ($line -split '=',2)[1] }
}
if(-not $dsn){
  Write-Host "Enter JOBMODEL_DSN (postgresql://...):"
  $dsn = Read-Host
}
Write-Host "Enter DB_PASSWORD (for supabase.properties):"
$pw = Read-Host
@"
apiVersion: v1
kind: Secret
metadata:
  name: supabase-secrets
  namespace: data
type: Opaque
stringData:
  supabase.properties: |
    DB_PASSWORD=$pw
  dsn: |
    $dsn
"@
