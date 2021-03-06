<#
 .SYNOPSIS
 Lists the management commands for Stackdump.
 .DESCRIPTION
 Prints out a list of all the management commands supported in this version of 
 Stackdump.
 .EXAMPLE
 List-StackdumpCommands
 #>

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
$CommandsDir = Join-Path $ScriptDir 'python\src\stackdump\commands'

ls $CommandsDir -Filter '*.py' | % { Write-Host "`t$($_.BaseName)" }
