---
name: fusion-conception-imprimable
description: Design parts in Fusion 360 through the local `fusion` MCP (`mcp__fusion__*` tools) with FDM 3D printing in mind from the start — printable parts, print-in-place where possible, with as few supports as possible. Use this skill as soon as the user asks to model, modify or export a part in Fusion 360 (or "Fusion"), even if they do not mention printing: the skill assumes that their Fusion parts are meant to be printed.
---

# Fusion 360 design for FDM printing

This skill assumes that the user prints their parts in FDM (most often PLA). A part is only a success if it comes off the printer with no support, or almost none, and with no rework. So think about the print orientation **before** you draw, and review every hole, every overhang and every hardware pocket with that orientation in mind.

> Draft: this skill starts with rules noted over the course of projects. Add here every new rule the user gives.

## 1. Choose the orientation first

- Layers resist tension between them poorly: orient the part so that the main loads (leverage, bending) stay in the plane of the layers.
- Look for the orientation that gives the most flat faces on the build plate and the fewest overhangs.
- Note the chosen orientation (which face is on the build plate, which direction is "up"): all the rules below depend on it.

## 2. Remove supports

- **Overhangs**: beyond 45° from vertical, replace with a 45° chamfer rather than a fillet or a flat face.
- **Horizontal holes (axis parallel to the build plate): teardrop profile.** Add above the circle a triangle whose two sides are tangent to the circle and form 90° between them (45° on each side of vertical). The tip sits a little above the circle (at r·√2 from the centre). Extrude this profile through the full depth of the hole. The hole then prints without support. Point the tip towards the top **of the print**, not towards the top of the model.
- **Large horizontal openings** (cut-outs, windows, pockets): same idea, a pointed 45° roof (hexagon, octagon with a short flat of less than 10–15 mm, diamond).
- **Bridges**: a short horizontal ceiling (≲ 10–15 mm) is fine; beyond that, use a 45° roof.
- **Counterbore facing the build plate**: successive bridges (one layer as a slot, then one perpendicular layer as a square) at the bottom of the counterbore, or a 0.2 mm sacrificial membrane to pierce.
- **Elephant's foot**: a 0.4 to 0.6 mm chamfer on the edges resting on the build plate whenever a dimension or an assembly matters.
- If a support cannot be avoided (e.g. a shouldered dovetail), limit it to a small area resting on the build plate and tell the user.

The full catalogue (walls, clearances, nuts, clips, text, threads, assemblies) is in `references/techniques-fdm.md`: read it before drawing a mechanical part, and reread the relevant section whenever a detail calls for it.

## 3. Print-in-place

- When parts must move together (hinge, pivot, slide), first try to print them assembled.
- Keep a clearance between moving parts (0.3 to 0.5 mm in XY, at least two layers in Z, as a parameter) and avoid facing surfaces that lie horizontally one on top of the other (they fuse): offset them or replace them with 45° cones.
- Horizontal hinge pins as a teardrop or a diamond; chamfer at the bottom of moving parts.
- Starting fit clearances: tight 0.15, close 0.2, sliding 0.3, loose 0.4 mm; calibrate on the printer when the fit matters.

## 4. Hardware

- **Brass heat-set inserts**: hole at the diameter recommended by the manufacturer (parameter), depth = insert length + 0.5 mm, and **a small lead-in chamfer** (0.5 to 0.8 mm, less than 1 mm) to centre the insert before heating it. The insert hole also follows the teardrop rule if it is horizontal.
- Clearance holes: standard clearance (M3 → 3.4; M4 → 4.5; M5 → 5.5).
- Captive nuts: hexagon with 0.2–0.3 mm of clearance across flats, preferably as a side slot to avoid bridges.
- Countersinks: facing the top of the print, nothing to do; facing the build plate, the ceiling is a 45° cone that prints without support. Counterbores facing the build plate: successive bridges.
- Walls in multiples of the line width (≈ 0.45 mm), 1.2 mm minimum; strength comes from the walls more than from the infill.
- Always list the hardware needed (inserts, screws, lengths).

## 5. Parametric modelling

- All adjustable dimensions go in the **"Paramètres utilisateur" (User Parameters)**, with a short name and a comment (role). Separate input parameters from computed parameters.
- Fully constrained sketches; dimensions driven by the parameters (`dim.parameter.expression = 'nom'`).
- After building, change a few parameters to check that the timeline recomputes without error, then restore the values.

## 6. Fusion API pitfalls (through the MCP)

- The script runs in a single transaction: one exception cancels the whole script. Split into several calls and check volume / bounding box after each step.
- `importToTarget` of a STEP can fail in a blank document: use `importToNewDocument`, then copy the bodies with `TemporaryBRepManager.copy` into a `baseFeature`.
- Extrusion draft (`taperAngle`): the sign depends on the direction; check the bounding box right after.
- `addTwoPointRectangle` does not always add the horizontal/vertical constraints: add them by hand.
- `addScribedPolygon` creates a free centre point: add a coincidence with the origin and a horizontal constraint on one side.
- A large chamfer on a concave edge often fails: draw the wanted shape in the sketch instead.
- Distance dimensions are always positive: place the geometry on the correct side before dimensioning, and write the expressions so that they stay positive.

## 7. Check and deliver

- Interference and clearance check against the reference parts (temporary booleans, `measureMinimumDistance`).
- Estimated mass (PLA 1.24 g/cm³) solid and with a realistic infill.
- One screenshot at a time, at half resolution.
- Save in Fusion; export STEP + 3MF to the folder the user approves.
- **Export each part already in its print orientation**: face resting on the build plate at z = 0, part centred on the origin in x and y, top of the print towards +z. When imported into the slicer, the part is directly flat and support-free, with nothing to rotate. The Fusion model stays in the assembly coordinate system: copy the body (`TemporaryBRepManager.copy`), apply the rotation and the translation, export this copy (visible temporary component), then delete it. Check by reimporting: identical volume, `minPoint.z = 0`, build plate face at the bottom. Test parts: same orientation as their original part.
- After each export, check that the file contains a solid (STEP: `MANIFOLD_SOLID_BREP`): Fusion does not export hidden geometry and then writes an empty file, with no error.
- Give: parameters and role, print orientation, settings (walls, infill), any supports, hardware.
