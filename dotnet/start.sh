#!/bin/bash
# Workflow Lab - Launch .NET Workflow Project

echo "============================================================"
echo "              Workflow Lab (.NET) - Starting"
echo "============================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Running dotnet project..."
dotnet run


