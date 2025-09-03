# Omarchy IDE Theme Sync

I've been having a lot of fun with Omarchy after installing it a day or two ago. I really appreciated how the system keeps the Neovim theme in sync. I don’t use Neovim (yet), but I really wanted that same “your editor just follows your system theme” magic in VS Code and Cursor. So I hacked this together.

This is a best‑effort tool. Some themes convert beautifully, others need a nudge. The goal is to get you most of the way there so you can tweak the last 10% to your exact taste.

## See it in action

[Leaving Windows, finding Omarchy, and dressing my OS](https://www.keyrxng.xyz/writing/omarchy-ide-theme-sync)


- Clone the repo. Run the install script. Change theme using the Omarchy default cmd.


https://github.com/user-attachments/assets/32ebf929-2be1-46e7-acae-6a90c202f9d1



- Install a new theme through Omarchy theme installer and both IDEs update automagically.



https://github.com/user-attachments/assets/9d36c793-998e-427c-a439-1f3efeca3e8d


- Apply theme changes to both IDEs without affecting the system theme.


https://github.com/user-attachments/assets/f686042f-9226-4643-81a9-9047528f0214

## What this does

- Generates VS Code/Cursor themes from your Omarchy theme colors
- Hooks into Omarchy’s theme switch so editors follow along automatically
- Writes a single theme JSON per theme: `[theme-name]-theme-sync.json`

## Quick start

Prereqs:
- Omarchy installed and working
- Python 3
- Optional: VS Code and/or Cursor in your PATH

Install:
```bash
./install.sh
```

Use it:
```bash
omarchy-theme-set nord         # Editors pick up Nord automatically
omarchy-theme-set tokyo-night  # And switch when you do
```

Handy commands:
```bash
omarchy-theme-sync status            # See which themes are ready
omarchy-theme-sync generate <name>   # Generate for one theme
omarchy-theme-sync generate-all      # Generate for everything
omarchy-theme-sync apply [name]      # Apply to editors now
```

## A couple of caveats

- Best effort: some themes won’t map 1:1 to editor UI. That’s okay — it’s meant to get you close, not perfect.
- Your editor settings: applying a theme currently writes to `~/.config/Code/User/settings.json` and `~/.config/Cursor/User/settings.json`. Back those up if you have handcrafted settings.


## How it works (under the hood)

1. When you switch themes in Omarchy, a hook runs.
2. It reads colors from the theme’s `alacritty.toml`.
3. A generator builds `[theme-name]-theme-sync.json` inside that theme’s folder.
4. The sync script applies it to VS Code and/or Cursor if they’re installed.

Generated file lives at:
```
~/.config/omarchy/themes/<theme>/<theme>-theme-sync.json
```

## Uninstall

```bash
./uninstall.sh
```

That will remove the integration and CLI. It’ll also offer to clean up generated editor theme files. Your original Omarchy behavior is restored.

## Project layout (for the curious)

```
omarchy-ide-theme-sync/
├── src/
│   ├── theme_generator.py  # builds the JSON themes
│   ├── theme_sync.py                      # applies them to editors
│   └── integration_hooks.py               # wires into Omarchy
├── hooks/
│   ├── post-theme-install.sh              # runs after installing a theme
│   └── post-theme-switch.sh               # runs on theme switch
├── install.sh
└── uninstall.sh
```

If you spot something off or have a better way, I’m all ears. PRs, issues, or quick notes are welcome.
