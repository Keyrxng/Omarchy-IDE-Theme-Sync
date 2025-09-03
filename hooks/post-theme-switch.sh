#!/bin/bash

# Post Theme Switch Hook for Omarchy IDE Theme Sync
# This script is called after a theme switch via Omarchy Menu > Style > Theme
# and is used to generate and apply IDE themes for the new theme

THEME_NAME="$1"
THEMES_DIR="$HOME/.config/omarchy/themes"
GENERATOR="$THEMES_DIR/theme_generator.py"

if [[ -z "$THEME_NAME" ]]; then
    echo "Error: No theme name provided to post-theme-switch hook"
    exit 1
fi

echo "🔄 Post-theme-switch hook: $THEME_NAME"

# Generate IDE theme if it doesn't exist
THEME_DIR="$THEMES_DIR/$THEME_NAME"
if [[ ! -f "$THEME_DIR/$THEME_NAME-theme-sync.json" ]]; then
    echo "🔧 Generating missing IDE themes for $THEME_NAME..."
    
    if [[ -f "$GENERATOR" ]]; then
        if python3 "$GENERATOR" generate "$THEME_NAME"; then
            echo "✅ Successfully generated IDE themes"
        else
            echo "⚠️ Failed to generate IDE themes"
        fi
    else
        echo "⚠️ Theme generator not found"
    fi
fi

# Apply the themes
echo "🎨 Applying IDE themes..."
# Look for theme sync script in common locations
SYNC_SCRIPT=""
POSSIBLE_LOCATIONS=(
    "$HOME/.local/bin/omarchy-theme-sync"
    "$HOME/projects/omarchy-ide-theme-sync/src/theme_sync.py"
    "/usr/local/bin/omarchy-theme-sync"
)

for location in "${POSSIBLE_LOCATIONS[@]}"; do
    if [[ -f "$location" ]]; then
        SYNC_SCRIPT="$location"
        break
    fi
done

if [[ -n "$SYNC_SCRIPT" ]]; then
    if [[ "$SYNC_SCRIPT" == *"omarchy-theme-sync" ]]; then
        if "$SYNC_SCRIPT" apply "$THEME_NAME"; then
            echo "✅ IDE themes applied successfully"
        else
            echo "⚠️ Failed to apply IDE themes"
        fi
    else
        if python3 "$SYNC_SCRIPT" "$THEME_NAME"; then
            echo "✅ IDE themes applied successfully"
        else
            echo "⚠️ Failed to apply IDE themes"
        fi
    fi
else
    echo "⚠️ Theme sync script not found"
fi

echo "✨ Post-theme-switch hook completed"
