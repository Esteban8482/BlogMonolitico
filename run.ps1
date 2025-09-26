# Ejecutar el proyecto localmente con todos los microservicios
# Ejecutar en segundo plano o mostrarlos en consola
# Permitir elegir los microservicios a mostrar o a ejecutar

# Ejemplo de uso:
# .\run.ps1 -d auth -r auth, user -> mostrar auth en consola externa y ejecutar auth y user

param (
    [string[]]$d = @(),  # Lista de servicios a mostrar en consola, null o vacío todos en segundo plano
    [string[]]$r = @()   # Lista de servicios a ejecutar, null o vacío para todos
)

Write-Host "Iniciando entorno local..."

if (-not (Test-Path ".venv")) {
    # crear entorno virtual
    Write-Host "Creando entorno virtual..."
    python -m venv .venv
}

$venvPath = "$PWD\.venv\Scripts\activate.ps1"
# Activar entorno virtual
& $venvPath

# Definir servicios
$services_list = @(
    @{ Name = "auth"; Path = "."; Script = "python app.py" },
    @{ Name = "user"; Path = "microservices/user"; Script = "python app.py" },
    @{ Name = "post"; Path = "microservices/post"; Script = "python app.py" },
    @{ Name = "comments"; Path = "microservices/comments-service"; Script = "python app.py" }
)

$services = $services_list | Where-Object { $r -contains $_.Name -or $r.Count -eq 0 }

# Ejecutar servicios según visibilidad
foreach ($svc in $services) {
    $fullCommand = "cd $($svc.Path); $($svc.Script)"

    if ($d -contains $svc.Name) {
        Write-Host "Mostrando servicio: $($svc.Name)"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", $fullCommand
    }
    else {
        Write-Host "Ejecutando en segundo plano: $($svc.Name)"
        # Start-Job -ScriptBlock {
        #     & $using:venvPath
        #     Invoke-Expression
        #     $args[0]
        # } -ArgumentList $fullCommand
        Start-Process powershell -WindowStyle Hidden -ArgumentList "-Command", $fullCommand
    }
}

Write-Host "`nTodos los servicios han sido lanzados."
Write-Host "Presiona ENTER para detenerlos..."
Read-Host

# Detener servicios
Get-Job | Stop-Job
Get-Job | Remove-Job
Get-Process python | ForEach-Object {
    try {
        $_.CloseMainWindow() | Out-Null
        $_.Kill()
    } catch {
        Write-Host "No se pudo cerrar el proceso $($_.Id): $($_.Exception.Message)"
    }
}

Write-Host "Servicios detenidos."
