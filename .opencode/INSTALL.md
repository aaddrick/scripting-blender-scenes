# Installing scripting-blender-scenes for OpenCode

This repository ships one skill. OpenCode finds skills on its own in
`~/.config/opencode/skills/<name>/SKILL.md`, so no plugin or config entry is needed.

## Install

Clone the repository and link the skill folder into OpenCode's global skills directory:

```bash
git clone https://github.com/aaddrick/scripting-blender-scenes.git ~/.local/share/scripting-blender-scenes
mkdir -p ~/.config/opencode/skills
ln -s ~/.local/share/scripting-blender-scenes/skills/scripting-blender-scenes ~/.config/opencode/skills/scripting-blender-scenes
```

On Windows, or anywhere symlinks are awkward, copy the folder instead of linking it:

```bash
cp -r ~/.local/share/scripting-blender-scenes/skills/scripting-blender-scenes ~/.config/opencode/skills/
```

To install for one project only, put the folder in that project's `.opencode/skills/` instead.

## Check it installed

```bash
opencode debug skill | grep '"name": "scripting-blender-scenes"'
```

Restart OpenCode. It loads the skill when the task matches. To load it by hand, ask:

```
use the skill tool to load scripting-blender-scenes
```

The skill links to sibling topic files (`checks.md`, `rigging.md`, and so on). OpenCode tells the
agent the skill's base directory when it loads, so the agent reads them from there.

## Update

```bash
git -C ~/.local/share/scripting-blender-scenes pull
```

If you copied the folder, copy it again after pulling.

## Uninstall

Delete the `scripting-blender-scenes` link (or copied folder) from `~/.config/opencode/skills/`,
then delete the clone at `~/.local/share/scripting-blender-scenes`.
