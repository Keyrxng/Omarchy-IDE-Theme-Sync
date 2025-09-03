#!/usr/bin/env python3
"""
Omarchy IDE Theme Generator
Generates VS Code and Cursor themes from Omarchy color schemes
"""

import json
import os
import sys
import argparse
from pathlib import Path
import re
import colorsys

# Constants for color calculations
GAMMA_THRESHOLD = 0.03928
GAMMA_OFFSET = 0.055
GAMMA_POWER = 2.4
GAMMA_DIVISOR = 12.92
GAMMA_DENOMINATOR = 1.055

# Luminance coefficients for sRGB
LUMINANCE_R = 0.2126
LUMINANCE_G = 0.7152
LUMINANCE_B = 0.0722

# Contrast ratio thresholds
MIN_READABLE_CONTRAST = 3.0
MIN_ACCEPTABLE_CONTRAST = 2.0


def normalize_hex_color(color_value):
    """Normalize hex color value to proper format for VSCode"""
    if not color_value:
        return None
    
    # Remove quotes and whitespace
    color_value = str(color_value).strip().strip('"\'')
    
    # Handle 0x prefix (from alacritty)
    if color_value.startswith('0x'):
        color_value = '#' + color_value[2:]
    
    # Ensure it starts with #
    if not color_value.startswith('#'):
        color_value = '#' + color_value
    
    # Validate hex format
    if len(color_value) == 4:  # #RGB -> #RRGGBB
        color_value = '#' + ''.join([c*2 for c in color_value[1:]])
    
    # Validate it's a proper hex color
    if len(color_value) != 7:
        return None
    
    try:
        int(color_value[1:], 16)  # Test if it's valid hex
        return color_value
    except ValueError:
        return None

def is_valid_hex_color(hex_color):
    """Check if a color is a valid hex color"""
    normalized = normalize_hex_color(hex_color)
    return normalized is not None

def calculate_contrast_ratio(color1, color2):
    """Calculate contrast ratio between two colors for accessibility"""
    def get_luminance(hex_color):
        """Calculate relative luminance of a color"""
        normalized = normalize_hex_color(hex_color)
        if not normalized:
            return 0
        
        try:
            r = int(normalized[1:3], 16) / 255.0
            g = int(normalized[3:5], 16) / 255.0
            b = int(normalized[5:7], 16) / 255.0
            
            # Apply gamma correction
            def gamma_correct(c):
                return c / GAMMA_DIVISOR if c <= GAMMA_THRESHOLD else pow((c + GAMMA_OFFSET) / GAMMA_DENOMINATOR, GAMMA_POWER)
            
            r = gamma_correct(r)
            g = gamma_correct(g)
            b = gamma_correct(b)
            
            return LUMINANCE_R * r + LUMINANCE_G * g + LUMINANCE_B * b
        except (ValueError, TypeError):
            return 0
    
    lum1 = get_luminance(color1)
    lum2 = get_luminance(color2)
    
    # Ensure the brighter color is in the numerator
    if lum1 > lum2:
        return (lum1 + 0.05) / (lum2 + 0.05)
    else:
        return (lum2 + 0.05) / (lum1 + 0.05)

def hex_to_hsv(hex_color):
    """Convert hex color to HSV for better color manipulation"""
    normalized = normalize_hex_color(hex_color)
    if not normalized:
        return (0, 0, 0)
    try:
        r = int(normalized[1:3], 16) / 255.0
        g = int(normalized[3:5], 16) / 255.0
        b = int(normalized[5:7], 16) / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return (h, s, v)
    except (ValueError, TypeError):
        return (0, 0, 0)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    normalized = normalize_hex_color(hex_color)
    if not normalized:
        return (0, 0, 0)
    try:
        r = int(normalized[1:3], 16)
        g = int(normalized[3:5], 16)
        b = int(normalized[5:7], 16)
        return (r, g, b)
    except (ValueError, TypeError):
        return (0, 0, 0)

def rgb_to_hex(r, g, b):
    """Convert RGB tuple to hex color"""
    return f"#{r:02x}{g:02x}{b:02x}"

def is_light_theme(background_color):
    """Determine if a theme is light or dark based on background color"""
    normalized = normalize_hex_color(background_color)
    if not normalized:
        return False  # Default to dark theme if color is invalid
    r, g, b = hex_to_rgb(normalized)
    # Calculate perceived brightness
    brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    return brightness > 0.5

def adjust_color_for_theme(hex_color, is_light, factor=0.1):
    """Adjust color based on whether it's a light or dark theme"""
    normalized = normalize_hex_color(hex_color)
    if not normalized:
        return hex_color  # Return original if can't normalize
    
    r, g, b = hex_to_rgb(normalized)
    
    if is_light:
        # For light themes, darken colors slightly
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
    else:
        # For dark themes, lighten colors slightly
        r = min(255, int(r * (1 + factor)))
        g = min(255, int(g * (1 + factor)))
        b = min(255, int(b * (1 + factor)))
    
    return rgb_to_hex(r, g, b)

