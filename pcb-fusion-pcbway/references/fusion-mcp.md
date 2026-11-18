# Fusion Electronics through the MCP: recipes and pitfalls

All recipes go through `mcp__fusion__fusion_mcp_execute` with `featureType: "script"`,
a Python script that defines `run(_context)`. Electronics commands go through
`app.executeTextCommand(...)`.

## Pitfall No. 1: the "Sélectionner" (Select) command blocks scripts

In an electronics document, Fusion almost always leaves the "Sélectionner" (Select) command
(`Electron::Group`) open. A script that modifies the document then fails with
"Cannot perform 'script' while a command dialog is open".

- **Read only:** pass `readOnly: true`. It works even with the command open,
  but without `executeTextCommand`.
- **Write:** bring Fusion to the foreground, then send Escape twice through
  desktop control (access to request for `fusion360.exe`). On Windows:
  ```powershell
  Add-Type -Name W -Namespace U -MemberDefinition '[DllImport("user32.dll")] public static extern bool ShowWindow(System.IntPtr h,int c); [DllImport("user32.dll")] public static extern bool SetForegroundWindow(System.IntPtr h);'
  $p = Get-Process Fusion360 | ? { $_.MainWindowHandle -ne 0 } | select -First 1
  [U.W]::ShowWindow($p.MainWindowHandle,6); sleep -m 400; [U.W]::ShowWindow($p.MainWindowHandle,3); [U.W]::SetForegroundWindow($p.MainWindowHandle)
  ```
  Then click in the Fusion command line, and send `escape` twice.
  If Fusion has been updated, the path of the executable changes: request access again.
- **Grouping:** chain several commands in the same script, only once
  after Escape.

## Import a linked schematic and board

```python
app.executeTextCommand('Electron.importSchAndBrd "C:\\...\\carte.sch" "C:\\...\\carte.brd"')
```

This command creates an electronics project with its three tabs: project, schematic and
board. The schematic and the board are **linked** in it, and the ERC confirms it. Opening the `.sch` and
the `.brd` separately gives two unlinked documents. Each import adds
"Sans nom" (Untitled) tabs: tell the user which ones to close.

## Route and check in one call

```python
app.executeTextCommand('Electron.run "RATSNEST; AUTO ! GND ; RATSNEST; DRC ;"')
```

- `AUTO ! GND` routes everything except ground, which the polygon on the bottom side
  takes care of.
- The call often exceeds the MCP timeout ("timed out"), but it continues in Fusion.
  Wait about 20 s, then check the result.
- Track widths come from the net classes. The clearance comes from the
  `<designrules>` block of the board.

## Read the errors without a screenshot

- **DRC errors:** `fusion_mcp_electronics_read` with `entity_type: "electronics.Error"`
  and `fields: ["description"]`. An empty list means no error. The
  "Angle aigu" warnings come from the autorouter and have no effect in
  industrial manufacturing.
- **Track widths:** `electronics.Wire`, fields `signal_object_id`, `width`, `layer`,
  cross-referenced with `electronics.Signal`. The units are inches: 0.03937 = 1.0 mm.
- **ERC:** activate the schematic document, then run `Electron.run "ERC ;"`. The API does not
  expose the result: zoom the screen on the Errors panel, which must show
  "le circuit imprimé et le schéma sont cohérents" (the board and the schematic are consistent).
- **Switch document:** `app.documents.item(i).activate()`. The type is read with
  `d.products.item(0).productType`: `EcadDesignProductType`, `SchematicProductType`,
  `BoardProductType`.

## Extract the pad netlist without passing it through the conversation

A raw `electronics.Pad` response weighs several thousand tokens. Instead, have Fusion
write it directly to a file. The JSON must be **in quotes, with
the inner quotes escaped**:

```python
import adsk.core, json, os
def run(_context: str):
    app = adsk.core.Application.get()
    q = {'entity_type': 'electronics.Pad', 'object': {'fields': ['x', 'y', 'signal'], 'pagination': {'limit': 1000}}}
    arg = json.dumps(q, separators=(',', ':')).replace('"', '\\"')
    out = os.path.join(os.environ['TEMP'], 'pads.json')
    open(out, 'w', encoding='utf-8').write(app.executeTextCommand('MCP.ElectronicsRead "' + arg + '"'))
```

This script runs with `readOnly: true`, with the board document active. The file
produced is the `--pads` input of `check_gerbers.py`. The coordinates are in inches,
and the script converts them.

## Save (with the user's agreement)

```python
ecad = [d for d in docs if d.products.item(0).productType == 'EcadDesignProductType'][-1]
project = next(p for p in (app.data.dataProjects.item(i) for i in range(app.data.dataProjects.count)) if p.name == 'Default Project')
ecad.saveAs('Nom de la carte r1', project.rootFolder, 'description', '')
```

`saveAs` creates a new file and never overwrites the old one. For each revision,
add a suffix (r2, r3…) and tell the user which version is out of date.
Avoid accents in the name.

## Export Gerber and drill files

You must first **save the board**. Otherwise, Fusion offers to export "la
dernière version enregistrée" (the last saved version), which may have no tracks: answer "Annuler" (Cancel).

- **By script** (board active, after Escape):
  ```python
  cam = r'<Fusion>\Applications\Electron\LibEagle\examples\cam\examples\example_2_layer.cam'
  app.executeTextCommand(f'Electron.mfgexport "{dossier}" "{cam}"')
  ```
  The files land in an unexpected path:
  `<parent of dossier>\example_2_layer\example_2_layer.gbr\<hub>\<project>\CAMOutputs\`.
  Look for `CAMOutputs` under the parent folder. The `<Fusion>` folder is the one from
  `(Get-Process Fusion360).Path`.
- **Through the interface:** open the FABRICATION tab, choose the "Exporter les sorties
  Gerber, de perçage NC…" icon, confirm with OK, then "Enregistrer" (Save). You get a complete zip,
  to send as is.
- The `example_2_layer.cam` template outputs the copper, the outline, the masks, the
  silkscreen of both sides and the drill file `drill_1_16.xln`. It does not separate
  plated holes from non-plated holes.

## Format pitfalls

- Fusion Gerber files are in `FSLAX34Y34` format, in mm: **4** implicit decimals.
- The Excellon drill file is in `METRIC,TZ,000.000` format: **3** implicit decimals.
  If you mix them up, the holes end up at a tenth of their position.
- A library such as pygerber does not read all Fusion files (the outline,
  in particular) and renders a logo made of rectangles as stripes. These are rendering
  artefacts, not defects: `check_gerbers.py`, for its part, measures.

## 3D models

The API cannot attach a 3D model to a footprint, nor create the linked 3D PCB
(`NuElectronCommands.ReferenceToPCBCmd` is not available from a script). For the
enclosure, build a separate assembly:
- a board extruded to 1.6 mm;
- the STEP models placed at the pad positions.

The KiCad STEP files are in `KiCad\<version>\share\kicad\3dmodels`: their
origin is pad 1, and z = 0 is the top of the board. The modules
(ESP32 boards, drivers) come from GrabCAD. The download requires an account:
the user does it.
