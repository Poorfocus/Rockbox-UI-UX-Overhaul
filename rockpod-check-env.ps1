param(
    [string]$MsysRoot = "",
    [ValidateSet("All", "SimOnly", "HwOnly")]
    [string]$Scope = "All"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$repoRoot\tools\rockpod-msys.ps1"

$flag = switch ($Scope) {
    "SimOnly" { "--sim-only" }
    "HwOnly"  { "--hw-only" }
    default   { "" }
}

$bashCmd = if ($flag -ne "") {
    "./tools/rockpod-check-env.sh $flag"
} else {
    "./tools/rockpod-check-env.sh"
}

$code = Invoke-RockpodMsysBash -RepoRoot $repoRoot -MsysRoot $MsysRoot -BashCommand $bashCmd
exit $code
