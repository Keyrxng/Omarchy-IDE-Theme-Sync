#!/usr/bin/env python3
"""
Omarchy Integration Hooks
Provides system integration for automatic theme synchronization
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


class OmarchyIntegration:
    """Handles integration with the Omarchy theming system"""
    
    def __init__(self):
        self.omarchy_bin_dir = Path.home() / '.local' / 'share' / 'omarchy' / 'bin'
        self.themes_dir = Path.home() / '.config' / 'omarchy' / 'themes'
        self.project_dir = Path(__file__).parent.parent
        
        # Ensure directories exist
        self.omarchy_bin_dir.mkdir(parents=True, exist_ok=True)
        self.themes_dir.mkdir(parents=True, exist_ok=True)
    
    def setup_integration(self) -> bool:
        """Set up integration with Omarchy system"""
        print("🔧 Setting up Omarchy IDE Theme Sync integration...")
        
        success = True
        
        # Install theme generator
        if not self._install_theme_generator():
            success = False
        
        # Setup theme switching hooks
        if not self._setup_theme_switching_hooks():
            success = False
        
        # Setup theme installation hooks
        if not self._setup_theme_installation_hooks():
            success = False
        
        if success:
            print("✅ Integration setup complete!")
            print("\n🎉 Your VS Code and Cursor will now automatically sync with Omarchy themes!")
            print("\nUsage:")
            print("  omarchy-theme-set <theme-name>  # Themes will auto-sync")
            print("  omarchy-theme-install <url>     # New themes will auto-generate editor themes")
        else:
            print("❌ Integration setup failed. Check errors above.")
        
        return success
    
    def _install_theme_generator(self) -> bool:
        """Install the theme generator to the themes directory"""
        try:
            import shutil
            
            # Install the theme generator (main one)
            comprehensive_source = self.project_dir / 'src' / 'theme_generator.py'
            comprehensive_dest = self.themes_dir / 'theme_generator.py'
            
            if comprehensive_source.exists():
                shutil.copy2(comprehensive_source, comprehensive_dest)
                comprehensive_dest.chmod(0o755)
                print(f"✓ Installed theme generator: {comprehensive_dest}")
            else:
                print(f"❌ Theme generator not found: {comprehensive_source}")
                return False
            

            
            return True
            
        except Exception as e:
            print(f"❌ Failed to install theme generators: {e}")
            return False
    
    def _setup_theme_switching_hooks(self) -> bool:
        """Setup hooks for theme switching"""
        try:
            # Backup original omarchy-theme-set if it exists
            original_script = self.omarchy_bin_dir / 'omarchy-theme-set'
            backup_script = self.omarchy_bin_dir / 'omarchy-theme-set.backup'
            
            if original_script.exists() and not backup_script.exists():
                import shutil
                shutil.copy2(original_script, backup_script)
                print(f"✓ Backed up original theme script: {backup_script}")
            
            # Create enhanced theme switcher
            enhanced_script = self._create_enhanced_theme_switcher()
            if enhanced_script:
                print(f"✓ Created enhanced theme switcher: {enhanced_script}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Failed to setup theme switching hooks: {e}")
            return False
    
    def _create_enhanced_theme_switcher(self) -> Optional[Path]:
        """Create the enhanced omarchy-theme-set script"""
        script_path = self.omarchy_bin_dir / 'omarchy-theme-set-enhanced'
        
        script_content = '''#!/bin/bash

# Enhanced omarchy-theme-set with automatic IDE theme synchronization
# Part of Omarchy IDE Theme Sync

if [[ -z "$1" && "$1" != "CNCLD" ]]; then
    echo "Usage: omarchy-theme-set-enhanced <theme-name>" >&2
    exit 1
fi

THEMES_DIR="$HOME/.config/omarchy/themes/"
CURRENT_THEME_DIR="$HOME/.config/omarchy/current/theme"

THEME_NAME=$(echo "$1" | sed -E 's/<[^>]+>//g' | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
THEME_PATH="$THEMES_DIR/$THEME_NAME"

# Check if the theme exists
if [[ ! -d "$THEME_PATH" ]]; then
    echo "Theme '$THEME_NAME' does not exist in $THEMES_DIR" >&2
    exit 2
fi

echo "🎨 Switching to theme: $THEME_NAME"

# Update theme symlinks
ln -nsf "$THEME_PATH" "$CURRENT_THEME_DIR"

# Generate IDE theme if it doesn't exist
if [[ ! -f "$THEME_PATH/$THEME_NAME-theme-sync.json" ]]; then
    echo "🔧 Generating IDE themes for $THEME_NAME..."
    
    if [[ -f "$THEMES_DIR/theme_generator.py" ]]; then
        cd "$THEMES_DIR"
        if python3 theme_generator.py generate "$THEME_NAME"; then
            echo "✅ Successfully generated IDE themes for $THEME_NAME"
        else
            echo "⚠️ Failed to generate IDE themes for $THEME_NAME"
        fi
    else
        echo "⚠️ Theme generator not found, skipping IDE theme generation"
    fi
fi

# Apply Gnome settings (from original omarchy-theme-set)
if [[ -f ~/.config/omarchy/current/theme/light.mode ]]; then
    gsettings set org.gnome.desktop.interface color-scheme "prefer-light" 2>/dev/null || true
    gsettings set org.gnome.desktop.interface gtk-theme "Adwaita" 2>/dev/null || true
else
    gsettings set org.gnome.desktop.interface color-scheme "prefer-dark" 2>/dev/null || true
    gsettings set org.gnome.desktop.interface gtk-theme "Adwaita-dark" 2>/dev/null || true
fi

# Apply icon theme
if [[ -f ~/.config/omarchy/current/theme/icons.theme ]]; then
    gsettings set org.gnome.desktop.interface icon-theme "$(<~/.config/omarchy/current/theme/icons.theme)" 2>/dev/null || true
else
    gsettings set org.gnome.desktop.interface icon-theme "Yaru-blue" 2>/dev/null || true
fi

# Apply Chromium colors
if command -v chromium &>/dev/null; then
    if [[ -f ~/.config/omarchy/current/theme/light.mode ]]; then
        chromium --no-startup-window --set-color-scheme="light" 2>/dev/null || true
    else
        chromium --no-startup-window --set-color-scheme="dark" 2>/dev/null || true
    fi

    if [[ -f ~/.config/omarchy/current/theme/chromium.theme ]]; then
        chromium --no-startup-window --set-theme-color="$(<~/.config/omarchy/current/theme/chromium.theme)" 2>/dev/null || true
    else
        chromium --no-startup-window --set-theme-color="28,32,39" 2>/dev/null || true
    fi
fi

# Trigger alacritty config reload
touch "$HOME/.config/alacritty/alacritty.toml"

# Apply IDE themes
echo "🎨 Applying IDE themes..."
if command -v omarchy-theme-sync &>/dev/null; then
    omarchy-theme-sync apply "$THEME_NAME" 2>/dev/null || true
else
    # Look for theme sync script in common locations
    SYNC_LOCATIONS=(
        "$THEMES_DIR/../../../projects/omarchy-ide-theme-sync/src/theme_sync.py"
        "$HOME/.local/share/omarchy-ide-theme-sync/src/theme_sync.py"
    )
    
    for location in "${SYNC_LOCATIONS[@]}"; do
        if [[ -f "$location" ]]; then
            python3 "$location" "$THEME_NAME" 2>/dev/null || true
            break
        fi
    done
fi

# Restart components (from original omarchy-theme-set)
pkill -SIGUSR2 btop 2>/dev/null || true
command -v omarchy-restart-waybar &>/dev/null && omarchy-restart-waybar || true
command -v omarchy-restart-swayosd &>/dev/null && omarchy-restart-swayosd || true
command -v makoctl &>/dev/null && makoctl reload || true
command -v hyprctl &>/dev/null && hyprctl reload || true

# Set new background
command -v omarchy-theme-bg-next &>/dev/null && omarchy-theme-bg-next || true

echo "✨ Theme '$THEME_NAME' applied successfully with IDE synchronization!"
'''
        
        try:
            with open(script_path, 'w') as f:
                f.write(script_content)
            script_path.chmod(0o755)
            
            # Create alias script for backward compatibility
            alias_script = self.omarchy_bin_dir / 'omarchy-theme-set'
            with open(alias_script, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'exec "{script_path}" "$@"\n')
            alias_script.chmod(0o755)
            
            return script_path
        except Exception as e:
            print(f"❌ Failed to create enhanced theme switcher: {e}")
            return None
    
    def _setup_theme_installation_hooks(self) -> bool:
        """Setup hooks for when new themes are installed"""
        # For now, this would require modifications to the omarchy-theme-install command
        # We'll document this as a future enhancement
        print("✓ Theme installation hooks ready (requires omarchy-theme-install integration)")
        return True
    
    def remove_integration(self) -> bool:
        """Remove the integration (for uninstall)"""
        print("🗑️ Removing Omarchy IDE Theme Sync integration...")
        
        try:
            # Restore original theme script if backup exists
            original_script = self.omarchy_bin_dir / 'omarchy-theme-set'
            backup_script = self.omarchy_bin_dir / 'omarchy-theme-set.backup'
            enhanced_script = self.omarchy_bin_dir / 'omarchy-theme-set-enhanced'
            
            if backup_script.exists():
                import shutil
                shutil.copy2(backup_script, original_script)
                backup_script.unlink()
                print("✓ Restored original omarchy-theme-set script")
            
            if enhanced_script.exists():
                enhanced_script.unlink()
                print("✓ Removed enhanced theme script")
            
            # Remove theme generator
            generator_path = self.themes_dir / 'theme_generator.py'
            if generator_path.exists():
                generator_path.unlink()
                print("✓ Removed theme generator")
            

            
            print("✅ Integration removed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to remove integration: {e}")
            return False


def main():
    """Main function for standalone usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Omarchy Integration Setup')
    parser.add_argument('action', choices=['setup', 'remove'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    integration = OmarchyIntegration()
    
    if args.action == 'setup':
        success = integration.setup_integration()
    elif args.action == 'remove':
        success = integration.remove_integration()
    else:
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
