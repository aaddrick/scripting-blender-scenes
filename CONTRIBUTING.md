# Contributing

Corrections, new pitfalls, and new checks are welcome.

## Fix or add a rule

The skill lives in `skills/scripting-blender-scenes/`. `SKILL.md` is the entry point and routes to one topic file per kind of work (`rigging.md`, `contact.md`, and so on). Put a new rule in the topic file an agent would already be reading when it hits the problem, not in `SKILL.md`.

A good rule comes from a failure you saw:

- what the agent did and what went wrong in the built scene,
- the check that would have caught it, ideally one you saw fail on the planted defect and pass on the fix (`trusting-checks.md` explains why that matters),
- the Blender version, if the behaviour is version-specific.

For a Blender error, add it to `bpy-pitfalls.md` under the matching section, with the exact error text so an agent can search for it.

Keep `SKILL.md` short. Every harness loads its description at the start of each session, and the frontmatter must stay under 1024 characters.

## Change a manifest

Each harness reads its own file. Every manifest must carry the same name and version:

| Harness | Files |
|---|---|
| Claude Code, Claude Desktop, Cowork, claude.ai | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` |
| Codex | `.codex-plugin/plugin.json` (marketplace from `.claude-plugin/`) |
| Antigravity CLI, and the plugin manifest Copilot CLI and Grok read | `plugin.json` |
| Cursor | `.cursor-plugin/plugin.json`, `.cursor-plugin/marketplace.json` |
| Devin CLI | `.devin-plugin/plugin.json` |
| Factory Droid | reads `.claude-plugin/` |
| Gemini CLI | `gemini-extension.json` |
| GitHub Copilot CLI | `.github/plugin/marketplace.json` |
| Grok Build CLI | `.grok-plugin/marketplace.json` |
| Hermes Agent | `.hermes-plugin/` |
| Kimi Code | `.kimi-plugin/plugin.json` |
| Muse Code | `.muse-plugin/plugin.json` |
| Muse (muse.ai) | `scripts/install_muse.sh` |
| OpenCode | `.opencode/INSTALL.md` (no manifest; OpenCode finds the skill folder) |
| Pi | `package.json` (`pi` key) |

To release a new version, bump `version` in every file above. `scripts/check_configs.py` fails if any of them disagree.

Some harnesses read files meant for others. Copilot and Grok take the root `plugin.json` ahead of `.claude-plugin/plugin.json`. Hermes scans the whole repository before it installs. If you add a file for one harness, run the plugin-load workflow so every other harness gets checked too.

## Before you open a pull request

```bash
python3 scripts/check_configs.py
python3 -m unittest discover -s tests -v
```

The `plugin loads` workflow installs the plugin into a scratch config for each harness and checks that it finds the skill. It runs on pull requests that touch a manifest or the skill.

## Social preview

`scripts/make_card.py` renders `.github/assets/social-preview.png` in headless Blender and sets the type with Pillow. GitHub reads the preview only from **Settings > General > Social preview**, so upload the new PNG there by hand after you regenerate it.
