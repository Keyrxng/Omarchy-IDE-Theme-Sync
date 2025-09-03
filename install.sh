#!/bin/bash

# Omarchy IDE Theme Sync Installer
# Automatic VS Code and Cursor theme synchronization for Omarchy

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="Omarchy IDE Theme Sync"

echo "🚀 Installing $PROJECT_NAME..."
echo ""

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    # Check for Python 3
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed"
        exit 1
    fi
    echo "✓ Python 3 found"
    
    # Check for Omarchy
    if [[ ! -d "$HOME/.config/omarchy" ]]; then
        echo "❌ Omarchy configuration directory not found"
        echo "   Please install Omarchy first: https://omarchy.org"
        exit 1
    fi
    echo "✓ Omarchy configuration found"
    
    # Check for themes directory
    if [[ ! -d "$HOME/.config/omarchy/themes" ]]; then
        echo "❌ Omarchy themes directory not found"
        echo "   Please ensure Omarchy is properly installed"
        exit 1
    fi
    echo "✓ Omarchy themes directory found"
    
    # Check for at least one editor
    local editors_found=false
    if command -v code &> /dev/null; then
        echo "✓ VS Code found"
        editors_found=true
    fi
    
    if command -v cursor &> /dev/null; then
        echo "✓ Cursor found"
        editors_found=true
    fi
    
    if [[ "$editors_found" == false ]]; then
        echo "⚠️ Neither VS Code nor Cursor found in PATH"
        echo "   Install at least one editor for theme synchronization to work"
        echo "   Continuing anyway..."
    fi
    
    echo ""
}

# Install the integration
install_integration() {
    echo "🔧 Installing integration..."
    
    # Make scripts executable
    chmod +x "$SCRIPT_DIR/src"/*.py
    chmod +x "$SCRIPT_DIR/src"/*.sh 2>/dev/null || true
    
    # Run the integration setup
    if python3 "$SCRIPT_DIR/src/integration_hooks.py" setup; then
        echo "✓ Integration installed successfully"
    else
        echo "❌ Failed to install integration"
        exit 1
    fi
    
    echo ""
}

# Remove non-essential repo assets from local clone
cleanup_after_install() {
    echo "🧹 Cleaning up non-essential assets..."
    README_CLIPS_DIR="$SCRIPT_DIR/readme-clips"
    if [[ -d "$README_CLIPS_DIR" ]]; then
        rm -rf "$README_CLIPS_DIR"
        echo "✓ Removed readme-clips directory"
    else
        echo "ℹ️ No readme-clips directory to remove"
    fi
    echo ""
}

# Generate themes for existing themes
generate_existing_themes() {
    echo "🎨 Generating themes for existing Omarchy themes..."
    
    THEMES_DIR="$HOME/.config/omarchy/themes"
    GENERATOR="$THEMES_DIR/theme_generator.py"
    
    if [[ -f "$GENERATOR" ]]; then
        # Get count of themes
        THEME_COUNT=$(find "$THEMES_DIR" -maxdepth 1 -type d -name "*" -exec test -f "{}/alacritty.toml" \; -print | wc -l)
        
        if [[ "$THEME_COUNT" -gt 0 ]]; then
            echo "Found $THEME_COUNT themes to process..."
            
            # Generate themes for all existing themes
            if python3 "$GENERATOR" generate-all; then
                echo "✓ Generated themes for existing themes"
            else
                echo "⚠️ Some themes may have failed to generate (this is usually okay)"
            fi
        else
            echo "ℹ️ No existing themes found to process"
        fi
    else
        echo "❌ Theme generator not found after installation"
        exit 1
    fi
    
    echo ""
}

# Create command line tool
create_cli_tool() {
    echo "🛠️ Creating command line tool..."
    
    CLI_SCRIPT="$HOME/.local/bin/omarchy-theme-sync"
    CLI_DIR="$(dirname "$CLI_SCRIPT")"
    
    # Ensure .local/bin exists
    mkdir -p "$CLI_DIR"
    
    # Create the CLI script
    cat > "$CLI_SCRIPT" << 'EOF'
#!/bin/bash

# Omarchy IDE Theme Sync CLI Tool

THEMES_DIR="$HOME/.config/omarchy/themes"
GENERATOR="$THEMES_DIR/theme_generator.py"
# Note: Path will be determined dynamically by CLI tool

case "$1" in
    generate)
        if [[ -z "$2" ]]; then
            echo "Usage: omarchy-theme-sync generate <theme-name>"
            exit 1
        fi
        python3 "$GENERATOR" generate "$2"
        ;;
    generate-all)
        python3 "$GENERATOR" generate-all
        ;;
    status)
        python3 "$GENERATOR" status
        ;;
    apply)
        # Look for sync script in installed locations
        SYNC_LOCATIONS=(
            "$THEMES_DIR/../../../projects/omarchy-ide-theme-sync/src/theme_sync.py"
            "$HOME/.local/share/omarchy-ide-theme-sync/src/theme_sync.py"
        )
        
        SYNC_SCRIPT=""
        for location in "${SYNC_LOCATIONS[@]}"; do
            if [[ -f "$location" ]]; then
                SYNC_SCRIPT="$location"
                break
            fi
        done
        
        if [[ -n "$SYNC_SCRIPT" ]]; then
            python3 "$SYNC_SCRIPT" "$2"
        else
            echo "Warning: Theme sync script not found - themes generated but not applied"
        fi
        ;;
    *)
        echo "Omarchy IDE Theme Sync CLI"
        echo ""
        echo "Usage:"
        echo "  omarchy-theme-sync generate <theme-name>  Generate themes for specific theme"
        echo "  omarchy-theme-sync generate-all           Generate themes for all themes"
        echo "  omarchy-theme-sync status                 Check status of all themes"
        echo "  omarchy-theme-sync apply [theme-name]     Apply themes to editors"
        echo ""
        ;;
esac
EOF
    
    chmod +x "$CLI_SCRIPT"
    echo "✓ Created CLI tool: $CLI_SCRIPT"
    echo ""
}

# Show completion message
show_completion() {
    echo "🎉 Installation complete!"
    echo ""
    echo "📖 What's been installed:"
    echo "  • Theme generator integrated into Omarchy themes directory"
    echo "  • Enhanced theme switcher with automatic IDE sync"
    echo "  • Command line tool: omarchy-theme-sync"
    echo ""
    echo "🚀 Usage:"
    echo "  omarchy-theme-set <theme-name>        # Switch themes (IDEs will auto-sync)"
    echo "  omarchy-theme-sync status             # Check theme status"
    echo "  omarchy-theme-sync generate-all       # Regenerate all themes"
    echo ""
    echo "💡 Tips:"
    echo "  • Your VS Code and Cursor will now automatically match your Omarchy theme"
    echo "  • When you switch themes, IDE themes are generated and applied automatically"
    echo "  • Use 'omarchy-theme-sync status' to see which themes have IDE support"
    echo ""
    echo "🔧 If you need to uninstall:"
    echo "  ./uninstall.sh"
    echo ""
    echo "✨ Enjoy your synchronized themes!"
}

# Main installation flow
main() {
    check_prerequisites
    install_integration
    generate_existing_themes
    create_cli_tool
    cleanup_after_install
    show_completion
}

# Run installation
main
