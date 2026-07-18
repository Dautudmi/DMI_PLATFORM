[CmdletBinding()]
param(
    [string]$TaskName = "DMI Platform Daily Production",

    [ValidatePattern("^\d{2}:\d{2}$")]
    [string]$RunTime = "19:00",

    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (
    Resolve-Path (
        Join-Path $PSScriptRoot ".."
    )
).Path

$BatchFile = Join-Path `
    $ProjectRoot `
    "scripts\run_daily.bat"

if (-not (Test-Path -LiteralPath $BatchFile -PathType Leaf)) {
    throw "Batch file not found: $BatchFile"
}

$ClientConfigPath = [Environment]::GetEnvironmentVariable(
    "DMI_PEV24_CLIENT_CONFIG_PATH",
    "User"
)

$ClientsFolderPath = [Environment]::GetEnvironmentVariable(
    "DMI_PEV24_CLIENTS_FOLDER_PATH",
    "User"
)

if ([string]::IsNullOrWhiteSpace($ClientConfigPath)) {
    throw (
        "Missing User environment variable: " +
        "DMI_PEV24_CLIENT_CONFIG_PATH"
    )
}

if ([string]::IsNullOrWhiteSpace($ClientsFolderPath)) {
    throw (
        "Missing User environment variable: " +
        "DMI_PEV24_CLIENTS_FOLDER_PATH"
    )
}

if (-not (Test-Path -LiteralPath $ClientConfigPath -PathType Leaf)) {
    throw "Client config file does not exist: $ClientConfigPath"
}

if (-not (Test-Path -LiteralPath $ClientsFolderPath -PathType Container)) {
    throw "Clients folder does not exist: $ClientsFolderPath"
}

$ExistingTask = Get-ScheduledTask `
    -TaskName $TaskName `
    -ErrorAction SilentlyContinue

if ($null -ne $ExistingTask -and -not $Force) {
    throw (
        "Scheduled task already exists: $TaskName. " +
        "Run again with -Force to replace it."
    )
}

if ($null -ne $ExistingTask -and $Force) {
    Unregister-ScheduledTask `
        -TaskName $TaskName `
        -Confirm:$false
}

$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$BatchFile`"" `
    -WorkingDirectory $ProjectRoot

$TriggerTime = [datetime]::ParseExact(
    $RunTime,
    "HH:mm",
    [System.Globalization.CultureInfo]::InvariantCulture
)

$Trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At $TriggerTime

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (
        New-TimeSpan -Hours 2
    ) `
    -MultipleInstances IgnoreNew

$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

$Principal = New-ScheduledTaskPrincipal `
    -UserId $CurrentUser `
    -LogonType Interactive `
    -RunLevel Limited

$Description = (
    "Run DMI Platform daily production pipeline. " +
    "Launcher: $BatchFile"
)

$Task = New-ScheduledTask `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description $Description

Register-ScheduledTask `
    -TaskName $TaskName `
    -InputObject $Task `
    -Force | Out-Null

Write-Host ""
Write-Host "DMI scheduled task installed successfully."
Write-Host "Task name : $TaskName"
Write-Host "Run time  : $RunTime"
Write-Host "User      : $CurrentUser"
Write-Host "Launcher  : $BatchFile"
Write-Host ""
Write-Host "The task runs while this Windows user is logged in."