#!/usr/bin/env python3
"""Draw the social preview card at .github/assets/social-preview.png (1280x640).

The card is the skill's argument in one picture: a crate the script says is
resting on the floor, with the corner that actually sinks through it lit red,
and the measurement that caught it.

Two stages. Blender renders the scene headless, then Pillow sets the type:

    python3 scripts/make_card.py

Needs Blender 4.2+ on PATH and Pillow. CI does not run this. GitHub reads the
social preview only from Settings > General > Social preview, so upload the
PNG there by hand after regenerating it.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".github" / "assets" / "social-preview.png"
W, H = 1280, 640
SINK = 0.09  # metres the lowest corner sits below the floor

SCENE = r'''
import bpy, bmesh, math, sys
from mathutils import Vector, Euler

out, W, H, SINK = sys.argv[-4], int(sys.argv[-3]), int(sys.argv[-2]), float(sys.argv[-1])
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

def mat(name, rgb, emit=0.0, alpha=1.0, rough=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    return m

# Floor: a thin slab, half see-through so the sunk corner shows under it.
bpy.ops.mesh.primitive_plane_add(size=40)
floor = bpy.context.object
floor.data.materials.append(mat("floor", (0.05, 0.055, 0.065), alpha=0.35, rough=0.35))

# Grid lines on the floor, 0.5 m apart.
grid = bpy.data.materials.new("grid")
grid.use_nodes = True
grid.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.16, 0.17, 0.2, 1)
for i in range(-20, 21):
    for axis in (0, 1):
        bpy.ops.mesh.primitive_cube_add(size=1)
        g = bpy.context.object
        g.scale = (40, 0.008, 0.001) if axis == 0 else (0.008, 40, 0.001)
        g.location = (0, i * 0.5, 0.0006) if axis == 0 else (i * 0.5, 0, 0.0006)
        g.data.materials.append(grid)

# Crate: tilted so one corner dips SINK below the floor.
bpy.ops.mesh.primitive_cube_add(size=1)
crate = bpy.context.object
crate.rotation_euler = Euler((math.radians(10), math.radians(-12), math.radians(28)))
bpy.ops.object.transform_apply(rotation=True)
bpy.ops.object.modifier_add(type="BEVEL")
crate.modifiers["Bevel"].width = 0.03
crate.modifiers["Bevel"].segments = 3
low = min(v.co.z for v in crate.data.vertices)
crate.location = (0.15, 0, -low - SINK)
crate.data.materials.append(mat("crate", (0.95, 0.40, 0.02), rough=0.45))

# The part below the floor, lit red: crate intersected with a box under z=0.
bpy.ops.object.duplicate()
cut = bpy.context.object
cut.modifiers.clear()
cut.data.materials.clear()
cut.data.materials.append(mat("clip", (1.0, 0.08, 0.06), emit=25.0))
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.5))
below = bpy.context.object
below.scale = (10, 10, 1)
mod = cut.modifiers.new("below", "BOOLEAN")
mod.operation = "INTERSECT"
mod.object = below
bpy.context.view_layer.objects.active = cut
bpy.ops.object.modifier_apply(modifier="below")
bpy.data.objects.remove(below)
cut.scale = (1.002, 1.002, 1.002)

# Measure it, so the card cannot claim a depth the scene does not have.
dg = bpy.context.evaluated_depsgraph_get()
ev = crate.evaluated_get(dg)
depth = -min((ev.matrix_world @ v.co).z for v in ev.data.vertices)
print(f"MEASURED_SINK_MM={depth * 1000:.1f}")

# Camera: low three-quarter view, crate on the right third.
bpy.ops.object.camera_add(location=(-2.2, -5.2, 0.55))
cam = bpy.context.object
cam.data.lens = 50
cam.data.shift_x = -0.2
direction = Vector((0.15, 0, 0.3)) - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
scene.camera = cam

# Light: one key, one cool rim, dark world.
bpy.ops.object.light_add(type="AREA", location=(-2.5, -2.5, 4))
key = bpy.context.object
key.data.energy, key.data.size = 900, 3
key.rotation_euler = (Vector((0, 0, 0)) - key.location).to_track_quat("-Z", "Y").to_euler()
bpy.ops.object.light_add(type="AREA", location=(3, 3, 2))
rim = bpy.context.object
rim.data.energy, rim.data.size, rim.data.color = 500, 2, (0.6, 0.75, 1.0)
rim.rotation_euler = (Vector((0, 0, 0.3)) - rim.location).to_track_quat("-Z", "Y").to_euler()
world = bpy.data.worlds.new("w")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.013, 0.017, 1)
scene.world = world

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 96
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Punchy"
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
'''


def render(path: Path) -> float:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(SCENE)
    run = subprocess.run(
        ["blender", "--background", "--factory-startup", "--python", f.name,
         "--", str(path), str(W), str(H), str(SINK)],
        capture_output=True, text=True,
    )
    for line in run.stdout.splitlines():
        if line.startswith("MEASURED_SINK_MM="):
            return float(line.split("=")[1])
    sys.exit(f"render failed:\n{run.stdout[-2000:]}\n{run.stderr[-2000:]}")


def font(names: list[str], size: int):
    from PIL import ImageFont
    import subprocess as sp
    for name in names:
        hit = sp.run(["fc-match", "-f", "%{file}", name], capture_output=True, text=True).stdout
        if hit:
            return ImageFont.truetype(hit, size)
    return ImageFont.load_default(size)


def compose(raw: Path, sink_mm: float) -> None:
    from PIL import Image, ImageDraw
    img = Image.open(raw).convert("RGB")
    # Darken the left side so the type reads over the grid.
    shade = Image.linear_gradient("L").rotate(90).resize((W, H))
    shade = shade.point(lambda v: int(v * 0.85))
    img = Image.composite(img, Image.new("RGB", (W, H), (8, 9, 12)), shade)
    d = ImageDraw.Draw(img)
    sans_b = font(["Inter:bold", "DejaVu Sans:bold"], 64)
    sans = font(["Inter", "DejaVu Sans"], 27)
    mono = font(["IBM Plex Mono:medium", "DejaVu Sans Mono"], 22)
    x = 72
    d.text((x, 150), "Scripting", font=sans_b, fill=(240, 240, 242))
    d.text((x, 222), "Blender Scenes", font=sans_b, fill=(232, 125, 13))
    d.text((x, 318), "A skill for coding agents that build", font=sans, fill=(190, 193, 200))
    d.text((x, 354), "Blender scenes they can't see.", font=sans, fill=(190, 193, 200))
    d.text((x, 440), "script:   crate rests on floor   PASS", font=mono, fill=(130, 135, 145))
    d.text((x, 474), f"measured: corner {sink_mm:.0f} mm below    FAIL", font=mono, fill=(255, 92, 80))
    d.text((x, 560), "Claude Code · Codex · Cursor · Gemini · Copilot · +12 more", font=font(["Inter", "DejaVu Sans"], 18), fill=(110, 114, 124))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "raw.png"
        sink_mm = render(raw)
        compose(raw, sink_mm)
    print(f"wrote {OUT.relative_to(ROOT)} (measured sink {sink_mm:.1f} mm)")
