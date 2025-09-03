#!/bin/bash

# Post Theme Install Hook for Omarchy IDE Theme Sync
# This script is called after a new theme is installed via Omarchy Menu > Install > Style > Theme
# and is used to generate IDE themes for the new theme

THEME_NAME="$1"
THEME_DIR="$2"
THEMES_DIR="$HOME/.config/omarchy/themes"
GENERATOR="$THEMES_DIR/theme_generator.py"

if [[ -z "$THEME_NAME" ]]; then
    echo "Error: No theme name provided to post-theme-install hook"
    exit 1
fi

if [[ -z "$THEME_DIR" ]]; then
    THEME_DIR="$THEMES_DIR/$THEME_NAME"
fi

echo "🔄 Post-theme-install hook: $THEME_NAME"
echo "📁 Theme directory: $THEME_DIR"

# Check if the theme has an alacritty.toml file
if [[ ! -f "$THEME_DIR/alacritty.toml" ]]; then
    echo "⚠️ No alacritty.toml found in theme, skipping IDE theme generation"
    exit 0
fi

echo "🔧 Generating IDE themes for newly installed theme: $THEME_NAME"

if [[ -f "$GENERATOR" ]]; then
    if python3 "$GENERATOR" generate "$THEME_NAME"; then
        echo "✅ Successfully generated IDE themes for $THEME_NAME"
        
        # Show what was generated
        if [[ -f "$THEME_DIR/$THEME_NAME-theme-sync.json" ]]; then
            echo "  ✓ IDE theme generated (works for both VS Code and Cursor)"
        fi
        
        echo ""
        echo "💡 The new theme is ready for use with IDE synchronization!"
        echo "   Switch to it with: omarchy-theme-set $THEME_NAME"
        
    else
        echo "❌ Failed to generate IDE themes for $THEME_NAME"
        echo "   You can manually generate them later with:"
        echo "   omarchy-theme-sync generate $THEME_NAME"
    fi
else
    echo "⚠️ Theme generator not found at: $GENERATOR"
    echo "   Please ensure Omarchy IDE Theme Sync is properly installed"
fi

echo "✨ Post-theme-install hook completed"
