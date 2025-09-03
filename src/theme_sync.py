#!/usr/bin/env python3
"""
Omarchy Theme Sync - Apply themes to VS Code and Cursor
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


class EditorThemeApplier:
    """Handles applying themes to different editors"""
    
    def __init__(self):
        self.vscode_config_dir = Path.home() / '.config' / 'Code' / 'User'
        self.cursor_config_dir = Path.home() / '.config' / 'Cursor' / 'User'
    
    def apply_themes(self, theme_name: Optional[str] = None) -> bool:
        """Apply themes to all supported editors"""
        if not theme_name:
            # Get current theme from symlink
            current_theme_link = Path.home() / '.config' / 'omarchy' / 'current' / 'theme'
            if current_theme_link.exists() and current_theme_link.is_symlink():
                theme_name = current_theme_link.readlink().name
            else:
                print("❌ No current theme found")
                return False
        
        print(f"🎨 Applying editor themes for: {theme_name}")
        
        theme_dir = Path.home() / '.config' / 'omarchy' / 'themes' / theme_name
        if not theme_dir.exists():
            print(f"❌ Theme directory not found: {theme_dir}")
            return False
        
        success = True
        
        # Apply VS Code theme
        if self._is_editor_available('code'):
            if self._apply_vscode_theme(theme_dir):
                print("✓ Applied VS Code theme")
            else:
                print("⚠ Failed to apply VS Code theme")
                success = False
        else:
            print("⚠ VS Code not found")
        
        # Apply Cursor theme
        if self._is_editor_available('cursor'):
            if self._apply_cursor_theme(theme_dir):
                print("✓ Applied Cursor theme")
            else:
                print("⚠ Failed to apply Cursor theme")
                success = False
        else:
            print("⚠ Cursor not found")
        
        return success
    
    def _is_editor_available(self, editor_command: str) -> bool:
        """Check if an editor is available in PATH"""
        return shutil.which(editor_command) is not None
    
    def _apply_vscode_theme(self, theme_dir: Path) -> bool:
        """Apply theme to VS Code"""
        theme_name = theme_dir.name
        theme_file = theme_dir / f'{theme_name}-theme-sync.json'
        if not theme_file.exists():
            print(f"⚠ Theme file not found: {theme_file}")
            return False
        
        try:
            # Ensure config directory exists
            self.vscode_config_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy theme file
            settings_file = self.vscode_config_dir / 'settings.json'
            shutil.copy2(theme_file, settings_file)
            
            return True
        except Exception as e:
            print(f"❌ Error applying VS Code theme: {e}")
            return False
    
    def _apply_cursor_theme(self, theme_dir: Path) -> bool:
        """Apply theme to Cursor"""
        theme_name = theme_dir.name
        theme_file = theme_dir / f'{theme_name}-theme-sync.json'
        if not theme_file.exists():
            print(f"⚠ Theme file not found: {theme_file}")
            return False
        
        try:
            # Ensure config directory exists
            self.cursor_config_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy theme file
            settings_file = self.cursor_config_dir / 'settings.json'
            shutil.copy2(theme_file, settings_file)
            
            return True
        except Exception as e:
            print(f"❌ Error applying Cursor theme: {e}")
            return False


def main():
    """Main function for standalone usage"""
    import sys
    
    applier = EditorThemeApplier()
    
    if len(sys.argv) > 1:
        theme_name = sys.argv[1]
        success = applier.apply_themes(theme_name)
    else:
        success = applier.apply_themes()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
