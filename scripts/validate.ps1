$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Theme = Join-Path $Root "themes/Apollo.vstheme"
$Schema = Join-Path $Root "schemas/vstheme.xsd"

$settings = [System.Xml.XmlReaderSettings]::new()
$null = $settings.Schemas.Add($null, $Schema)
$settings.ValidationType = [System.Xml.ValidationType]::Schema
$settings.ValidationFlags = [System.Xml.Schema.XmlSchemaValidationFlags]::ReportValidationWarnings
$errors = [System.Collections.Generic.List[string]]::new()
$handler = [System.Xml.Schema.ValidationEventHandler] {
    param($sender, $eventArgs)
    $errors.Add($eventArgs.Message)
}
$settings.add_ValidationEventHandler($handler)

$reader = [System.Xml.XmlReader]::Create($Theme, $settings)
try {
    while ($reader.Read()) { }
}
finally {
    $reader.Dispose()
}

if ($errors.Count -gt 0) {
    throw "Theme XML schema validation failed:`n$($errors -join "`n")"
}

$document = [System.Xml.XmlDocument]::new()
$document.Load($Theme)
$themeNode = $document.SelectSingleNode("/Themes/Theme")
if ($null -eq $themeNode -or $themeNode.GetAttribute("Name") -ne "Apollo" -or $themeNode.GetAttribute("MinVSVersion") -ne "17.0") {
    throw "Theme metadata is invalid."
}

$requiredCategories = @("Environment", "Text Editor", "Command Window", "Output Window")
foreach ($category in $requiredCategories) {
    $node = $document.SelectSingleNode("/Themes/Theme/Category[@Name='$category']")
    if ($null -eq $node) {
        throw "Required category '$category' is missing."
    }
}

Write-Host "Validated themes/Apollo.vstheme against schemas/vstheme.xsd on Windows."
