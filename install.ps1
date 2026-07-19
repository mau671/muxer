<#
.SYNOPSIS
Installs the latest version of Muxer for Windows.
#>

$ErrorActionPreference = "Stop"

$repo = "mau671/muxer"
$binName = "muxer.exe"

Write-Host "Fetching latest release information..."
$releaseUrl = "https://api.github.com/repos/$repo/releases/latest"
$releaseData = Invoke-RestMethod -Uri $releaseUrl

$version = $releaseData.tag_name.TrimStart('v')
if ([string]::IsNullOrEmpty($version)) {
    Write-Error "Failed to fetch the latest version."
}

Write-Host "Latest version found: $version"

# Architecture detection
$arch = "amd64"
if ($env:PROCESSOR_ARCHITECTURE -match "ARM64") {
    $arch = "arm64"
}

# Format: muxer_VERSION_windows_arch.zip
$assetName = "muxer_${version}_windows_${arch}.zip"
$downloadUrl = "https://github.com/$repo/releases/download/v${version}/${assetName}"

$installDir = "$env:LOCALAPPDATA\Programs\muxer"
if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
}

$tempZip = Join-Path $env:TEMP $assetName

Write-Host "Downloading $assetName..."
Invoke-WebRequest -Uri $downloadUrl -OutFile $tempZip

Write-Host "Extracting binary..."
Expand-Archive -Path $tempZip -DestinationPath $installDir -Force

Remove-Item $tempZip

# Add to PATH if not already present
$userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$installDir*") {
    Write-Host "Adding $installDir to user PATH..."
    [Environment]::SetEnvironmentVariable("PATH", "$userPath;$installDir", "User")
    Write-Host "Please restart your terminal to use the 'muxer' command."
}

Write-Host "✅ Successfully installed Muxer v$version to $installDir\$binName"
