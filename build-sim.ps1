param(
    [string]$MsysRoot = "",
    [int]$Jobs = 0,
    [switch]$Incremental,
    [switch]$SkipDep,
    [switch]$StrictInstall,
    [switch]$InstallOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$repoRoot\tools\rockpod-msys.ps1"

$extra = @{}
if ($Jobs -gt 0) {
    $extra["JOBS"] = "$Jobs"
}
if ($Incremental) {
    $extra["ROCKPOD_INCREMENTAL"] = "1"
}
if ($SkipDep) {
    $extra["ROCKPOD_SKIP_DEP"] = "1"
}
if ($StrictInstall) {
    $extra["ROCKPOD_STRICT_INSTALL"] = "1"
}
if ($InstallOnly) {
    $extra["ROCKPOD_INSTALL_ONLY"] = "1"
}

$envExtra = $null
if ($extra.Count -gt 0) {
    $envExtra = $extra
}

$code = Invoke-RockpodMsysBash -RepoRoot $repoRoot -MsysRoot $MsysRoot -BashCommand "./build-sim.sh" -ExtraEnv $envExtra
if ($code -ne 0) {
    throw "build-sim.sh failed with exit code $code"
}
