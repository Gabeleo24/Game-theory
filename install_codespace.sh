#!/bin/bash

# ADS599 Capstone - One-Command Codespace Installation
# GitHub Codespace Quick Setup Script

echo "🚀 ADS599 Capstone Soccer Intelligence System - Codespace Installation"
echo ""

# Check if we're in a Codespace
if [ -z "$CODESPACE_NAME" ]; then
    echo "⚠️  This script is designed for GitHub Codespaces"
    echo "   Please run this in a GitHub Codespace environment"
    echo ""
    echo "📋 To create a Codespace:"
    echo "   1. Go to: https://github.com/mmoramora/ADS599_Capstone"
    echo "   2. Click Code > Codespaces > Create codespace on main"
    echo "   3. Run this script in the Codespace terminal"
    exit 1
fi

echo "✅ GitHub Codespace detected: $CODESPACE_NAME"
echo ""

# Download and run the full installation script
echo "📥 Downloading installation script..."
curl -fsSL https://raw.githubusercontent.com/mmoramora/ADS599_Capstone/main/scripts/setup/codespace_installation.sh -o /tmp/codespace_installation.sh

echo "🚀 Running installation..."
chmod +x /tmp/codespace_installation.sh
/tmp/codespace_installation.sh

echo ""
echo "🎉 Installation complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Set your SportMonks API key as a Codespace secret (if not done)"
echo "2. Run: ./start_codespace.sh"
echo "3. Access Jupyter Lab: https://$CODESPACE_NAME-8888.app.github.dev"
echo ""
echo "📚 Full guide: CODESPACE_INSTALLATION_GUIDE.md"