def generate_ui_colors(colors, is_light):
    """Generate UI colors based on theme type"""
    bg = colors.get('background', '#1e1e2e')
    fg = colors.get('foreground', '#cdd6f4')
    normal = colors.get('normal', {})
    bright = colors.get('bright', {})
    
    if is_light:
        # Light theme: darker backgrounds for contrast
        side_bg = adjust_color_for_theme(bg, is_light, 0.15)
        panel_bg = adjust_color_for_theme(bg, is_light, 0.2)
        tab_bg = adjust_color_for_theme(bg, is_light, 0.1)
        input_bg = adjust_color_for_theme(bg, is_light, 0.05)
        list_bg = adjust_color_for_theme(bg, is_light, 0.1)
        hover_bg = adjust_color_for_theme(bg, is_light, 0.2)
        border_color = adjust_color_for_theme(bg, is_light, 0.3)
    else:
        # Dark theme: lighter backgrounds for contrast
        side_bg = adjust_color_for_theme(bg, is_light, 0.1)
        panel_bg = adjust_color_for_theme(bg, is_light, 0.15)
        tab_bg = adjust_color_for_theme(bg, is_light, 0.05)
        input_bg = adjust_color_for_theme(bg, is_light, 0.05)
        list_bg = adjust_color_for_theme(bg, is_light, 0.1)
        hover_bg = adjust_color_for_theme(bg, is_light, 0.15)
        border_color = adjust_color_for_theme(bg, is_light, 0.2)
    
    return {
        'side_bg': side_bg,
        'panel_bg': panel_bg,
        'tab_bg': tab_bg,
        'input_bg': input_bg,
        'list_bg': list_bg,
        'hover_bg': hover_bg,
        'border_color': border_color
    }

def validate_and_fix_colors(colors):
    """Validate and fix color values, providing fallbacks for invalid colors"""
    # Default fallback colors
    fallback_colors = {
        'background': '#282a36',
        'foreground': '#f8f8f2',
        'normal': {
            'black': '#21222c',
            'red': '#ff5555',
            'green': '#50fa7b',
            'yellow': '#f1fa8c',
            'blue': '#bd93f9',
            'magenta': '#ff79c6',
            'cyan': '#8be9fd',
            'white': '#f8f8f2'
        },
        'bright': {
            'black': '#6272a4',
            'red': '#ff6e6e',
            'green': '#69ff94',
            'yellow': '#ffffa5',
            'blue': '#d6acff',
            'magenta': '#ff92df',
            'cyan': '#a4ffff',
            'white': '#ffffff'
        }
    }
    
    fixed_colors = {}
    issues_found = []
    
    # Validate and fix primary colors
    for key in ['background', 'foreground', 'cursor']:
        if key in colors:
            normalized = normalize_hex_color(colors[key])
            if normalized:
                fixed_colors[key] = normalized
            else:
                fixed_colors[key] = fallback_colors.get(key, fallback_colors['background'])
                issues_found.append(f"Invalid {key} color '{colors[key]}' - using fallback")
        else:
            # Special handling for cursor color - derive from foreground if available
            if key == 'cursor' and 'foreground' in fixed_colors:
                fixed_colors[key] = fixed_colors['foreground']
                issues_found.append(f"Missing {key} color - derived from foreground")
            else:
                fixed_colors[key] = fallback_colors.get(key, fallback_colors['background'])
                issues_found.append(f"Missing {key} color - using fallback")
    
    # Validate and fix normal colors
    fixed_colors['normal'] = {}
    normal_colors = colors.get('normal', {})
    for color_name in ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']:
        if color_name in normal_colors:
            normalized = normalize_hex_color(normal_colors[color_name])
            if normalized:
                fixed_colors['normal'][color_name] = normalized
            else:
                fixed_colors['normal'][color_name] = fallback_colors['normal'][color_name]
                issues_found.append(f"Invalid normal.{color_name} color '{normal_colors[color_name]}' - using fallback")
        else:
            fixed_colors['normal'][color_name] = fallback_colors['normal'][color_name]
            issues_found.append(f"Missing normal.{color_name} color - using fallback")
    
    # Validate and fix bright colors
    fixed_colors['bright'] = {}
    bright_colors = colors.get('bright', {})
    for color_name in ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']:
        if color_name in bright_colors:
            normalized = normalize_hex_color(bright_colors[color_name])
            if normalized:
                fixed_colors['bright'][color_name] = normalized
            else:
                fixed_colors['bright'][color_name] = fallback_colors['bright'][color_name]
                issues_found.append(f"Invalid bright.{color_name} color '{bright_colors[color_name]}' - using fallback")
        else:
            fixed_colors['bright'][color_name] = fallback_colors['bright'][color_name]
            issues_found.append(f"Missing bright.{color_name} color - using fallback")
    
    # Check contrast ratios for readability
    bg_color = fixed_colors['background']
    fg_color = fixed_colors['foreground']
    contrast = calculate_contrast_ratio(bg_color, fg_color)
    
    if contrast < MIN_READABLE_CONTRAST:  # Minimum readable contrast
        issues_found.append(f"Low contrast ratio ({contrast:.2f}) between background and foreground")
        # If contrast is too low, use fallback colors
        if contrast < MIN_ACCEPTABLE_CONTRAST:
            fixed_colors['background'] = fallback_colors['background']
            fixed_colors['foreground'] = fallback_colors['foreground']
            issues_found.append("Applied fallback colors due to extremely low contrast")
    
    return fixed_colors, issues_found

