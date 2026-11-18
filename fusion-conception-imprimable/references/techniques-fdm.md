# Design techniques for FDM printing

Catalogue of the rules to apply while modelling. Starting values for a 0.4 mm nozzle, 0.2 mm layers and PLA; PETG generally needs a little more clearance. Clearances depend on the printer: when a fit matters, plan a test part (clearance comb) or put the value in a parameter.

## Contents
1. Orientation and strength
2. Overhangs and chamfers
3. Horizontal holes
4. Bridges and sacrificial layers
5. Vertical holes and accuracy
6. First layer (elephant's foot)
7. Walls, ribs, corners
8. Clearances and fits
9. Hardware: inserts, nuts, screws
10. Print-in-place (hinges, pivots)
11. Clips and flexible parts
12. Text and markings
13. Printed threads
14. Supports when they cannot be avoided
15. Large parts and assemblies

## 1. Orientation and strength
- An FDM part is anisotropic: the bond between layers is 2 to 4 times weaker than the filament in the plane. Tension and bending loads must run in the plane of the layers.
- Choose the orientation before drawing, then draw every detail for that orientation ("the top" of the print is not necessarily the top of the model).
- A large flat face on the build plate = good adhesion and no support.
- Accurate cylinders (shafts, bores) print better with a vertical axis: a clean circle in each layer.

## 2. Overhangs and chamfers
- The 45° rule: a face that leans more than 45° from vertical prints badly without support. Between 45° and 60°, it often works in PLA with good cooling, but the surface finish gets worse.
- Under an overhang, use a **45° chamfer**, not a fillet: the bottom of a fillet is horizontal and collapses.
- Fillets: on vertical edges and in the plane of the layers (they strengthen and cause no problem). Chamfers: on the edges at the bottom of the part and under protrusions.
- A protrusion (rim, lip, hook) can almost always become a gusset or a 45° chamfer underneath.

## 3. Horizontal holes (axis parallel to the build plate)
- **Teardrop**: add above the circle a triangle whose sides are tangent to the circle and form 90° between them; the tip is at r·√2 from the centre. Tip towards the top of the print. For an accurate dimension at the top of the hole, truncate the tip with a flat (0.3–0.5 × r above the circle): a small bridge, but the hole keeps its functional diameter.
- **Diamond**: for large non-functional openings, a square rotated by 45°.
- Large openings (windows, pockets): a pointed 45° roof, hexagon or octagon with a short flat.
- A small horizontal hole (≤ 5–6 mm) often prints without a teardrop, but comes out oval at the top: the teardrop keeps it round on its lower part.

## 4. Bridges and sacrificial layers
- A bridge (horizontal ceiling held at both ends) prints well up to 10–15 mm in PLA, sometimes 20–30 mm with good cooling, but the underside stays less clean. Beyond that, use a 45° roof or break the bridge with a support point.
- **Counterbore facing the build plate** (screw head under the part): the clearance hole opens in the middle of the counterbore ceiling, with nothing to rest on. The "successive bridges" solution: at the bottom of the counterbore, a first bridged layer (0.2 mm) that reduces the opening to a slot as wide as the hole, then a second, perpendicular bridged layer that reduces it to the square of the hole. The round hole resumes above.
- **Sacrificial membrane**: a hole that must open above a void can be closed by a 0.2 mm layer, pierced by hand afterwards. Also useful to print a screw hole on top of a nut pocket.

## 5. Vertical holes and accuracy
- Holes come out smaller than drawn (0.1 to 0.3 mm on the diameter depending on size and profile) and outer cylinders a little larger.
- For an accurate fit: put the diameter in a parameter, print a test, or ream with a drill bit afterwards.
- Small, very accurate holes can be drawn as a polygon (polyhole): a circumscribed hexagon or octagon compensates for the undersize of circles.

## 6. First layer (elephant's foot)
- The squashed first layer spreads out by 0.2 to 0.5 mm. Put a 0.4 to 0.6 mm chamfer (45°) on all edges in contact with the build plate when a dimension or an assembly matters.
- In print-in-place, this is the first cause of parts fused at build plate level: also chamfer the bottom of moving parts.

## 7. Walls, ribs, corners
- Thicknesses in multiples of the line width (≈ 0.45 mm): 0.9 / 1.2 / 1.6 / 2 mm. Minimum 1.2 mm for a load-bearing wall.
- Strength comes mostly from the walls (perimeters): for a mechanical part, 4 walls and 30–40% infill are better than 100% infill with 2 walls.
- Ribs rather than solid mass; rib thickness ≈ 0.6 to 1 × the wall that carries it.
- Inside corners: fillet (radius ≥ thickness/2) in the plane of the layers to avoid stress concentration.
- Avoid isolated thin, tall parts (> 8–10 × their thickness): they vibrate during printing; add a stiffener or change the orientation.

## 8. Clearances and fits (starting points, to calibrate)
| Use | Clearance (per side) |
|---|---|
| Tight / press fit | 0.10–0.15 mm |
| Close, no play | 0.20 mm |
| Sliding | 0.25–0.30 mm |
| Loose | 0.40 mm |
| Print-in-place (moving part printed assembled) | 0.30–0.50 mm in XY, at least 2 layers (0.4 mm) in Z |

- The clearance between vertical surfaces (in XY) is more reliable than between horizontal surfaces (in Z): plan more clearance in Z.
- A clearance perpendicular to a flank inclined at angle a is obtained with a horizontal offset of clearance / cos(a).

## 9. Hardware: inserts, nuts, screws
- **Brass heat-set inserts**: hole at the manufacturer's diameter (parameter), depth = length + 0.5 to 1 mm (the molten material needs room), a 0.5 to 0.8 mm lead-in chamfer to centre the insert, at least 1.5–2 mm of material around it. Set with the iron at 220–230 °C (PLA), insert well perpendicular.
- **Captive nuts**: hexagonal pocket with 0.2–0.3 mm of clearance across flats; if the pocket is horizontal, think of the sacrificial membrane or the 45° roof. A side-slot pocket (nut slid in from the side) avoids bridges.
- **Screws directly into plastic**: pilot hole ≈ 0.8–0.85 × the nominal diameter for self-tapping screws, good depth and a thick wall around it.
- Screw clearance holes: M3 → 3.4; M4 → 4.5; M5 → 5.5; M6 → 6.5 mm.
- Countersunk heads: a countersink (90° cone) prints without support in both directions; facing the build plate, its ceiling is a 45° overhang, at the limit but acceptable. A counterbore (flat bottom) facing the build plate needs successive bridges.

## 10. Print-in-place (hinges, pivots)
- Horizontal hinge pin: pin and bore with a teardrop or diamond profile so that nothing hangs; clearance 0.3–0.5 mm.
- Conical stops at 45° rather than flat faces facing each other: a cone prints without support and separates easily.
- No moving surface may rest flat on another during printing: leave at least 0.3–0.4 mm (2 layers) between them in Z.
- Chamfer at the bottom of moving parts (elephant's foot).
- Plan a way to "break free" the part after printing (turn, pull): the first movement breaks the small bridges.

## 11. Clips and flexible parts
- The part that flexes must flex in the plane of the layers (otherwise it breaks between two layers).
- Long, tapered clip arm; low allowable strain in PLA (~1–2%): prefer PETG for clips that are used often.
- Fillet at the base of the arm.

## 12. Text and markings
- Raised or recessed by ≥ 0.6 mm (3 layers), stroke ≥ 0.8 mm (2 lines), sans-serif and fairly bold font.
- Text prints better on a horizontal top face or a vertical face; recessed on a vertical face, it gives small bridges.

## 13. Printed threads
- Modelled threads: reliable from about M8–M10, vertical axis, with a little radial clearance (0.2–0.3 mm). 45° profiles (ISO 60°, trapezoidal) printable without support.
- Below that: brass insert, captive nut or tapping in a pilot hole.

## 14. Supports when they cannot be avoided
- Limit them to a small accessible area, resting on the build plate (not on the part).
- Supports built into the model: thin ribs separated from the part by a 0.2 mm clearance (one layer), easy to break off.
- Tell the user, with the location and the setting ("supports on build plate only", support blocker, support enforcer).

## 15. Large parts and assemblies
- If a part is larger than the build plate or piles up overhangs, cut it into elements that print flat and plan the assembly: dovetails, pins (hole + rod with clearance), screws + inserts.
- Cutting plane far from highly loaded areas, or an overlap to carry the load.

## Sources consulted
- Hubs, "How to design parts for FDM 3D printing" (chamfers on the edges at the build plate).
- FacFox, "FDM 3D Printing Design Tips" (elephant's foot).
- Sovol, "Print-in-Place 3D Printing" (clearances, elephant's foot in print-in-place).
- Wevolver, "FDM 3D printing design tips"; EduHK (bridge lengths).
- Chief Delphi, "Prepare to Print FeatureScript" (teardrops, bridged counterbores).
- Community skills: andreahaku/openscad_claude_skill (1.2 mm walls, clearances press 0.15 / close 0.25 / slide 0.30 / loose 0.40, overhangs < 45°), flowful-ai/cad-skill (design review).
