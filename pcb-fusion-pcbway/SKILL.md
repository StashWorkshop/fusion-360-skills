---
name: pcb-fusion-pcbway
description: Design, check and prepare for ordering a printed circuit board in Fusion 360 (Electronics) for PCBWay, driving Fusion through the local `fusion` MCP (`mcp__fusion__*` tools). Use this skill as soon as the user talks about a PCB, a circuit board, a schematic or routing in Fusion (or "Fusion 360", "EAGLE"), Gerber files, manufacturing files, DRC/ERC, or ordering a board from PCBWay (or JLCPCB, same logic), even if they name neither PCBWay nor the skill. It avoids costly mistakes (clearance, polarity, export of an unrouted version) and makes the checks fast.
---

# PCB in Fusion 360 for PCBWay

A board ordered with a defect costs a week and a shipment. This skill gathers
the rules that avoid these defects, the efficient use of the Fusion MCP, and an
automatic check of the files actually sent to the manufacturer.

**Principle:** the Fusion checks (ERC, DRC) are not enough, because they apply to the
document, not to what PCBWay receives. Nothing is sent without the verdict of
`scripts/check_gerbers.py` on the exported Gerber files.

## References to read at the right time

- `references/fusion-mcp.md`: MCP recipes (import, routing, DRC, netlist
  extraction, saving, export) and Fusion pitfalls. **Read it before the first
  `mcp__fusion__*` call**; it avoids costly back-and-forth.
- `references/pcbway.md`: PCBWay capabilities, design rules block to embed in
  the board, silkscreen, drill holes, order settings. Read it before setting the
  rules or preparing the order.

## Workflow

1. **Validated netlist first.** A board is drawn from a tested pinout (on a
   breadboard if possible). Read the actual silkscreen of the modules received: the
   pin order of a module or a display varies from one seller to another. Cross-check
   each module pinout against an official source (the manufacturer's board file) rather
   than a seller's drawing.
2. **Rules before routing.** Embed the PCBWay rules in the board (`<designrules>`
   block, see `references/pcbway.md`) before starting the autorouter:
   the autorouter and the DRC both apply them. Target clearance: **0.3 mm**,
   not the 0.15 mm minimum. That minimum can be manufactured, but it bridges during
   hand soldering.
3. **Placement designed for assembly.** Connectors at the edge, facing outwards,
   with the wire entry side marked on the silkscreen. Power on one side, signals
   on the other. Decoupling capacitor right next to its pin. Motor connector in
   the order of the driver outputs, for tracks with no crossing. Check the actual
   footprint of the 3D models: a footprint can be smaller than its component.
4. **Routing and Fusion checks.** Linked import of the schematic and the board, autorouter,
   then ERC ("le circuit imprimé et le schéma sont cohérents" (the board and the
   schematic are consistent), 0 errors) and DRC (0 errors, no unrouted connection). Check
   the width of the power tracks.
5. **Save, then export.** Fusion only exports the **last saved
   version**. Saving to the Fusion cloud is an action visible to
   the user: ask for their agreement and suggest a name. Only then, export
   Gerber and drill files.
6. **Check of the exported files.** Extract the pad netlist from Fusion,
   then run:
   ```
   python scripts/check_gerbers.py <GerberFiles folder> <.xln file> --pads <pads.json> --clearance 0.3
   ```
   Read the verdict:
   - **0, OK:** the board can be ordered.
   - **2, TO FIX:** clearance below the target. Fix, re-route, then start again at
     step 4.
   - **1, BLOCKING:** short circuit, open connection, clearance below 0.15 mm or
     silkscreen on a pad. Do not order.

   The script does not see pinout errors, only the difference between the files
   and the Fusion netlist. The pinout still has to be validated at step 1. It needs Pillow
   and numpy (`pip install pillow numpy`); if they are installed in the user site,
   run Python without `-I`.
7. **Independent review** for any first revision: give a fresh agent the
   spec, the netlist and the Gerber files, with the points of step 6 and the polarities. A
   fresh review found, on the original board, a reversed pinout that the
   author's tests reproduced.
8. **Paper test** before soldering: print a template of the drill holes at 100% and push
   the modules into it to check the spacings.

## Rules that have already cost a lot

- **Never tick "Oui" (Yes) on Fusion's question about the last saved version**
  if the routed board has not been saved: the export would go out without tracks.
- **Spacing between the rows of a module:** a caliper measurement between inner
  edges is corrected by the thickness of one pin (0.64 mm), then rounded to the
  2.54 mm pitch.
- **Polarities on the silkscreen:** capacitor "+" on the + side; cathode band of the
  diode; square pad on pin 1; pin names of each connector; insertion
  direction of the modules (USB, EN). A test must check it, not the eye.
- **Silkscreen text:** EAGLE draws by default at 8% of the height, which is a stroke
  that is too thin. Set the ratio to 18% or more, with a height of at least 1 mm (1.2 mm
  for labels).
- **Through-hole pads:** at least 1.6 mm for a 0.8 mm drill, otherwise they
  tear off during desoldering.
- **A logo as an image** is drawn as rectangles 0.1 mm high, with no strokes under
  0.15 mm, on an area with no pad. On the back side, it is drawn mirrored.
- **The routing exists only in Fusion and in the exported archive.** Keep the dated
  zip with the project.

## Report to the user

End with:
- a clear verdict, orderable or not;
- the evidence: ERC, DRC, output of `check_gerbers.py`, and size and layers of the board;
- the order settings;
- what was not checked, usually the actual pinout of the modules.

The order is placed by the user, never by the agent.
