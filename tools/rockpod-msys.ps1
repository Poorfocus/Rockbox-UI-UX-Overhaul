# Shared MSYS2 / UCRT64 helpers for RockPod PowerShell wrappers.
# Dot-source from repo root: . ./tools/rockpod-msys.ps1

Set-StrictMode -Version Latest

function Get-RockpodMsysRoot {
    param(
        [string]$MsysRoot = ""
    )
    if ($MsysRoot -ne "") {
        return $MsysRoot.TrimEnd('\')
    }
    if ($null -ne $env:ROCKPOD_MSYS_ROOT -and $env:ROCKPOD_MSYS_ROOT -ne "") {
        return $env:ROCKPOD_MSYS_ROOT.TrimEnd('\')
    }
    return "C:\msys64"
}

function Get-RockpodMsysPaths {
    param(
        [string]$MsysRoot = ""
    )
    $root = Get-RockpodMsysRoot -MsysRoot $MsysRoot
    @{
        MsysRoot = $root
        EnvExe   = Join-Path $root "usr\bin\env.exe"
        BashExe  = Join-Path $root "usr\bin\bash.exe"
    }
}

function Test-RockpodMsysInstall {
    param(
        [string]$MsysRoot = ""
    )
    $p = Get-RockpodMsysPaths -MsysRoot $MsysRoot
    if (-not (Test-Path -LiteralPath $p.EnvExe)) {
        throw "MSYS2 env.exe not found at $($p.EnvExe). Install MSYS2 or set -MsysRoot / `$env:ROCKPOD_MSYS_ROOT."
    }
    if (-not (Test-Path -LiteralPath $p.BashExe)) {
        throw "MSYS2 bash.exe not found at $($p.BashExe)."
    }
    return $p
}

# Same PATH order as legacy build scripts (SDL + toolchain + coreutils)
$script:RockpodMsysPathPrefix = "/ucrt64/bin:/mingw64/bin:/usr/bin"

function Invoke-RockpodMsysBash {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,
        [Parameter(Mandatory = $true)]
        [string]$BashCommand,
        [string]$MsysRoot = "",
        [hashtable]$ExtraEnv = $null
    )
    $p = Test-RockpodMsysInstall -MsysRoot $MsysRoot
    $prefix = 'export PATH="' + $script:RockpodMsysPathPrefix + ':$PATH"; project_root=$(cygpath -u "$PROJECT_ROOT"); cd "$project_root" && '
    $fullCmd = $prefix + $BashCommand

    # Redirect all output to a temp file (no pipeline after native exe) so:
    # - $LASTEXITCODE stays bash/env's real exit code
    # - callers can safely do $code = Invoke-RockpodMsysBash (integer only; stdout not captured)
    $log = [System.IO.Path]::GetTempFileName()
    try {
        # Git / tools may write benign messages to stderr; do not let that surface as
        # NativeCommandError in StrictMode (real exit code still comes from env.exe).
        $prevEap = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try {
        if ($null -eq $ExtraEnv -or $ExtraEnv.Count -eq 0) {
            & $p.EnvExe `
                "MSYSTEM=UCRT64" `
                "CHERE_INVOKING=1" `
                "HOME=$env:USERPROFILE" `
                "PROJECT_ROOT=$RepoRoot" `
                $p.BashExe `
                -lc $fullCmd > $log 2>&1
        } else {
            $invokeArgs = [System.Collections.ArrayList]@(
                "MSYSTEM=UCRT64",
                "CHERE_INVOKING=1",
                "HOME=$env:USERPROFILE",
                "PROJECT_ROOT=$RepoRoot"
            )
            foreach ($k in $ExtraEnv.Keys) {
                [void]$invokeArgs.Add("$k=$($ExtraEnv[$k])")
            }
            [void]$invokeArgs.Add($p.BashExe)
            [void]$invokeArgs.Add("-lc")
            [void]$invokeArgs.Add($fullCmd)
            & $p.EnvExe @([string[]]$invokeArgs.ToArray()) > $log 2>&1
        }
        } finally {
            $ErrorActionPreference = $prevEap
        }
        $code = $LASTEXITCODE
        if (Test-Path -LiteralPath $log) {
            Get-Content -LiteralPath $log -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_ }
        }
        return $code
    }
    finally {
        Remove-Item -LiteralPath $log -ErrorAction SilentlyContinue
    }
}