def parse_alacritty_colors(alacritty_file):
    """Parse alacritty.toml and extract color information"""
    colors = {}
    
    try:
        with open(alacritty_file, 'r') as f:
            content = f.read()
            
        # Extract primary colors
        primary_match = re.search(r'background\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if primary_match:
            colors['background'] = primary_match.group(1)
            
        primary_match = re.search(r'foreground\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if primary_match:
            colors['foreground'] = primary_match.group(1)
            
        # Extract normal colors
        normal_colors = {}
        normal_section = re.search(r'\[colors\.normal\](.*?)(?=\[|$)', content, re.DOTALL)
        if normal_section:
            for line in normal_section.group(1).split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    if key and value and not key.startswith('#'):
                        normal_colors[key] = value
        colors['normal'] = normal_colors
        
        # Extract bright colors
        bright_colors = {}
        bright_section = re.search(r'\[colors\.bright\](.*?)(?=\[|$)', content, re.DOTALL)
        if bright_section:
            for line in bright_section.group(1).split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    if key and value and not key.startswith('#'):
                        bright_colors[key] = value
        colors['bright'] = bright_colors
        
        # Extract cursor colors
        cursor_match = re.search(r'cursor\s*=\s*[\'"]([^\'"]+)[\'"]', content)
        if cursor_match:
            colors['cursor'] = cursor_match.group(1)
            
    except Exception as e:
        print(f"Error parsing {alacritty_file}: {e}")
        
    return colors

def generate_vscode_theme(theme_name, colors):
    """Generate a VS Code theme from colors"""
    
    # Determine if this is a light or dark theme
    is_light = is_light_theme(colors.get('background', '#1e1e2e'))
    
    # Extract base colors
    bg = colors.get('background', '#1e1e2e')
    fg = colors.get('foreground', '#cdd6f4')
    normal = colors.get('normal', {})
    bright = colors.get('bright', {})
    cursor = colors.get('cursor', fg)
    
    # Generate UI colors
    ui_colors = generate_ui_colors(colors, is_light)
    
    # Create theme covering all UI elements
    theme = {
        "workbench.colorTheme": theme_name,
        "workbench.colorCustomizations": {
            # ===== EDITOR =====
            "editor.background": bg,
            "editor.foreground": fg,
            "editor.emptyBackground": bg,
            "editor.lineHighlightBackground": ui_colors['list_bg'],
            "editor.selectionBackground": ui_colors['tab_bg'],
            "editor.findMatchBackground": normal.get('green', '#50fa7b'),
            "editor.findMatchHighlightBackground": ui_colors['hover_bg'],
            "editorCursor.foreground": cursor,
            "editorWhitespace.foreground": normal.get('black', '#6272a4'),
            "editorIndentGuide.background": ui_colors['border_color'],
            "editorIndentGuide.activeBackground": normal.get('green', '#50fa7b'),
            "editor.lineHighlightBorder": ui_colors['border_color'],
            "editor.rangeHighlightBackground": ui_colors['hover_bg'],
            "editor.symbolHighlightBackground": ui_colors['hover_bg'],
            "editor.wordHighlightBackground": ui_colors['hover_bg'],
            "editor.wordHighlightStrongBackground": ui_colors['tab_bg'],
            "editorBracketMatch.background": ui_colors['border_color'],
            "editorBracketMatch.border": normal.get('blue', '#8be9fd'),
            "editorCodeLens.foreground": normal.get('black', '#6272a4'),
            "editorError.foreground": normal.get('red', '#ff5555'),
            "editorWarning.foreground": normal.get('yellow', '#f1fa8c'),
            "editorInfo.foreground": normal.get('blue', '#8be9fd'),
            "editorHint.foreground": normal.get('green', '#50fa7b'),
            "editorGutter.background": bg,
            "editorGutter.modifiedBackground": normal.get('yellow', '#f1fa8c'),
            "editorGutter.addedBackground": normal.get('green', '#50fa7b'),
            "editorGutter.deletedBackground": normal.get('red', '#ff5555'),
            "editorUnnecessaryCode.opacity": "0.4",
            "editorSuggestWidget.background": ui_colors['input_bg'],
            "editorSuggestWidget.border": ui_colors['border_color'],
            "editorSuggestWidget.selectedBackground": ui_colors['list_bg'],
            "editorSuggestWidget.highlightForeground": normal.get('blue', '#8be9fd'),
            "editorHoverWidget.background": ui_colors['input_bg'],
            "editorHoverWidget.border": ui_colors['border_color'],
            
            # ===== EDITOR GROUP =====
            "editorGroup.background": bg,
            "editorGroup.border": ui_colors['border_color'],
            "editorGroupHeader.background": ui_colors['side_bg'],
            "editorGroupHeader.tabsBackground": ui_colors['side_bg'],
            "editorGroupHeader.tabsBorder": ui_colors['border_color'],
            "editorGroupHeader.noTabsBackground": ui_colors['side_bg'],
            
            # ===== BREADCRUMBS =====
            "breadcrumb.background": bg,
            "breadcrumb.foreground": fg,
            "breadcrumb.focusForeground": normal.get('blue', '#8be9fd'),
            "breadcrumb.activeSelectionForeground": fg,
            "breadcrumbPicker.background": ui_colors['input_bg'],
            "breadcrumbPicker.foreground": fg,
            
            # ===== SIDEBAR =====
            "sideBar.background": ui_colors['side_bg'],
            "sideBar.foreground": fg,
            "sideBarTitle.foreground": fg,
            "sideBarSectionHeader.background": ui_colors['border_color'],
            "sideBarSectionHeader.foreground": fg,
            
            # ===== ACTIVITY BAR =====
            "activityBar.background": ui_colors['side_bg'],
            "activityBar.foreground": fg,
            "activityBar.activeBorder": normal.get('blue', '#8be9fd'),
            "activityBar.activeBackground": ui_colors['hover_bg'],
            "activityBar.inactiveForeground": normal.get('black', '#6272a4'),
            "activityBarBadge.background": normal.get('red', '#ff5555'),
            "activityBarBadge.foreground": bg,
            
            # ===== STATUS BAR =====
            "statusBar.background": ui_colors['side_bg'],
            "statusBar.foreground": fg,
            "statusBar.debuggingBackground": normal.get('red', '#ff5555'),
            "statusBar.debuggingForeground": fg,
            "statusBar.noFolderBackground": ui_colors['side_bg'],
            "statusBar.noFolderForeground": fg,
            "statusBarItem.prominentBackground": ui_colors['tab_bg'],
            "statusBarItem.prominentForeground": fg,
            "statusBarItem.hoverBackground": ui_colors['hover_bg'],
            "statusBarItem.errorBackground": normal.get('red', '#ff5555'),
            "statusBarItem.errorForeground": fg,
            "statusBarItem.warningBackground": normal.get('yellow', '#f1fa8c'),
            "statusBarItem.warningForeground": bg,
            
            # ===== TITLE BAR =====
            "titleBar.activeBackground": ui_colors['side_bg'],
            "titleBar.activeForeground": fg,
            "titleBar.inactiveBackground": ui_colors['panel_bg'],
            "titleBar.inactiveForeground": normal.get('black', '#6272a4'),
            
            # ===== TABS =====
            "tab.activeBackground": ui_colors['tab_bg'],
            "tab.activeForeground": fg,
            "tab.inactiveBackground": ui_colors['side_bg'],
            "tab.inactiveForeground": normal.get('black', '#6272a4'),
            "tab.border": ui_colors['border_color'],
            "tab.activeBorder": normal.get('blue', '#8be9fd'),
            "tab.hoverBackground": ui_colors['hover_bg'],
            "tab.hoverForeground": fg,
            "tab.unfocusedActiveBackground": ui_colors['tab_bg'],
            "tab.unfocusedActiveForeground": normal.get('black', '#6272a4'),
            "tab.unfocusedInactiveBackground": ui_colors['side_bg'],
            "tab.unfocusedInactiveForeground": normal.get('black', '#6272a4'),
            
            # ===== PANEL =====
            "panel.background": ui_colors['panel_bg'],
            "panel.foreground": fg,
            "panel.border": ui_colors['border_color'],
            "panelTitle.activeForeground": fg,
            "panelTitle.inactiveForeground": normal.get('black', '#6272a4'),
            "panelTitle.activeBorder": normal.get('blue', '#8be9fd'),
            
            # ===== TERMINAL =====
            "terminal.background": bg,
            "terminal.foreground": fg,
            "terminal.ansiBlack": normal.get('black', '#000000'),
            "terminal.ansiRed": normal.get('red', '#ff5555'),
            "terminal.ansiGreen": normal.get('green', '#50fa7b'),
            "terminal.ansiYellow": normal.get('yellow', '#f1fa8c'),
            "terminal.ansiBlue": normal.get('blue', '#bd93f9'),
            "terminal.ansiMagenta": normal.get('magenta', '#ff79c6'),
            "terminal.ansiCyan": normal.get('cyan', '#8be9fd'),
            "terminal.ansiWhite": normal.get('white', '#f8f8f2'),
            "terminal.ansiBrightBlack": bright.get('black', '#6272a4'),
            "terminal.ansiBrightRed": bright.get('red', '#ff6e6e'),
            "terminal.ansiBrightGreen": bright.get('green', '#69ff94'),
            "terminal.ansiBrightYellow": bright.get('yellow', '#ffffa5'),
            "terminal.ansiBrightBlue": bright.get('blue', '#d6acff'),
            "terminal.ansiBrightMagenta": bright.get('magenta', '#ff92df'),
            "terminal.ansiBrightCyan": bright.get('cyan', '#a4ffff'),
            "terminal.ansiBrightWhite": bright.get('white', '#ffffff'),
            "terminal.border": ui_colors['border_color'],
            "terminalCursor.background": cursor,
            "terminalCursor.foreground": bg,
            
            # ===== INPUT =====
            "input.background": ui_colors['input_bg'],
            "input.foreground": fg,
            "input.border": ui_colors['border_color'],
            "input.placeholderForeground": normal.get('black', '#6272a4'),
            "inputOption.activeBorder": normal.get('blue', '#8be9fd'),
            "inputValidation.infoBackground": normal.get('blue', '#8be9fd'),
            "inputValidation.infoBorder": normal.get('blue', '#8be9fd'),
            "inputValidation.warningBackground": normal.get('yellow', '#f1fa8c'),
            "inputValidation.warningBorder": normal.get('yellow', '#f1fa8c'),
            "inputValidation.errorBackground": normal.get('red', '#ff5555'),
            "inputValidation.errorBorder": normal.get('red', '#ff5555'),
            
            # ===== DROPDOWN =====
            "dropdown.background": ui_colors['input_bg'],
            "dropdown.foreground": fg,
            "dropdown.border": ui_colors['border_color'],
            "dropdown.listBackground": ui_colors['input_bg'],
            
            # ===== LISTS =====
            "list.activeSelectionBackground": ui_colors['list_bg'],
            "list.activeSelectionForeground": fg,
            "list.hoverBackground": ui_colors['hover_bg'],
            "list.hoverForeground": fg,
            "list.focusBackground": ui_colors['list_bg'],
            "list.focusForeground": fg,
            "list.inactiveSelectionBackground": ui_colors['list_bg'],
            "list.inactiveSelectionForeground": fg,
            "list.inactiveFocusBackground": ui_colors['list_bg'],
            "list.inactiveFocusForeground": fg,
            "list.warningForeground": normal.get('yellow', '#f1fa8c'),
            "list.errorForeground": normal.get('red', '#ff5555'),
            "list.infoForeground": normal.get('blue', '#8be9fd'),
            "list.highlightForeground": normal.get('blue', '#8be9fd'),
            "list.deemphasizedForeground": normal.get('black', '#6272a4'),
            
            # ===== AI COMPONENTS =====
            # AI prompt interfaces
            "ai-prompt-bar.background": ui_colors['input_bg'],
            "ai-prompt-bar.foreground": fg,
            "ai-prompt-bar.border": normal.get('blue', '#8be9fd'),
            "ai-prompt-bar.button.background": ui_colors['list_bg'],
            "ai-prompt-bar.button.foreground": fg,
            "ai-prompt-bar.button.hoverBackground": ui_colors['hover_bg'],
            "ai-prompt-bar.button.keep.background": normal.get('green', '#50fa7b'),
            "ai-prompt-bar.button.keep.foreground": bg,
            
            # ===== CHAT INTERFACE =====
            "chat.background": ui_colors['side_bg'],
            "chat.foreground": fg,
            "chat.border": normal.get('blue', '#8be9fd'),
            "chat.requestBackground": ui_colors['input_bg'],
            "chat.responseBackground": ui_colors['list_bg'],
            
            # ===== BUTTONS =====
            "button.background": ui_colors['input_bg'],
            "button.foreground": fg,
            "button.hoverBackground": ui_colors['hover_bg'],
            "button.border": ui_colors['border_color'],
            "button.secondaryBackground": ui_colors['panel_bg'],
            "button.secondaryForeground": fg,
            "button.secondaryHoverBackground": ui_colors['hover_bg'],
            "button.prominentBackground": normal.get('blue', '#8be9fd'),
            "button.prominentForeground": bg,
            "button.prominentHoverBackground": bright.get('blue', '#d6acff'),
            
            # ===== SCROLLBARS =====
            "scrollbarSlider.background": ui_colors['border_color'],
            "scrollbarSlider.hoverBackground": normal.get('black', '#6272a4'),
            "scrollbarSlider.activeBackground": normal.get('blue', '#8be9fd'),
            
            # ===== FOCUS AND BORDERS =====
            "focusBorder": normal.get('blue', '#8be9fd'),
            "contrastBorder": ui_colors['border_color'],
            "contrastActiveBorder": normal.get('blue', '#8be9fd'),
            
            # ===== ADDITIONAL UI ELEMENTS =====
            "foreground": fg,
            "disabledForeground": normal.get('black', '#6272a4'),
            "errorForeground": normal.get('red', '#ff5555'),
            "descriptionForeground": normal.get('black', '#6272a4'),
            
            # ===== WIDGETS =====
            "widget.background": ui_colors['input_bg'],
            "widget.foreground": fg,
            "widget.border": ui_colors['border_color'],
            "widget.shadow": "#00000040",
            
            # ===== EDITOR WIDGETS =====
            "editorWidget.background": ui_colors['input_bg'],
            "editorWidget.foreground": fg,
            "editorWidget.border": ui_colors['border_color'],
            "editorWidget.resizeBorder": normal.get('blue', '#8be9fd'),
            
            # ===== INPUT OPTIONS =====
            "inputOption.activeBackground": normal.get('blue', '#8be9fd'),
            "inputOption.activeForeground": bg,
            "inputOption.activeBorder": normal.get('blue', '#8be9fd'),
            "inputOption.hoverBackground": ui_colors['hover_bg'],
            
            # ===== SELECTION =====
            "selection.background": normal.get('blue', '#8be9fd'),
            
            # ===== EDITOR LINE NUMBERS =====
            "editorLineNumber.foreground": normal.get('black', '#6272a4'),
            "editorLineNumber.activeForeground": fg,
            "editorLineNumber.background": bg,
            
            # ===== ACTION ITEMS AND LABELS =====
            # Action item menu entries
            "actionItem.background": ui_colors['input_bg'],
            "actionItem.foreground": fg,
            "actionItem.border": ui_colors['border_color'],
            "actionItem.hoverBackground": ui_colors['hover_bg'],
            "actionItem.hoverForeground": fg,
            "actionItem.activeBackground": ui_colors['list_bg'],
            "actionItem.activeForeground": fg,
            "actionItem.disabledForeground": normal.get('black', '#6272a4'),
            
            # Action labels (button-like elements)
            "actionLabel.background": ui_colors['input_bg'],
            "actionLabel.foreground": fg,
            "actionLabel.border": ui_colors['border_color'],
            "actionLabel.hoverBackground": ui_colors['hover_bg'],
            "actionLabel.hoverForeground": fg,
            "actionLabel.activeBackground": ui_colors['list_bg'],
            "actionLabel.activeForeground": fg,
            "actionLabel.disabledForeground": normal.get('black', '#6272a4'),
            
            # Menu entries
            "menuEntry.background": ui_colors['input_bg'],
            "menuEntry.foreground": fg,
            "menuEntry.border": ui_colors['border_color'],
            "menuEntry.hoverBackground": ui_colors['hover_bg'],
            "menuEntry.hoverForeground": fg,
            "menuEntry.activeBackground": ui_colors['list_bg'],
            "menuEntry.activeForeground": fg,
            "menuEntry.disabledForeground": normal.get('black', '#6272a4'),
            
            # Outline elements and icons
            "outlineElement.background": ui_colors['side_bg'],
            "outlineElement.foreground": fg,
            "outlineElement.border": ui_colors['border_color'],
            "outlineElement.hoverBackground": ui_colors['hover_bg'],
            "outlineElement.hoverForeground": fg,
            "outlineElement.activeBackground": ui_colors['list_bg'],
            "outlineElement.activeForeground": fg,
            "outlineElement.icon": normal.get('blue', '#8be9fd'),
            "outlineElement.activeIcon": normal.get('cyan', '#8be9fd'),
            "outlineElement.inactiveIcon": normal.get('black', '#6272a4'),
            
            # ===== CODICON ELEMENTS =====
            # Codicon symbols (outline icons)
            "codicon.foreground": normal.get('blue', '#8be9fd'),
            "codicon.activeForeground": normal.get('cyan', '#8be9fd'),
            "codicon.inactiveForeground": normal.get('black', '#6272a4'),
            "codicon.hoverForeground": normal.get('cyan', '#8be9fd'),
            "codicon.disabledForeground": normal.get('black', '#6272a4'),
            
            # Specific codicon symbol types
            "codicon.symbolClass": normal.get('cyan', '#8be9fd'),
            "codicon.symbolMethod": normal.get('green', '#50fa7b'),
            "codicon.symbolFunction": normal.get('green', '#50fa7b'),
            "codicon.symbolVariable": normal.get('blue', '#8be9fd'),
            "codicon.symbolInterface": normal.get('cyan', '#8be9fd'),
            "codicon.symbolModule": normal.get('cyan', '#8be9fd'),
            "codicon.symbolProperty": normal.get('blue', '#8be9fd'),
            "codicon.symbolEnum": normal.get('yellow', '#f1fa8c'),
            "codicon.symbolKeyword": normal.get('magenta', '#ff79c6'),
            "codicon.symbolSnippet": normal.get('green', '#50fa7b'),
            "codicon.symbolColor": normal.get('magenta', '#ff79c6'),
            "codicon.symbolFile": normal.get('cyan', '#8be9fd'),
            "codicon.symbolReference": normal.get('blue', '#8be9fd'),
            "codicon.symbolFolder": normal.get('blue', '#8be9fd'),
            "codicon.symbolTypeParameter": normal.get('cyan', '#8be9fd'),
            "codicon.symbolUnit": normal.get('yellow', '#f1fa8c'),
            "codicon.symbolValue": normal.get('yellow', '#f1fa8c'),
            "codicon.symbolEnum": normal.get('yellow', '#f1fa8c'),
            "codicon.symbolStruct": normal.get('cyan', '#8be9fd'),
            "codicon.symbolEvent": normal.get('red', '#ff5555'),
            "codicon.symbolOperator": normal.get('red', '#ff5555'),
            "codicon.symbolTypeParameter": normal.get('cyan', '#8be9fd'),
            
            # ===== ICON COLORS =====
            # General icon colors for various UI elements
            "icon.foreground": normal.get('blue', '#8be9fd'),
            "icon.activeForeground": normal.get('cyan', '#8be9fd'),
            "icon.inactiveForeground": normal.get('black', '#6272a4'),
            "icon.hoverForeground": normal.get('cyan', '#8be9fd'),
            "icon.disabledForeground": normal.get('black', '#6272a4'),
            "icon.warningForeground": normal.get('yellow', '#f1fa8c'),
            "icon.errorForeground": normal.get('red', '#ff5555'),
            "icon.successForeground": normal.get('green', '#50fa7b'),
            "icon.infoForeground": normal.get('blue', '#8be9fd'),
            
            # ===== SYMBOL ICON THEMING =====
            # Icon theming for various symbol types
            "symbolIcon.arrayForeground": normal.get('yellow', '#f1fa8c'),
            "symbolIcon.booleanForeground": normal.get('blue', '#8be9fd'),
            "symbolIcon.classForeground": normal.get('cyan', '#8be9fd'),
            "symbolIcon.colorForeground": normal.get('magenta', '#ff79c6'),
            "symbolIcon.constantForeground": normal.get('yellow', '#f1fa8c'),
            "symbolIcon.constructorForeground": normal.get('green', '#50fa7b'),
            "symbolIcon.enumeratorForeground": normal.get('yellow', '#f1fa8c'),
            "symbolIcon.enumeratorMemberForeground": normal.get('blue', '#8be9fd'),
            "symbolIcon.eventForeground": normal.get('red', '#ff5555'),
            "symbolIcon.fieldForeground": normal.get('blue', '#8be9fd'),
            "symbolIcon.fileForeground": normal.get('cyan', '#8be9fd'),
            "symbolIcon.folderForeground": normal.get('blue', '#8be9fd'),
            "symbolIcon.functionForeground": normal.get('green', '#50fa7b'),
            "symbolIcon.interfaceForeground": normal.get('cyan', '#8be9fd'),
            "symbolIcon.keyForeground": normal.get('blue', '#8be9fd'),
            "symbolIcon.keywordForeground": normal.get('magenta', '#ff79c6'),
            "symbolIcon.methodForeground": normal.get('green', '#50fa7b'),
            "symbolIcon.moduleForeground": normal.get('cyan', '#8be9fd'),
            "symbolIcon.namespaceForeground": normal.get('cyan', '#8be9fd'),
            "symbolIcon.nullForeground": normal.get('red', '#ff5555'),
            "symbolIcon.numberForeground": normal.get('yellow', '#f1fa8c'),
            "symbolIcon.objectForeground": normal.get('blue', '#8be9fd'),
            "symbolIcon.operatorForeground": normal.get('red', '#ff5555'),
            "symbolIcon.packageForeground": normal.get('cyan', '#8be9fd'),
            "symbolIcon.propertyForeground": normal.get('blue', '#8be9fd'),
            "symbolIcon.referenceForeground": normal.get('blue', '#8be9fd'),
            "symbolIcon.snippetForeground": normal.get('green', '#50fa7b'),
            "symbolIcon.stringForeground": normal.get('green', '#50fa7b'),
            "symbolIcon.structForeground": normal.get('cyan', '#8be9fd'),
            "symbolIcon.textForeground": fg,
            "symbolIcon.typeParameterForeground": normal.get('cyan', '#8be9fd'),
            "symbolIcon.unitForeground": normal.get('yellow', '#f1fa8c'),
            "symbolIcon.variableForeground": normal.get('blue', '#8be9fd'),
            
            # ===== DEBUG ICONS =====
            "debugIcon.startForeground": normal.get('green', '#50fa7b'),
            "debugIcon.pauseForeground": normal.get('yellow', '#f1fa8c'),
            "debugIcon.stopForeground": normal.get('red', '#ff5555'),
            "debugIcon.disconnectForeground": normal.get('red', '#ff5555'),
            "debugIcon.restartForeground": normal.get('green', '#50fa7b'),
            "debugIcon.stepOverForeground": normal.get('blue', '#8be9fd'),
            "debugIcon.stepIntoForeground": normal.get('blue', '#8be9fd'),
            "debugIcon.stepOutForeground": normal.get('blue', '#8be9fd'),
            "debugIcon.continueForeground": normal.get('green', '#50fa7b'),
            "debugIcon.stepBackForeground": normal.get('blue', '#8be9fd'),
            
            # ===== PROBLEM ICONS =====
            "problemsErrorIcon.foreground": normal.get('red', '#ff5555'),
            "problemsWarningIcon.foreground": normal.get('yellow', '#f1fa8c'),
            "problemsInfoIcon.foreground": normal.get('blue', '#8be9fd'),
            
            # ===== TREE ICONS =====
            "tree.expandIcon": normal.get('blue', '#8be9fd'),
            "tree.collapseIcon": normal.get('blue', '#8be9fd'),
            
            # ===== COMMENTS ICONS =====
            "commentsView.resolvedIcon": normal.get('green', '#50fa7b'),
            "commentsView.unresolvedIcon": normal.get('blue', '#8be9fd'),
        },
        "editor.tokenColorCustomizations": {
            "textMateRules": [
                {
                    "scope": ["comment", "punctuation.definition.comment", "comment.line", "comment.block"],
                    "settings": {
                        "foreground": normal.get('black', '#6272a4')
                    }
                },
                {
                    "scope": ["string", "string.quoted", "string.quoted.single", "string.quoted.double"],
                    "settings": {
                        "foreground": normal.get('green', '#50fa7b')
                    }
                },
                {
                    "scope": ["constant.numeric", "constant.numeric.integer", "constant.numeric.float"],
                    "settings": {
                        "foreground": normal.get('yellow', '#f1fa8c')
                    }
                },
                {
                    "scope": ["constant.language", "constant.character", "constant.character.escape"],
                    "settings": {
                        "foreground": normal.get('red', '#ff5555')
                    }
                },
                {
                    "scope": ["variable", "variable.other", "variable.parameter"],
                    "settings": {
                        "foreground": fg
                    }
                },
                {
                    "scope": ["keyword", "storage.type", "storage.modifier", "storage.class"],
                    "settings": {
                        "foreground": normal.get('magenta', '#ff79c6')
                    }
                },
                {
                    "scope": ["entity.name.function", "support.function", "meta.function-call"],
                    "settings": {
                        "foreground": normal.get('blue', '#8be9fd')
                    }
                },
                {
                    "scope": ["entity.name.class", "entity.name.type", "support.class"],
                    "settings": {
                        "foreground": normal.get('cyan', '#8be9fd')
                    }
                },
                {
                    "scope": ["entity.name.tag", "support.type"],
                    "settings": {
                        "foreground": normal.get('green', '#50fa7b')
                    }
                },
                {
                    "scope": ["punctuation.definition.string", "punctuation.definition.parameters"],
                    "settings": {
                        "foreground": normal.get('black', '#6272a4')
                    }
                }
            ]
        }
    }
    
    return theme

def generate_theme_for_name(theme_name, themes_dir=None):
    """Generate theme for a specific theme name"""
    if themes_dir is None:
        themes_dir = Path.home() / '.config' / 'omarchy' / 'themes'
    else:
        themes_dir = Path(themes_dir)
    
    theme_dir = themes_dir / theme_name
    
    if not theme_dir.exists():
        print(f"Theme '{theme_name}' not found!")
        return False
    
    alacritty_file = theme_dir / "alacritty.toml"
    if not alacritty_file.exists():
        print(f"alacritty.toml not found in theme '{theme_name}'!")
        return False
    
    print(f"Generating theme for: {theme_name}")
    
    # Parse colors from alacritty.toml
    raw_colors = parse_alacritty_colors(alacritty_file)
    
    # Validate and fix colors
    colors, issues = validate_and_fix_colors(raw_colors)
    
    # Report any color issues found
    if issues:
        print(f"⚠️  Color validation issues found in {theme_name}:")
        for issue in issues:
            print(f"   - {issue}")
        print("   These issues have been automatically fixed with fallback colors.")
    
    # Generate VS Code theme
    vscode_theme = generate_vscode_theme(theme_name, colors)
    
    # Save only the unified theme file
    theme_sync_file = theme_dir / f'{theme_name}-theme-sync.json'
    with open(theme_sync_file, 'w') as f:
        json.dump(vscode_theme, f, indent=2)
    
    print(f"✓ Generated theme: {theme_sync_file}")
    print(f"✓ Theme includes {len(vscode_theme['workbench.colorCustomizations'])} color customizations")
    
    # Show theme type
    is_light = is_light_theme(colors.get('background', '#1e1e2e'))
    theme_type = "LIGHT" if is_light else "DARK"
    print(f"✓ Theme type: {theme_type}")
    
    return True

def generate_all_themes(themes_dir=None):
    """Generate themes for all available themes"""
    if themes_dir is None:
        themes_dir = Path.home() / '.config' / 'omarchy' / 'themes'
    else:
        themes_dir = Path(themes_dir)
    
    print("🎨 Generating themes for all Omarchy themes...")
    
    if not themes_dir.exists():
        print(f"Themes directory not found: {themes_dir}")
        return False
    
    theme_dirs = [d for d in themes_dir.iterdir() if d.is_dir() and (d / "alacritty.toml").exists()]
    
    if not theme_dirs:
        print("No themes found")
        return False
    
    success_count = 0
    for theme_dir in theme_dirs:
        theme_name = theme_dir.name
        if generate_theme_for_name(theme_name, themes_dir):
            success_count += 1
        print()  # Empty line between themes
    
    print(f"🎉 Generated themes for {success_count}/{len(theme_dirs)} themes")
    return success_count == len(theme_dirs)

def check_theme_status(themes_dir=None):
    """Check the status of all themes"""
    if themes_dir is None:
        themes_dir = Path.home() / '.config' / 'omarchy' / 'themes'
    else:
        themes_dir = Path(themes_dir)
    
    if not themes_dir.exists():
        print(f"Themes directory not found: {themes_dir}")
        return
    
    theme_dirs = [d for d in themes_dir.iterdir() if d.is_dir() and (d / "alacritty.toml").exists()]
    
    print("🎨 Theme Status Report")
    print("=" * 50)
    
    complete_count = 0
    for theme_dir in theme_dirs:
        theme_name = theme_dir.name
        has_theme = (theme_dir / f'{theme_name}-theme-sync.json').exists()
        
        if has_theme:
            print(f"✅ {theme_name} - Complete")
            complete_count += 1
        else:
            print(f"❌ {theme_name} - Missing")
    
    print(f"\n📊 {complete_count}/{len(theme_dirs)} themes complete")

def main():
    parser = argparse.ArgumentParser(description='Omarchy IDE Theme Generator')
    parser.add_argument('command', nargs='?', default='help',
                      choices=['generate', 'generate-all', 'status', 'help'],
                      help='Command to run')
    parser.add_argument('theme_name', nargs='?', help='Theme name for generate command')
    parser.add_argument('--themes-dir', type=str, help='Custom themes directory')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        if not args.theme_name:
            print("Error: Theme name required for generate command")
            themes_dir = Path(args.themes_dir) if args.themes_dir else Path.home() / '.config' / 'omarchy' / 'themes'
            if themes_dir.exists():
                print("Available themes:")
                for theme_dir in themes_dir.iterdir():
                    if theme_dir.is_dir() and (theme_dir / "alacritty.toml").exists():
                        print(f"  - {theme_dir.name}")
            sys.exit(1)
        
        success = generate_theme_for_name(args.theme_name, args.themes_dir)
        sys.exit(0 if success else 1)
    
    elif args.command == 'generate-all':
        success = generate_all_themes(args.themes_dir)
        sys.exit(0 if success else 1)
    
    elif args.command == 'status':
        check_theme_status(args.themes_dir)
    
    else:  # help
        print("Omarchy IDE Theme Generator")
        print("\nUsage:")
        print("  theme_generator.py generate <theme-name>")
        print("  theme_generator.py generate-all")
        print("  theme_generator.py status")
        print("\nOptions:")
        print("  --themes-dir <path>    Custom themes directory path")
        
        themes_dir = Path(args.themes_dir) if args.themes_dir else Path.home() / '.config' / 'omarchy' / 'themes'
        if themes_dir.exists():
            print("\nAvailable themes:")
            for theme_dir in themes_dir.iterdir():
                if theme_dir.is_dir() and (theme_dir / "alacritty.toml").exists():
                    print(f"  - {theme_dir.name}")

if __name__ == "__main__":
    main()