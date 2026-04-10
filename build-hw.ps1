param(
    [string]$Target = "ipod6g",
    [string]$MsysRoot = "",
    [int]$Jobs = 0,
    [switch]$Incremental,
    [switch]$SkipDep
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$repoRoot\tools\rockpod-msys.ps1"

$extra = @{
    TARGET_ARG = $Target
}
if ($Jobs -gt 0) {
    $extra["JOBS"] = "$Jobs"
}
if ($Incremental) {
    $extra["ROCKPOD_INCREMENTAL"] = "1"
}
if ($SkipDep) {
    $extra["ROCKPOD_SKIP_DEP"] = "1"
}

$code = Invoke-RockpodMsysBash -RepoRoot $repoRoot -MsysRoot $MsysRoot -BashCommand './build-hw.sh "$TARGET_ARG"' -ExtraEnv $extra
if ($code -ne 0) {
    throw "build-hw.sh failed with exit code $code"
}
