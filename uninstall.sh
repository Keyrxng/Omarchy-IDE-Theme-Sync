#!/bin/bash

# Omarchy IDE Theme Sync Uninstaller

set -e

PROJECT_NAME="Omarchy IDE Theme Sync"

echo "🗑️ Uninstalling $PROJECT_NAME..."
echo ""

# Remove integration
remove_integration() {
    echo "🔧 Removing integration..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [[ -f "$SCRIPT_DIR/src/integration_hooks.py" ]]; then
        if python3 "$SCRIPT_DIR/src/integration_hooks.py" remove; then
            echo "✓ Integration removed successfully"
        else
            echo "⚠️ Failed to remove integration cleanly"
        fi
    else
        echo "⚠️ Integration removal script not found"
    fi
    
    echo ""
}

# Remove CLI tool
remove_cli_tool() {
    echo "🛠️ Removing CLI tool..."
    
    CLI_SCRIPT="$HOME/.local/bin/omarchy-theme-sync"
    
    if [[ -f "$CLI_SCRIPT" ]]; then
        rm "$CLI_SCRIPT"
        echo "✓ Removed CLI tool: $CLI_SCRIPT"
    else
        echo "ℹ️ CLI tool not found (may already be removed)"
    fi
    
    echo ""
}

# Clean up generated theme files (optional)
clean_theme_files() {
    echo "🧹 Cleaning up generated theme files..."
    
    read -p "Do you want to remove all generated IDE theme files? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        THEMES_DIR="$HOME/.config/omarchy/themes"
        
        if [[ -d "$THEMES_DIR" ]]; then
            find "$THEMES_DIR" -name "vscode.json" -delete 2>/dev/null || true
            find "$THEMES_DIR" -name "cursor.json" -delete 2>/dev/null || true
            echo "✓ Removed generated theme files"
        else
            echo "ℹ️ Themes directory not found"
        fi
    else
        echo "ℹ️ Keeping generated theme files"
    fi
    
    echo ""
}

# Show completion message
show_completion() {
    echo "✅ Uninstallation complete!"
    echo ""
    echo "📖 What's been removed:"
    echo "  • Integration with Omarchy theme switching"
    echo "  • Enhanced theme switcher (original restored)"
    echo "  • Theme generator from themes directory"
    echo "  • Command line tool"
    echo ""
    echo "💡 Note:"
    echo "  • Your original Omarchy functionality is restored"
    echo "  • Generated theme files may still exist (unless you chose to remove them)"
    echo "  • This project directory can be safely deleted"
    echo ""
    echo "🔄 To reinstall:"
    echo "  ./install.sh"
    echo ""
    echo "👋 Thanks for trying $PROJECT_NAME!"
}

# Main uninstallation flow
main() {
    remove_integration
    remove_cli_tool
    clean_theme_files
    show_completion
}

# Run uninstallation
main
