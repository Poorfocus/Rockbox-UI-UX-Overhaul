# Verifies Apple2026 + core simulator install outputs under simdisk after "make install".
# Run from repo root:  .\tools\verify-sim-install.ps1  [-SimRoot path]
#
# Checks:
#   - sim binary present
#   - Apple2026.cfg (wpsbuild output)
#   - Apple2026 SBS slot fonts: 28-SFProDisplay-Bold (slot 2), 16-SFProText-Semibold (slot 3),
#     20-SFProText-Regular (slot 5 / list font), 22-SFProText-Medium (PictureFlow/WPS)
#   - All Apple2026 fonts that exist in repo/fonts/ (full staleness scan)
#   - Apple2026Icons.bmp (menu icon strip)
#   - Key WPS asset BMPs under wps/Apple2026/
#   - Staleness: warns when repo fonts/ are newer than the last make-install stamp
#     (falls back to sim binary mtime if stamp absent)

param(
    [string]$SimRoot = "",
    [switch]$StrictStale
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if ($SimRoot -eq "") {
    $SimRoot = Join-Path $repoRoot "build-sim\simdisk\.rockbox"
}

# rockboxui.exe lives in build-sim/, simdisk/.rockbox/ is two levels below it.
$buildSimRoot = Split-Path -Parent (Split-Path -Parent $SimRoot)
$exePath = Join-Path $buildSimRoot "rockboxui.exe"

$required = @(
    @{ Rel = "rockboxui.exe";                          Full = $exePath;                                  Note = "simulator binary" }
    @{ Rel = "themes\Apple2026.cfg";                   Full = Join-Path $SimRoot "themes\Apple2026.cfg"; Note = "Apple2026 theme cfg (wpsbuild)" }
    @{ Rel = "fonts\28-SFProDisplay-Bold.fnt";         Full = Join-Path $SimRoot "fonts\28-SFProDisplay-Bold.fnt";  Note = "SBS slot 2 - large title; MISSING = no Library heading" }
    @{ Rel = "fonts\16-SFProText-Semibold.fnt";        Full = Join-Path $SimRoot "fonts\16-SFProText-Semibold.fnt"; Note = "SBS slot 3 - header chrome + mini-player track" }
    @{ Rel = "fonts\20-SFProText-Regular.fnt";         Full = Join-Path $SimRoot "fonts\20-SFProText-Regular.fnt";  Note = "SBS slot 5 + WPSLIST list font" }
    @{ Rel = "fonts\22-SFProText-Regular.fnt";         Full = Join-Path $SimRoot "fonts\22-SFProText-Regular.fnt";  Note = "legacy list font / config.cfg override" }
    @{ Rel = "fonts\22-SFProText-Medium.fnt";          Full = Join-Path $SimRoot "fonts\22-SFProText-Medium.fnt";   Note = "PictureFlow album/artist title font" }
    @{ Rel = "fonts\18-SFProText-Regular.fnt";         Full = Join-Path $SimRoot "fonts\18-SFProText-Regular.fnt";  Note = "PictureFlow tracklist font" }
    @{ Rel = "fonts\19-SFProText-Medium.fnt";          Full = Join-Path $SimRoot "fonts\19-SFProText-Medium.fnt";   Note = "PictureFlow album/artist font" }
    @{ Rel = "icons\Apple2026Icons.bmp";               Full = Join-Path $SimRoot "icons\Apple2026Icons.bmp";        Note = "Apple2026 menu icon strip" }
    @{ Rel = "wps\Apple2026.sbs";                      Full = Join-Path $SimRoot "wps\Apple2026.sbs";               Note = "Apple2026 SBS skin" }
    @{ Rel = "wps\Apple2026.wps";                      Full = Join-Path $SimRoot "wps\Apple2026.wps";               Note = "Apple2026 WPS skin" }
    @{ Rel = "wps\Apple2026\batteryStatus.bmp";        Full = Join-Path $SimRoot "wps\Apple2026\batteryStatus.bmp"; Note = "WPS battery strip" }
    @{ Rel = "wps\Apple2026\playerStatus.bmp";         Full = Join-Path $SimRoot "wps\Apple2026\playerStatus.bmp"; Note = "WPS player state strip" }
    @{ Rel = "wps\Apple2026\pb.bmp";                   Full = Join-Path $SimRoot "wps\Apple2026\pb.bmp";            Note = "WPS progress bar fill" }
    @{ Rel = "wps\Apple2026\pb_backdrop.bmp";          Full = Join-Path $SimRoot "wps\Apple2026\pb_backdrop.bmp";  Note = "WPS progress bar backdrop" }
    @{ Rel = "wps\Apple2026\albumPlaceholder.bmp";     Full = Join-Path $SimRoot "wps\Apple2026\albumPlaceholder.bmp"; Note = "WPS no-cover placeholder" }
)

$fail = 0
Write-Host "RockPod sim install check"
Write-Host "  .rockbox root : $SimRoot"
Write-Host "  sim binary    : $exePath"
Write-Host ""

foreach ($item in $required) {
    if (Test-Path -LiteralPath $item.Full) {
        Write-Host "  [ok]   $($item.Rel)"
    }
    else {
        Write-Host "  [MISS] $($item.Rel)  -- $($item.Note)"
        $fail = 1
    }
}

# Staleness check: compare repo font/ .fnt files against installed runtime fonts.
# Uses .rockpod_install_stamp (written by make install via build-sim.sh) when present;
# falls back to rockboxui.exe mtime (less accurate — install runs after compile).
Write-Host ""
Write-Host "Staleness check (repo fonts vs runtime):"
$staleWarn = 0
$repoFontsDir = Join-Path $repoRoot "fonts"

# Prefer install stamp (written by build-sim.sh after successful make install)
$installStampPath = Join-Path $buildSimRoot ".rockpod_install_stamp"
$referenceTime = $null
$referenceLabel = ""
if (Test-Path -LiteralPath $installStampPath) {
    $referenceTime = (Get-Item -LiteralPath $installStampPath).LastWriteTime
    $referenceLabel = ".rockpod_install_stamp ($referenceTime)"
}
elseif (Test-Path -LiteralPath $exePath) {
    $referenceTime = (Get-Item -LiteralPath $exePath).LastWriteTime
    $referenceLabel = "rockboxui.exe ($referenceTime) [no install stamp; less accurate]"
}

if ($null -ne $referenceTime) {
    Write-Host "  Reference: $referenceLabel"
    if (Test-Path $repoFontsDir) {
        $staleFonts = @(Get-ChildItem $repoFontsDir -Filter "*.fnt" |
            Where-Object { $_.LastWriteTime -gt $referenceTime })
        if ($staleFonts.Count -gt 0) {
            Write-Host "  [WARN] $($staleFonts.Count) repo font(s) newer than last install -- run 'make install' or build-sim.ps1 -Incremental -SkipDep:"
            foreach ($f in $staleFonts) {
                Write-Host "         $($f.Name)  (repo: $($f.LastWriteTime))"
            }
            $staleWarn = 1
        }
        else {
            Write-Host "  [ok]   all repo fonts are current with last install"
        }
    }
}
else {
    Write-Host "  [skip] no sim binary or install stamp found; skipping staleness check"
}

# Skin staleness: warn if repo SBS/WPS are newer than installed runtime copies
$sbsRepo    = Join-Path $repoRoot "wps\Apple2026.sbs"
$sbsRuntime = Join-Path $SimRoot  "wps\Apple2026.sbs"
if ((Test-Path -LiteralPath $sbsRepo) -and (Test-Path -LiteralPath $sbsRuntime)) {
    $repoTime    = (Get-Item -LiteralPath $sbsRepo).LastWriteTime
    $runtimeTime = (Get-Item -LiteralPath $sbsRuntime).LastWriteTime
    if ($repoTime -gt $runtimeTime) {
        Write-Host "  [WARN] wps/Apple2026.sbs is newer than installed copy -- run make install"
        $staleWarn = 1
    }
    else {
        Write-Host "  [ok]   Apple2026.sbs runtime is current"
    }
}
$wpsRepo    = Join-Path $repoRoot "wps\Apple2026.wps"
$wpsRuntime = Join-Path $SimRoot  "wps\Apple2026.wps"
if ((Test-Path -LiteralPath $wpsRepo) -and (Test-Path -LiteralPath $wpsRuntime)) {
    $repoTime    = (Get-Item -LiteralPath $wpsRepo).LastWriteTime
    $runtimeTime = (Get-Item -LiteralPath $wpsRuntime).LastWriteTime
    if ($repoTime -gt $runtimeTime) {
        Write-Host "  [WARN] wps/Apple2026.wps is newer than installed copy -- run make install"
        $staleWarn = 1
    }
    else {
        Write-Host "  [ok]   Apple2026.wps runtime is current"
    }
}

# config.cfg font discrepancy report
$cfgPath = Join-Path $SimRoot "config.cfg"
if (Test-Path -LiteralPath $cfgPath) {
    $cfgFont = Get-Content $cfgPath | Where-Object { $_ -match "^font:" } | Select-Object -First 1
    $themeFont = Get-Content (Join-Path $SimRoot "themes\Apple2026.cfg") -ErrorAction SilentlyContinue |
                 Where-Object { $_ -match "^font:" } | Select-Object -First 1
    if ($cfgFont -and $themeFont -and ($cfgFont -ne $themeFont)) {
        Write-Host ""
        Write-Host "  [INFO] config.cfg font differs from Apple2026.cfg:"
        Write-Host "         config.cfg    : $cfgFont"
        Write-Host "         Apple2026.cfg : $themeFont"
        Write-Host "         (config.cfg is user runtime state; load theme in sim to sync)"
    }
}

Write-Host ""
if ($fail -ne 0) {
    Write-Host "Result: FAILED -- run 'make install' inside build-sim/ or use build-sim.ps1 -Incremental"
    Write-Host "         Use -StrictInstall on build-sim.ps1 to catch make install failures at build time."
    exit 1
}
if ($staleWarn -ne 0) {
    if ($StrictStale) {
        Write-Host "Result: FAILED (stale assets; -StrictStale set)"
        exit 1
    }
    Write-Host "Result: OK (with staleness warnings -- re-run make install to sync)"
    exit 0
}
Write-Host "Result: OK"
exit 0
