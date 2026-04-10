# Unified RockPod CLI (Windows PowerShell). Dispatches to check / sim / hw scripts.
# Usage:
#   .\rockpod.ps1 check [-Scope All|SimOnly|HwOnly] [-MsysRoot path]
#   .\rockpod.ps1 sim  [-Incremental] [-SkipDep] [-StrictInstall] [-InstallOnly] [-Jobs N] [-MsysRoot path]
#   .\rockpod.ps1 hw   [-Target ipod6g|ipodvideo] [-Incremental] [-SkipDep] [-Jobs N] [-MsysRoot path]
#
# Named parameters are listed explicitly so Windows PowerShell 5.1 can bind them reliably.
# (Splatting ValueFromRemainingArguments into child scripts merges switches incorrectly.)

param(
    [Parameter(Position = 0)]
    [ValidateSet("check", "sim", "hw", "help")]
    [string]$Command = "help",
    [string]$Target = "ipod6g",
    [string]$MsysRoot = "",
    [int]$Jobs = 0,
    [switch]$Incremental,
    [switch]$SkipDep,
    [switch]$StrictInstall,
    [switch]$InstallOnly,
    [ValidateSet("All", "SimOnly", "HwOnly")]
    [string]$Scope = "All",
    [Parameter(ValueFromRemainingArguments = $true)]
    [object[]]$RemainingArgs = @()
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Command -eq "help") {
    @"
RockPod toolchain (MSYS2 UCRT64)

  .\rockpod.ps1 check   Prerequisite audit (SDL2, gcc, arm-none-eabi, perl, ...).
                        -Scope SimOnly | HwOnly

  .\rockpod.ps1 sim     Simulator build. -Incremental -SkipDep -StrictInstall -InstallOnly -Jobs N
                        -InstallOnly: font/WPS/icon sync without recompile (fastest after asset changes).

  .\rockpod.ps1 hw      Hardware build. -Target ipod6g|ipodvideo -Incremental -SkipDep -Jobs N

MSYS2: -MsysRoot or env ROCKPOD_MSYS_ROOT (default C:\msys64).

See BUILD.md for full build flow.
"@
    exit 0
}

if ($null -ne $RemainingArgs -and $RemainingArgs.Count -gt 0) {
    Write-Warning ("Ignoring extra arguments (forwarding is explicit): " + ($RemainingArgs -join ' '))
}

switch ($Command) {
    "check" {
        & "$repoRoot\rockpod-check-env.ps1" -MsysRoot $MsysRoot -Scope $Scope
        exit $LASTEXITCODE
    }
    "sim" {
        & "$repoRoot\build-sim.ps1" -MsysRoot $MsysRoot -Jobs $Jobs -Incremental:$Incremental -SkipDep:$SkipDep -StrictInstall:$StrictInstall -InstallOnly:$InstallOnly
        if (-not $?) { exit 1 }
        exit 0
    }
    "hw" {
        & "$repoRoot\build-hw.ps1" -Target $Target -MsysRoot $MsysRoot -Jobs $Jobs -Incremental:$Incremental -SkipDep:$SkipDep
        if (-not $?) { exit 1 }
        exit 0
    }
}
