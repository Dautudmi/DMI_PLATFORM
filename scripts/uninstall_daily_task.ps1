[CmdletBinding()]
param(
    [string]$TaskName = "DMI Platform Daily Production"
)

$ErrorActionPreference = "Stop"

$ExistingTask = Get-ScheduledTask `
    -TaskName $TaskName `
    -ErrorAction SilentlyContinue

if ($null -eq $ExistingTask) {
    Write-Host "Scheduled task does not exist: $TaskName"
    exit 0
}

Unregister-ScheduledTask `
    -TaskName $TaskName `
    -Confirm:$false

Write-Host "Scheduled task removed successfully: $TaskName"