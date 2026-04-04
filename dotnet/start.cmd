@echo off
REM Workflow Lab - Launch .NET Workflow Project

echo ============================================================
echo              Workflow Lab (.NET) - Starting
echo ============================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo Running dotnet project...
dotnet run
